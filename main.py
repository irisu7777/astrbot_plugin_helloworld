from pathlib import Path

import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star
from astrbot.core.utils.astrbot_path import get_astrbot_data_path
from .utils.download import download_image_async
from .utils.messages import (
    build_savememe_help_text,
    build_filename_invalid_message,
    build_pathname_invalid_or_unsafe_message,
    build_savememe_save_success_message,
    build_savememe_save_failure_message,
    build_savememe_save_process_message,
    build_savememe_save_not_reply_message,
)
from .utils.response import (
    delayed_plain_result,
    get_user_acceptance_message,
)
from .utils.validators import is_safe_windows_relative_path, is_valid_windows_filename

class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig): # AstrBotConfig 继承自 Dict，拥有字典的所有方法
        super().__init__(context)
        self.config = config
        print(self.config)

    @filter.command_group("savememe", alias={"sm"})
    @filter.event_message_type(filter.EventMessageType.PRIVATE_MESSAGE)
    def savememe(self):
        pass

    @savememe.command("help")
    async def help(self, event: AstrMessageEvent):
        acceptance_message = get_user_acceptance_message(self.config, event.message_obj.sender.user_id) # 根据用户 ID 和插件配置检查是否应该拒绝服务，如果需要拒绝则返回拒绝消息，否则返回 None
        if acceptance_message is not None:
            yield await delayed_plain_result(event, acceptance_message)
            return

        yield await delayed_plain_result(event, build_savememe_help_text())

    @savememe.command("save")
    async def save(self, event: AstrMessageEvent, image_name: str = "meme", save_path: str = ""):
        acceptance_message = get_user_acceptance_message(self.config, event.message_obj.sender.user_id) # 根据用户 ID 和插件配置检查是否应该拒绝服务，如果需要拒绝则返回拒绝消息，否则返回 None
        if acceptance_message is not None:
            yield await delayed_plain_result(event, acceptance_message)
            return

        message = event.message_obj.message # 获取消息中的 message 字段

        if message and isinstance(message[0], Comp.Reply): # 如果消息链中有一个元素，并且这个元素是回复组件
            reply = message[0].chain # 获取回复组件中的消息链
            if reply and len(reply) == 1 and isinstance(reply[0], Comp.Image): # 如果回复组件中的消息链中只有一个元素，并且这个元素是图片组件
                img = reply[0] # 获取图片组件

                if not is_valid_windows_filename(image_name):
                    yield await delayed_plain_result(event, build_filename_invalid_message(image_name))
                    return

                if not is_safe_windows_relative_path(save_path):
                    yield await delayed_plain_result(event, build_pathname_invalid_or_unsafe_message(save_path))
                    return

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

                yield await delayed_plain_result(event, build_savememe_save_process_message())

                success = await download_image_async(img.url, str(save_directory), image_name)
                if success:
                    yield await delayed_plain_result(event, build_savememe_save_success_message(success, save_path))
                else:
                    yield await delayed_plain_result(event, build_savememe_save_failure_message())

            else: # 未完成模块
                yield await delayed_plain_result(
                    event,
                    "请确保您发送的消息中只引用了单张表情包哦（人家现在会做的事情还很少，请原谅人家啦 QAQ）",
                )
        else:
            yield await delayed_plain_result(event, build_savememe_save_not_reply_message())

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
