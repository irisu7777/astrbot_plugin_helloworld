import asyncio
import os
import random
from pathlib import Path, PureWindowsPath

import aiohttp

import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star
from astrbot.core.utils.astrbot_path import get_astrbot_data_path


def get_image_ext_from_bytes(data: bytes) -> str:
    """根据二进制数据返回图片扩展名（包含点），未识别返回 '.png'"""
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    elif data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    elif data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return ".gif"
    elif data.startswith(b"BM"):
        return ".bmp"
    elif data.startswith(b"RIFF") and b"WEBPVP8" in data[:12]:
        return ".webp"
    else:
        return ".png"  # 回退为 png

INVALID_CHARS = set(r'<>:"/\\|?*')
MAX_WINDOWS_NAME_LENGTH = 255
MAX_WINDOWS_PATH_LENGTH = 260
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def _is_valid_windows_name(name: str) -> bool:
    if not name or name in {".", ".."}:
        return False

    if len(name) > MAX_WINDOWS_NAME_LENGTH:
        return False

    if any(ord(ch) < 32 for ch in name):
        return False

    if any(ch in INVALID_CHARS for ch in name):
        return False

    if name[-1] in {" ", "."}:
        return False

    stem = name.split(".", 1)[0].upper()
    if stem in WINDOWS_RESERVED_NAMES:
        return False

    return True


def is_valid_windows_filename(name: str) -> bool:
    if os.path.basename(name) != name:
        # reject paths like "foo/bar.txt" or "C:\foo.txt"
        return False

    return _is_valid_windows_name(name)


def is_safe_windows_relative_path(path: str) -> bool:
    # logger.info(f"{path} 是否是安全的 Windows 相对路径？")

    if not path:
        return True

    if len(path) > MAX_WINDOWS_PATH_LENGTH:
        return False

    pure_path = PureWindowsPath(path)
    if pure_path.is_absolute() or pure_path.drive or pure_path.root:
        return False

    for part in pure_path.parts:
        if part in {"", ".", ".."}:
            return False
        if len(part) > MAX_WINDOWS_NAME_LENGTH:
            return False
        if not _is_valid_windows_name(part):
            return False

    return True

