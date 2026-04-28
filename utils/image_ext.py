from __future__ import annotations


def get_image_ext_from_bytes(data: bytes) -> str:
    """根据图片二进制数据返回合适的扩展名（含点）。"""
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return ".gif"
    if data.startswith(b"BM"):
        return ".bmp"
    if data.startswith(b"RIFF") and b"WEBPVP8" in data[:12]:
        return ".webp"
    return ".png"
