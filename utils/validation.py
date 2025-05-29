# Copyright: (c) OpenChiip Organization. https://github.com/OpenChiip/Chiip
# Copyright: (c) <aigc@openchiip.com>
# Generated model: Qwen2.5-coder
# Released under the AIGCGPL-1.0 License.

"""
输入验证工具模块，提供各种验证函数
"""
import os
import re
from pathlib import Path
from typing import Union, List, Dict, Any, Optional

def validate_path(path: Union[str, Path], check_exists: bool = False) -> bool:
    """
    验证文件路径是否合法
    
    Args:
        path: 文件路径
        check_exists: 是否检查文件是否存在
        
    Returns:
        bool: 路径是否合法
    """
    try:
        # 转换为Path对象
        path_obj = Path(path)
        
        # 检查路径是否包含非法字符
        invalid_chars = '<>:"|?*'
        if any(char in str(path_obj.name) for char in invalid_chars):
            return False
        
        # 检查路径是否为绝对路径
        if path_obj.is_absolute():
            return False
        
        # 检查路径是否试图访问父目录
        if '..' in path_obj.parts:
            return False
        
        # 如果需要检查文件是否存在
        if check_exists and not path_obj.exists():
            return False
        
        return True
        
    except Exception:
        return False

def validate_content(content: str, content_type: str) -> bool:
    """
    验证内容格式是否合法
    
    Args:
        content: 要验证的内容
        content_type: 内容类型（如'python', 'json', 'xml'等）
        
    Returns:
        bool: 内容是否合法
    """
    if not content or not content_type:
        return False
    
    content_type = content_type.lower()
    
    try:
        if content_type == 'json':
            import json
            json.loads(content)
            return True
            
        elif content_type == 'xml':
            import xml.etree.ElementTree as ET
            ET.fromstring(content)
            return True
            
        elif content_type == 'python':
            import ast
            ast.parse(content)
            return True
            
        elif content_type == 'yaml':
            import yaml
            yaml.safe_load(content)
            return True
            
        else:
            # 对于其他类型，仅检查是否为非空字符串
            return bool(content.strip())
            
    except Exception:
        return False

def validate_file_name(file_name: str) -> bool:
    """
    验证文件名是否合法
    
    Args:
        file_name: 文件名
        
    Returns:
        bool: 文件名是否合法
    """
    if not file_name:
        return False
    
    # 文件名不应包含路径分隔符
    if '/' in file_name or '\\' in file_name:
        return False
    
    # 检查文件名中的非法字符
    invalid_chars = '<>:"|?*'
    if any(char in file_name for char in invalid_chars):
        return False
    
    # 文件名不应以点或空格开头或结尾
    if file_name.startswith(('.', ' ')) or file_name.endswith((' ')):
        return False
    
    # 文件名长度应在合理范围内
    if len(file_name) > 255:
        return False
    
    return True

def validate_directory_name(dir_name: str) -> bool:
    """
    验证目录名是否合法
    
    Args:
        dir_name: 目录名
        
    Returns:
        bool: 目录名是否合法
    """
    # 目录名的验证规则与文件名类似
    return validate_file_name(dir_name)

def validate_python_identifier(identifier: str) -> bool:
    """
    验证Python标识符是否合法
    
    Args:
        identifier: 要验证的标识符
        
    Returns:
        bool: 标识符是否合法
    """
    if not identifier:
        return False
    
    # Python标识符的正则表达式
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    
    return bool(re.match(pattern, identifier))

def validate_requirements(requirements: List[str]) -> bool:
    """
    验证Python包依赖列表是否合法
    
    Args:
        requirements: 依赖包列表
        
    Returns:
        bool: 依赖列表是否合法
    """
    if not requirements:
        return False
    
    # 包名规范的正则表达式
    pattern = r'^[a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*$'
    
    for req in requirements:
        # 移除版本信息进行验证
        package_name = req.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].strip()
        if not re.match(pattern, package_name):
            return False
    
    return True

def validate_code_block(code: str, language: str) -> Dict[str, Any]:
    """
    验证代码块的语法是否正确
    
    Args:
        code: 代码内容
        language: 编程语言
        
    Returns:
        Dict[str, Any]: 验证结果，包含：
            - is_valid: 是否有效
            - errors: 错误信息列表
    """
    result = {
        'is_valid': False,
        'errors': []
    }
    
    if not code or not language:
        result['errors'].append('代码或语言类型为空')
        return result
    
    try:
        if language.lower() == 'python':
            import ast
            ast.parse(code)
            result['is_valid'] = True
            
        elif language.lower() == 'javascript':
            # 这里可以集成JavaScript解析器，如esprima
            # 当前仅做基本检查
            if '{' in code and '}' in code:  # 简单的括号匹配检查
                result['is_valid'] = True
            else:
                result['errors'].append('JavaScript代码可能缺少大括号')
                
        else:
            # 对于其他语言，仅做基本的格式检查
            result['is_valid'] = bool(code.strip())
            if not result['is_valid']:
                result['errors'].append(f'不支持的语言类型：{language}')
    
    except SyntaxError as e:
        result['errors'].append(f'语法错误：{str(e)}')
    except Exception as e:
        result['errors'].append(f'验证过程出错：{str(e)}')
    
    return result

def validate_project_structure(structure: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证项目结构配置是否合法
    
    Args:
        structure: 项目结构配置字典
        
    Returns:
        Dict[str, Any]: 验证结果，包含：
            - is_valid: 是否有效
            - errors: 错误信息列表
    """
    result = {
        'is_valid': False,
        'errors': []
    }
    
    if not isinstance(structure, dict):
        result['errors'].append('项目结构必须是字典类型')
        return result
    
    def validate_node(node: Any, path: str) -> List[str]:
        """验证结构树的节点"""
        errors = []
        
        if isinstance(node, dict):
            # 目录节点
            for name, child in node.items():
                if not validate_directory_name(name):
                    errors.append(f'无效的目录名：{path}/{name}')
                errors.extend(validate_node(child, f'{path}/{name}'))
                
        elif isinstance(node, str):
            # 文件节点
            if not validate_file_name(node):
                errors.append(f'无效的文件名：{path}/{node}')
                
        elif isinstance(node, list):
            # 文件列表
            for item in node:
                if isinstance(item, str):
                    if not validate_file_name(item):
                        errors.append(f'无效的文件名：{path}/{item}')
                else:
                    errors.append(f'无效的文件列表项类型：{type(item)}')
                    
        else:
            errors.append(f'无效的节点类型：{type(node)}')
        
        return errors
    
    # 验证整个结构树
    errors = validate_node(structure, '')
    
    if errors:
        result['errors'].extend(errors)
    else:
        result['is_valid'] = True
    
    return result