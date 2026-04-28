import os
from pathlib import PureWindowsPath

INVALID_CHARS = set(r'<>:"/\\|?*')
MAX_WINDOWS_NAME_LENGTH = 255
MAX_WINDOWS_PATH_LENGTH = 260
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def _is_valid_windows_name(name: str) -> bool:
    """
    检查单个文件或目录名称是否符合 Windows 的命名规则。
    这不检查路径，只检查名称本身。
    """
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
    """检查一个字符串是否是一个有效的 Windows 文件或目录名称。"""
    if os.path.basename(name) != name:
        # reject paths like "foo/bar.txt" or "C:\foo.txt"
        return False

    return _is_valid_windows_name(name)


def is_safe_windows_relative_path(path: str) -> bool:
    """检查一个字符串是否是一个安全的 Windows 相对路径。"""
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