class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig): # AstrBotConfig 继承自 Dict，拥有字典的所有方法
        super().__init__(context)
        self.config = config
        print(self.config)

        self.http = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=15),
            headers={"User-Agent": "AstrBot/1.0"}
        )

    async def download_image_async(self, url: str, save_path: str, base_name: str) -> str | None:
        """下载图片，根据内容自动识别扩展名并保存，返回最终文件名"""
        try:
            async with self.http.get(url) as resp:
                if resp.status != 200:
                    return None
                img_data = await resp.read()  # 全部读到内存
        except Exception as e:
            logger.error(f"下载失败: {e}")
            return None

        ext = get_image_ext_from_bytes(img_data)
        filename = f"{base_name}{ext}"
        new_save_path = os.path.join(save_path, filename)

        if os.path.exists(save_path):
            for i in range(1, 101): # 最多尝试 100 个备选文件名
                new_filename = f"{base_name}_{i}{ext}"
                new_save_path = os.path.join(save_path, new_filename)
                if not os.path.exists(new_save_path):
                    filename = new_filename
                    break
                elif i == 100:
                    logger.error("无法保存文件，已存在过多同名文件")
                    return None

        save_path = new_save_path

        with open(save_path, "wb") as f:
            f.write(img_data)

        return filename

    def is_user_accepted(self, event: AstrMessageEvent) -> int:
        """检查用户是否被允许使用插件，返回 0 表示允许，1 表示被禁止，2 表示不在允许列表中"""
        user_id = event.message_obj.sender.user_id

        blocked_users_enabled = self.config.get("blocked_users_enabled", False)
        blocked_users = self.config.get("blocked_users", [])
        if blocked_users_enabled and user_id in blocked_users:
            return 1

        allowed_users_enabled = self.config.get("allowed_users_enabled", False)
        allowed_users = self.config.get("allowed_users", [])
        if allowed_users_enabled and user_id not in allowed_users:
            return 2

        return 0

    @filter.command_group("savememe", alias={"sm"})
    @filter.event_message_type(filter.EventMessageType.PRIVATE_MESSAGE)
    def savememe(self):
        pass

    @savememe.command("help")
    async def help(self, event: AstrMessageEvent):
        acceptance = self.is_user_accepted(event)
        if acceptance == 1:
            await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
            yield event.plain_result("呜，是被主人放进黑名单的人……主人讨厌的家伙，人家也讨厌！")
            return
        elif acceptance == 2:
            await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
            yield event.plain_result("抱歉啦~♪ 只有在白名单的主人们才能使用该插件喵~♪")
            return
        else:
            await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
            yield event.plain_result("꧁༺【Help me, SAVEMEME!!】༻꧂\n\n❗请好好按照以下方法来玩弄女仆哦❗\n\n"
                                     "1. 引用想要保存的表情包，并发送 /savememe save <save_path> <image_name>\n\n"
                                     "- save_path（可选字符串参数，默认为空）。图片将被保存在插件数据目录下的 memes/save_path。\n\n"
                                     "- image_name（可选字符串参数，默认为空）。如果提供了 image_name，保存的图片将使用这个名字。"
                                     "否则，插件会使用图片的原始文件名作为保存名称。"
                                     "请注意，插件会根据图片内容自动识别扩展名，并将其添加到 image_name 后面，所以 image_name 不需要包含扩展名【划重点】。\n\n"
                                     "\n示例：\n引用一张图片，并发送 /savememe save cute_cat "
                                     "可将图片保存到插件数据目录下的 memes 文件夹中的 cute_cat 子文件夹中，名字为 cute_cat.<extension>\n\n"
                                     "【注意】如果 cute_cat 已经存在，插件会自动尝试 cute_cat_1、cute_cat_2 等名字，直到找到一个可用的名字或者放弃保存（如果同名文件多于100个）。"
                                     "\n\n"
                                     "2. ... （人家现在会的事情还很少，不过作为主人的女仆，人家迟早会做到完美潇洒的程度的。嗯哼~♪）")

    @savememe.command("save")
    async def save(self, event: AstrMessageEvent, save_path: str = "", image_name: str = ""):
        acceptance = self.is_user_accepted(event)
        if acceptance == 1:
            await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
            yield event.plain_result("呜，是被主人放进黑名单的人……主人讨厌的家伙，人家也讨厌！")
            return
        elif acceptance == 2:
            await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
            yield event.plain_result("抱歉啦~♪ 只有在白名单的主人们才能使用该插件喵~♪")
            return
        else:
            message = event.message_obj.message # 获取消息中的 message 字段

            if message and isinstance(message[0], Comp.Reply): # 如果消息链中有一个元素，并且这个元素是回复组件
                reply = message[0].chain # 获取回复组件中的消息链
                if reply and len(reply) == 1 and isinstance(reply[0], Comp.Image): # 如果回复组件中的消息链中只有一个元素，并且这个元素是图片组件
                    img = reply[0] # 获取图片组件

                    # logger.info(f"收到保存表情包的请求，save_path: '{save_path}', image_name: '{image_name}'")

                    is_valid_save_path = is_safe_windows_relative_path(save_path) if save_path else True

                    if save_path and not is_valid_save_path:
                        await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
                        yield event.plain_result(f"诶诶诶~ “{save_path}” 在 Windows 中是无效或不安全的保存路径呢……是不小心犯错了呢，还是想要对人家越界呢♡？")
                        return

                    is_valid_image_name = is_valid_windows_filename(image_name) if image_name else True

                    if image_name and not is_valid_image_name:
                        await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
                        yield event.plain_result(f"哎呀呀~ “{image_name}” 在 Windows 中是无效的文件名哦~♪")
                        return

                    if image_name:
                        image_name = image_name.strip() # 去除用户提供的 image_name 参数的前后空白
                    else:
                        image_name = os.path.splitext(os.path.basename(img.file or "image"))[0] # 从图片的原始文件名中提取不带扩展名的部分作为 image_name，如果原始文件名不可用则使用 "image" 作为默认名字

                    plugin_data_path = Path(get_astrbot_data_path()) / "plugin_data" / self.name # self.name 为插件名称，在 v4.9.2 及以上版本可用，低于此版本请自行指定插件名称
                    save_directory = plugin_data_path / "memes" / save_path # 构造保存目录的路径，默认为插件数据目录下的 memes 文件夹中的 save_path 子文件夹

                    root_path = plugin_data_path.resolve(strict=False)
                    save_directory = save_directory.resolve(strict=False)
                    try:
                        save_directory.relative_to(root_path)
                    except ValueError:
                        yield event.plain_result("保存路径无效或超出插件目录，请使用安全的相对路径【考虑到我们已经做了安全检查，这条错误信息是不应该出现的】。")
                        return

                    save_directory.mkdir(parents=True, exist_ok=True) # 创建保存目录，如果目录已经存在则忽略

                    # 异步下载
                    url = img.url
                    if not url:
                        yield event.plain_result("图片 URL 无效，无法下载表情包【这条错误信息是不应该出现的】。")
                        return

                    await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
                    yield event.plain_result("马上就帮您把表情包保存到本地哦~♪")

                    # logger.info(f"正在下载图片，URL: {url}, 保存目录: {save_directory}, 保存名称: {image_name}")
                    success = await self.download_image_async(url, str(save_directory), image_name)
                    if success:
                        # 记录元数据...
                        await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
                        yield event.plain_result(f"表情包已保存为 {success}！女仆修行又进了一步呢~♪")
                    else:
                        await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
                        yield event.plain_result("搞，搞糟了~~~ 怎么会这样 QAQ……")

                else:
                    await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
                    yield event.plain_result("请确保您发送的消息中引用了单张表情包哦（人家现在会做的事情还很少，请原谅人家啦 QAQ）")
            else:
                await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
                yield event.plain_result("请确保您发送的消息中引用了单张表情包哦（人家现在会做的事情还很少，请原谅人家啦 QAQ）")

    # 监听私聊消息事件
    # @filter.event_message_type(filter.EventMessageType.PRIVATE_MESSAGE)
    # async def log_for_debug(self, event: AstrMessageEvent):
    #     message_obj = event.message_obj # 获取消息的对象内容

    #     self_id = message_obj.self_id # 获取消息中的 self_id 字段
    #     message_id = message_obj.message_id # 获取消息中的 message_id 字段
    #     sender = message_obj.sender # 获取消息中的 sender 字段
    #     message = message_obj.message # 获取消息中的 message 字段
    #     timestamp = message_obj.timestamp # 获取消息中的 timestamp 字段

    #     date_time = datetime.datetime.fromtimestamp(timestamp) # 将 timestamp 转换为 datetime 对象
    #     readable_time = date_time.strftime("%Y-%m-%d %H:%M:%S") # 将 datetime 对象格式化为可读的字符串

    #     if message:
    #         logger.info(f"{self_id} 收到了来自 {sender} 于 {readable_time} 发出的一条私聊消息，消息编号为 {message_id}，消息内容为：{message}。")
    #     else:
    #         logger.info(f"{sender} 正在输入。")
