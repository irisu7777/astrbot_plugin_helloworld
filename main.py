import asyncio
import datetime
import os
import random
from pathlib import Path

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
        safe_name = "".join(c for c in base_name if c.isalnum() or c in "._- ")
        filename = f"{safe_name}{ext}"
        save_path = os.path.join(save_path, filename)

        with open(save_path, "wb") as f:
            f.write(img_data)

        return filename

    @filter.command_group("savememe", alias={"sm"})
    @filter.event_message_type(filter.EventMessageType.PRIVATE_MESSAGE)
    def savememe(self):
        pass

    @savememe.command("help")
    async def help(self, event: AstrMessageEvent):
        sender_id = event.message_obj.sender.user_id # 获取发送者的 user_id 字段

        blocked_users_enabled = self.config.get("blocked_users_enabled", False) # 从配置中获取是否启用禁止用户列表的开关，默认为 False
        blocked_users = self.config.get("blocked_users", []) # 从配置中获取禁止使用插件的用户列表，默认为空列表

        if blocked_users_enabled and sender_id in blocked_users: # 如果启用了禁止用户列表的开关，并且发送者的 user_id 在禁止使用插件的用户列表中
            await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
            yield event.plain_result("呜，是被主人放进黑名单的人……主人讨厌的家伙，人家也讨厌！")
            return

        allowed_users_enabled = self.config.get("allowed_users_enabled", False) # 从配置中获取是否启用允许用户列表的开关，默认为 False
        allowed_users = self.config.get("allowed_users", []) # 从配置中获取允许使用插件的用户列表，默认为空列表

        if allowed_users_enabled and sender_id not in allowed_users: # 如果启用了允许用户列表的开关，并且发送者的 user_id 不在允许使用插件的用户列表中
            await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
            yield event.plain_result("抱歉啦~♪ 只有在白名单的主人们才能使用该插件喵~♪")
            return

        await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
        yield event.plain_result("꧁༺【Help me, SAVEMEME!!】༻꧂\n\n❗请好好按照以下方法来玩弄女仆哦❗\n\n 1. 引用想要保存的表情包，并发送 /savememe save <save_path> <image_name> \n - save_path 是可选参数，默认为 memes。图片将被保存到插件数据目录下的 save_path 文件夹中。\n - image_name 是可选参数，默认为空。如果不提供，插件会使用图片的原始文件名（不带扩展名）作为保存的文件名。\n示例：\n引用一张图片，并发送 /savememe save memes funny_cat\n这将把图片保存到插件数据目录下的 memes 文件夹中，文件名为 funny_cat.gif（如果图片是 GIF 格式的话）。\n\n2. ... （人家现在会的事情还很少，不过作为主人的女仆，人家迟早会做到完美潇洒的程度的。嗯哼~♪）")

    @savememe.command("save")
    async def save(self, event: AstrMessageEvent, save_path: str = "memes", image_name: str = ""):
        sender_id = event.message_obj.sender.user_id # 获取发送者的 user_id 字段

        blocked_users_enabled = self.config.get("blocked_users_enabled", False) # 从配置中获取是否启用禁止用户列表的开关，默认为 False
        blocked_users = self.config.get("blocked_users", []) # 从配置中获取禁止使用插件的用户列表，默认为空列表

        if blocked_users_enabled and sender_id in blocked_users: # 如果启用了禁止用户列表的开关，并且发送者的 user_id 在禁止使用插件的用户列表中
            await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
            yield event.plain_result("呜，是被主人放进黑名单的人……主人讨厌的家伙，人家也讨厌！")
            return

        allowed_users_enabled = self.config.get("allowed_users_enabled", False) # 从配置中获取是否启用允许用户列表的开关，默认为 False
        allowed_users = self.config.get("allowed_users", []) # 从配置中获取允许使用插件的用户列表，默认为空列表

        if allowed_users_enabled and sender_id not in allowed_users: # 如果启用了允许用户列表的开关，并且发送者的 user_id 不在允许使用插件的用户列表中
            await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
            yield event.plain_result("抱歉啦~♪ 只有在白名单的主人们才能使用该插件喵~♪")
            return

        message = event.message_obj.message # 获取消息中的 message 字段
        logger.info(f"收到 savememe save 命令，发送者 ID: {sender_id}，消息内容: {message}, save_path: {save_path}, image_name: {image_name}")

        if message and isinstance(message[0], Comp.Reply): # 如果消息链中有一个元素，并且这个元素是回复组件
            reply = message[0].chain # 获取回复组件中的消息链
            if reply and len(reply) == 1 and isinstance(reply[0], Comp.Image): # 如果回复组件中的消息链中只有一个元素，并且这个元素是图片组件
                img = reply[0] # 获取图片组件

                if image_name:
                    image_name = image_name.strip() # 去除用户提供的 image_name 参数的前后空白
                else:
                    image_name = os.path.splitext(os.path.basename(img.file))[0] # 如果用户没有提供 image_name 参数，就使用图片文件名（不带扩展名）

                plugin_data_path = Path(get_astrbot_data_path()) / "plugin_data" / self.name # self.name 为插件名称，在 v4.9.2 及以上版本可用，低于此版本请自行指定插件名称
                save_directory = plugin_data_path / save_path # 构建保存目录的路径
                save_directory.mkdir(parents=True, exist_ok=True) # 创建保存目录，如果目录已经存在则忽略

                await asyncio.sleep(random.uniform(1, 3.14)) # 模拟处理消息的时间，随机等待 1-3.14 秒
                yield event.plain_result("马上就帮您把表情包保存到本地哦~♪")

                # 异步下载
                success = await self.download_image_async(img.url, str(save_directory), image_name)
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
    @filter.event_message_type(filter.EventMessageType.PRIVATE_MESSAGE)
    async def log_for_debug(self, event: AstrMessageEvent):
        message_obj = event.message_obj # 获取消息的对象内容

        self_id = message_obj.self_id # 获取消息中的 self_id 字段
        message_id = message_obj.message_id # 获取消息中的 message_id 字段
        sender = message_obj.sender # 获取消息中的 sender 字段
        message = message_obj.message # 获取消息中的 message 字段
        timestamp = message_obj.timestamp # 获取消息中的 timestamp 字段

        date_time = datetime.datetime.fromtimestamp(timestamp) # 将 timestamp 转换为 datetime 对象
        readable_time = date_time.strftime("%Y-%m-%d %H:%M:%S") # 将 datetime 对象格式化为可读的字符串

        if message:
            logger.info(f"{self_id} 收到了来自 {sender} 于 {readable_time} 发出的一条私聊消息，消息编号为 {message_id}，消息内容为：{message}。")
        else:
            logger.info(f"{sender} 正在输入。")
