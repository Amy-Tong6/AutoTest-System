import re
from pathlib import Path
from typing import List, Optional
from yaml import full_load

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parents[1]

def read_file(path: str | Path) -> dict:
    """读取文件并返回内容"""
    try:
        with open(str(path), "r", encoding="utf-8") as f:
            return full_load(f)
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"读取文件失败: {e}")


def read_files(directory: str | Path, pattern: Optional[str] = None) -> List[Path]:
    """读取指定目录下的文件列表"""
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
        return str(variables_dict.get(var, match.group(0)))  # 如果变量不存在，保留原 {{var}}
    return re.sub(r'{{(\w+)}}', replacer, text)

def get_locator_str(data:dict) -> str:
    """获取定位器字符串"""
    return f"{data['locator_type']}={data['locator_value']}" if 'locator_type' in data and 'locator_value' in data else None

def get_cases(type: str)-> list[dict]:
    """生成测试用例数据"""
    case_paths = read_files(str(BASE_DIR / "cases" / type))
    cases = []

    for case_path in case_paths:
        file = read_file(case_path)
        details = {k: file.get(k) for k in ['enable', 'name', 'steps', 'assertions', 'reuse_browser']}
        test_data = file.get('test_data', [])

        if not test_data:
            cases.append({
                **details
            })

        for data in test_data:
            cases.append({
                **details,
                'data': data
            })

    return cases

def get_config(customer_id: str, key: str):
    """获取用户配置信息"""
    file = read_file(str(BASE_DIR / "config" / f"{customer_id}.yaml"))
    return file.get(key)