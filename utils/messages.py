def build_savememe_help_text() -> str:
    """返回 /savememe help 命令的帮助文本。"""
    return """꧁༺【Help me, SAVEMEME!!】༻꧂

❗请好好按照以下方法来玩弄女仆哦❗

1. 引用想要保存的图片，并发送 /savememe save <image_name> <save_path>

- image_name（可选字符串参数，默认为 "meme"）。图片将被保存为 image_name.<extension>。
请注意，插件会根据图片内容自动识别扩展名，所以 image_name 不需要包含扩展名【划重点】。

- save_path（可选字符串参数，默认为空）。图片将被保存在插件数据目录下的 memes/save_path。

示例：
引用一张图片，并发送 /savememe cute_cat save，则可将图片保存到插件数据目录下的 memes/save 文件夹中，名字为 cute_cat.<extension>

【注意】如果 cute_cat 已经存在，插件会自动尝试 cute_cat_1、cute_cat_2 等名字，直到找到一个可用的名字或者放弃保存（如果同名文件多于100个）。

2. ... （人家现在会的事情还很少，不过作为主人的女仆，人家迟早会做到完美潇洒的程度的。所以如果有新功能建议的话，也请大家帮帮这个笨蛋女仆哦 OwO！）"""

def build_meme_help_text() -> str:
    """返回 /meme help 命令的帮助文本。"""
    return """꧁༺【PokéMEME GO!!】༻꧂

❗请好好按照以下方法来玩弄女仆哦❗

1. 发送 /meme send <image_path>（或者 /mm s <image_path>）来让 Bot 替你发送表情包。

- image_path 是相对于插件数据目录下 memes 文件夹的路径，比如 save/cute_cat.png。

示例：
发送 /meme send save/cute_cat.png 就可以让 Bot 发送插件数据目录下 memes/save 文件夹中的 cute_cat.png 这张表情包。

2. ... （人家现在会的事情还很少，不过作为主人的女仆，人家迟早会做到完美潇洒的程度的。所以如果有新功能建议的话，也请大家帮帮这个笨蛋女仆哦 OwO！）
    """

def build_blocked_user_message() -> str:
    """返回用户被黑名单屏蔽时的提示消息。"""
    return "呜，是被主人放进黑名单的人……主人讨厌的家伙，人家也讨厌！"

def build_not_in_allowed_user_list_message() -> str:
    """返回用户不在白名单时的提示消息。"""
    return "抱歉啦~♪ 只有在白名单的主人们才能使用该插件喵~♪"

def build_filename_invalid_message(filename: str) -> str:
    """返回文件名无效时的提示消息。"""
    return f"哎呀呀~ “{filename}” 在 Windows 中是无效的文件名哦~♪"

def build_pathname_invalid_or_unsafe_message(pathname: str) -> str:
    """返回路径无效或不安全时的提示消息。"""
    return f"诶诶诶~ “{pathname}” 在 Windows 中是无效或不安全的路径呢……是不小心犯错了呢，还是想要对人家越界了呢♡？"

def build_savememe_save_success_message(filename: str, save_path: str) -> str:
    """返回表情包保存成功时的提示消息。"""
    return f"表情包已经成功保存为“插件数据目录/memes{save_path}/{filename}”！女仆修行又进了一步呢~♪"

def build_savememe_save_failure_message() -> str:
    """返回表情包保存失败时的提示消息。"""
    return "搞，搞糟了~~~ 怎么会这样 QAQ……"

def build_savememe_save_process_message() -> str:
    """返回表情包正在保存时的提示消息。"""
    return "马上就帮您把表情包保存到本地哦~♪"

def build_savememe_save_not_reply_message() -> str:
    """返回表情包保存时未引用消息的提示消息。"""
    return "请确保您引用了消息，不然人家是不知道主人想保存的表情包是什么的哦~♪"

def build_meme_image_not_found_message() -> str:
    """返回表情包图片未找到时的提示消息。"""
    return "啊啦啦，好像没有这张表情包哦~♪"

def build_meme_image_path_empty_message() -> str:
    """返回表情包图片路径为空时的提示消息。"""
    return "啊嘞嘞？到底是要发送什么表情包呢？qaq"