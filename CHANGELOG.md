v0.1.0 更新：其实没有更新，就是单纯把模板克隆了过来 haha。

v0.2.0 更新：
- 支持将表情包保存到本地的新功能。请使用命令 `/savememe (/sm)` 来执行此操作；
- 添加了白名单与黑名单系统。

v0.2.1 更新：
- 增加了 CHANGELOG.md，现在你可以在 CHANGELOG.md 看到插件更新情况，而不是在 README.md；
- 规范了版本号，希望现在版本号是正确运作的。

v0.2.2 更新：
- 现在会检查文件名和文件路径是否正确与安全；
- 现在会检查是否已有重名表情包，若有重名则会尝试添加数字后缀，数字后缀最多添加到 100，之后将保存失败；
- 添加了 requirements.txt，在 metadata.yaml 中添加了 astrbot_version, display_name 项。

v0.2.3 更新：
- 修复了 metadata.yaml 中 version, astrbot_version 项格式错误的问题。

v0.2.4 更新：
- 增加了群组白名单与黑名单；
- 新建 utils，将与插件逻辑外的代码整合到该文件夹中；
- 重设 `/savememe save` 参数顺序，现在第一个可选参数将是文件名；
- 规范了图片下载，现在下载之前会做基本的安全检查，以及会拒绝过大图片的下载。

v0.2.5 更新：
- 修复了 build_savememe_save_success_message 中参数顺序错误的问题。