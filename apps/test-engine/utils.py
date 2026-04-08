import re
from pathlib import Path
from typing import List, Optional
from yaml import full_load

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent

def read_file(path: str | Path) -> dict:
    """读取文件

    Args:
        path: 文件路径
    Returns:
        解析后的字典
    Raises:
        FileNotFoundError: 文件不存在时
        Exception: 解析失败时
    """
    try:
        with open(str(path), "r", encoding="utf-8") as f:
            return full_load(f)
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"读取文件失败: {e}")


def read_files(directory: str | Path, pattern: Optional[str] = None) -> List[Path]:
    """读取给定文件夹目录下的所有文件
    
    Args:
        directory: 文件夹路径（可以是字符串或 Path 对象）
        pattern: 可选的文件匹配模式，如 '*.yaml', '*.py' 等
        
    Returns:
        包含所有文件路径的列表（Path 对象）
        
    Raises:
        NotADirectoryError: 当给定路径不是目录时
        FileNotFoundError: 当目录不存在时
    """
    dir_path = Path(directory) if isinstance(directory, str) else directory
    
    if not dir_path.exists():
        raise FileNotFoundError(f"目录不存在：{dir_path}")
    
    if not dir_path.is_dir():
        raise NotADirectoryError(f"路径不是目录：{dir_path}")
    
    if pattern:
        return list(dir_path.glob(pattern))
    else:
        # 获取所有文件（不包括子目录）
        return [f for f in dir_path.iterdir() if f.is_file()]

def replace_variables(text: str|int, variables_dict: dict) -> str|int:
    """替换字符串中的 {{variable}} 为实际值"""
    # 如果不是字符串，直接返回（可能是数字等）
    if not isinstance(text, str):
        return text
    
    def replacer(match):
        var = match.group(1) # 变量名为 {{var}} 中的 var
        return variables_dict.get(var, match.group(0))  # 如果变量不存在，保留原 {{var}}
    return re.sub(r'{{(\w+)}}', replacer, text)


def get_user(user_id: str | None = None, config_path: str | Path = None) -> dict:
    """从配置文件获取用户信息
    
    Args:
        user_id: 用户 ID，不传则使用默认用户
        config_path: users.yaml 文件路径，不传则使用默认路径
        
    Returns:
        包含用户信息的字典
        
    Raises:
        FileNotFoundError: 当配置文件不存在时
        KeyError: 当用户 ID 不存在时
    """
    if config_path is None:
        # 使用默认的配置文件路径（config/users.yaml）
        base_dir = Path(__file__).resolve().parent
        config_path = base_dir / "config" / "users.yaml"
    
    # 读取配置文件
    users_config = read_file(config_path)
    
    # 如果没有指定 user_id，使用默认用户
    user_id = user_id or users_config.get("default_user")
    
    if not user_id:
        raise KeyError("未指定用户 ID 且配置文件中没有 default_user")
    
    if user_id not in users_config.get("users", {}):
        raise KeyError(f"用户 ID '{user_id}' 不存在")
    
    return users_config["users"][user_id]

def get_locator_str(data:dict) -> str:
    """获取定位器字符串"""
    return f"{data['locator_type']}={data['locator_value']}" if 'locator_type' in data and 'locator_value' in data else None

def get_cases(type: str):
    """获取指定类型的测试用例文件列表"""
    return read_files(str(BASE_DIR / "cases" / type))