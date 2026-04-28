from __future__ import annotations

import ipaddress
import logging
import ssl
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
import certifi

from .image_ext import get_image_ext_from_bytes

logger = logging.getLogger(__name__)


def _is_local_or_private_host(hostname: str) -> bool:
    if not hostname:
        return True

    lowered = hostname.lower()
    if lowered == "localhost":
        return True

    try:
        ip = ipaddress.ip_address(lowered)
    except ValueError:
        return False

    return (
        ip.is_loopback
        or ip.is_private
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _validate_download_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"不支持的 URL 协议：{parsed.scheme}")
    if not parsed.netloc:
        raise ValueError("下载 URL 必须包含主机名。")
    if parsed.username or parsed.password:
        raise ValueError("不允许在下载 URL 中包含凭证。")

    hostname = parsed.hostname
    if hostname is None or _is_local_or_private_host(hostname):
        raise ValueError("不允许下载本地或私有网络地址。")


DEFAULT_MAX_IMAGE_BYTES = 10 * 1024 * 1024


def _create_ssl_connector() -> aiohttp.TCPConnector:
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    return aiohttp.TCPConnector(ssl=ssl_context)


async def download_file_async(url: str, path: str, timeout: int = 15) -> None:
    """从指定 URL 下载文件到本地路径。"""
    _validate_download_url(url)

    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        async with aiohttp.ClientSession(
            trust_env=True,
            connector=_create_ssl_connector(),
        ) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                if resp.status != 200:
                    raise ValueError(f"下载文件失败: {resp.status}")

                with open(target_path, "wb") as f:
                    while True:
                        chunk = await resp.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
    except Exception:
        if target_path.exists():
            try:
                target_path.unlink()
            except Exception:
                pass
        raise


async def download_image_async(
    url: str,
    save_dir: str,
    base_name: str,
    max_attempts: int = 100,
    timeout: int = 15,
    max_size_bytes: int = DEFAULT_MAX_IMAGE_BYTES,
) -> str | None:
    """下载图片并根据内容自动识别扩展名，返回保存的文件名。

    如果图片超过 max_size_bytes，则拒绝下载。
    """
    _validate_download_url(url)

    save_dir_path = Path(save_dir)
    save_dir_path.mkdir(parents=True, exist_ok=True)

    try:
        async with aiohttp.ClientSession(
            trust_env=True,
            connector=_create_ssl_connector(),
        ) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                if resp.status != 200:
                    return None

                content_length = resp.headers.get("content-length")
                if content_length is not None:
                    try:
                        total_size = int(content_length)
                    except ValueError:
                        total_size = 0
                    if max_size_bytes and total_size > max_size_bytes:
                        logger.error(
                            f"下载失败: 文件大小 {total_size} 超过限制 {max_size_bytes}。"
                        )
                        return None

                img_data = bytearray()
                downloaded = 0
                while True:
                    chunk = await resp.content.read(8192)
                    if not chunk:
                        break
                    downloaded += len(chunk)
                    if max_size_bytes and downloaded > max_size_bytes:
                        logger.error(
                            f"下载失败: 文件大小已超过限制 {max_size_bytes}。"
                        )
                        return None
                    img_data.extend(chunk)
                img_data = bytes(img_data)
    except Exception as e:
        logger.error(f"下载失败: {e}")
        return None
    
    filename = f"{base_name}"
    file_path = save_dir_path / filename

    if file_path.exists():
        for i in range(1, max_attempts + 1):
            candidate = save_dir_path / f"{base_name}_{i}"
            if not candidate.exists():
                file_path = candidate
                filename = candidate.name
                break
        else:
            logger.error("无法保存文件，已存在过多同名文件")
            return None

    try:
        with open(file_path, "wb") as f:
            f.write(img_data)
    except Exception as e:
        logger.error(f"保存图片失败: {e}")
        return None 
        
    ext = get_image_ext_from_bytes(img_data)
    filename = f"{filename}{ext}"
    file_path = save_dir_path / filename

    try:
        with open(file_path, "wb") as f:
            f.write(img_data)
    except Exception as e:
        logger.error(f"保存图片失败: {e}")
        return None

    return filename
