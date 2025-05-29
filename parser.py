# Copyright: (c) OpenChiip Organization. https://github.com/OpenChiip/Chiip
# Copyright: (c) <aigc@openchiip.com>
# Generated model: Qwen2.5-coder
# Released under the AIGCGPL-1.0 License.

"""
需求解析模块，负责分析用户的自然语言需求并提取关键信息
"""
import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

class RequirementType(Enum):
    """需求类型枚举"""
    CREATE = auto()  # 创建新代码
    MODIFY = auto()  # 修改现有代码
    UNKNOWN = auto() # 未知类型

@dataclass
class FileRequirement:
    """文件需求信息"""
    path: str                    # 文件路径
    language: str               # 编程语言
    description: str            # 功能描述
    dependencies: List[str]     # 依赖项列表
    is_test: bool = False      # 是否为测试文件

@dataclass
class ParsedRequirement:
    """解析后的需求信息"""
    type: RequirementType                       # 需求类型
    files: List[FileRequirement]               # 相关文件列表
    description: str                           # 需求描述
    modification_details: Optional[str] = None  # 修改详情（仅用于MODIFY类型）

class RequirementParser:
    """需求解析器"""
    
    def __init__(self):
        """初始化解析器"""
        # 编程语言关键词映射
        self.language_keywords = {
            'python': ['python', 'py', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'js', 'node', 'nodejs', 'react', 'vue'],
            'typescript': ['typescript', 'ts', 'angular'],
            'java': ['java', 'spring', 'maven', 'gradle'],
            'cpp': ['c++', 'cpp', 'cmake'],
            'go': ['go', 'golang'],
            'rust': ['rust', 'cargo'],
        }
        
        # 文件类型后缀映射
        self.file_extensions = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'cpp': '.cpp',
            'go': '.go',
            'rust': '.rs',
        }

    def parse(self, requirement: str) -> ParsedRequirement:
        """
        解析用户需求
        
        Args:
            requirement: 用户输入的需求描述
            
        Returns:
            ParsedRequirement: 解析后的需求信息
        """
        # 确定需求类型
        req_type = self._determine_type(requirement)
        
        # 提取文件需求
        files = self._extract_file_requirements(requirement)
        
        # 创建ParsedRequirement对象
        parsed = ParsedRequirement(
            type=req_type,
            files=files,
            description=requirement
        )
        
        # 如果是修改类型，提取修改详情
        if req_type == RequirementType.MODIFY:
            parsed.modification_details = self._extract_modification_details(requirement)
        
        return parsed

    def _determine_type(self, requirement: str) -> RequirementType:
        """
        确定需求类型
        
        Args:
            requirement: 需求描述
            
        Returns:
            RequirementType: 需求类型
        """
        # 修改相关的关键词
        modify_keywords = ['修改', '更新', '改变', '优化', '重构', '修复', 'modify', 'update', 'change', 'optimize', 'refactor', 'fix']
        
        # 创建相关的关键词
        create_keywords = ['创建', '新建', '生成', '实现', 'create', 'new', 'generate', 'implement']
        
        requirement_lower = requirement.lower()
        
        # 检查是否包含修改关键词
        if any(keyword in requirement_lower for keyword in modify_keywords):
            return RequirementType.MODIFY
            
        # 检查是否包含创建关键词
        if any(keyword in requirement_lower for keyword in create_keywords):
            return RequirementType.CREATE
            
        # 默认为创建类型
        return RequirementType.CREATE

    def _extract_file_requirements(self, requirement: str) -> List[FileRequirement]:
        """
        提取文件需求
        
        Args:
            requirement: 需求描述
            
        Returns:
            List[FileRequirement]: 文件需求列表
        """
        files = []
        
        # 检测编程语言
        detected_language = self._detect_language(requirement)
        
        # 检测是否包含测试相关内容
        is_test = bool(re.search(r'测试|test|spec|unit', requirement.lower()))
        
        # 从需求中提取可能的文件名
        file_patterns = [
            r'文件[名路径]*[：:]\s*([^\s,，.。]+)',
            r'[创建修改更新].*?[文件模块]:\s*([^\s,，.。]+)',
            r'(?:in|at|在)\s+([^\s,，.。]+?\.(?:py|js|ts|java|cpp|go|rs))',
        ]
        
        found_files = set()
        for pattern in file_patterns:
            matches = re.finditer(pattern, requirement)
            for match in matches:
                found_files.add(match.group(1))
        
        # 如果没有找到明确的文件名，根据需求生成一个合理的文件名
        if not found_files:
            words = re.findall(r'[a-zA-Z]+', requirement)
            if words:
                # 使用找到的英文单词生成文件名
                file_name = '_'.join(words[:3]).lower()  # 最多使用前三个单词
            else:
                # 如果没有英文单词，使用默认名称
                file_name = 'main'
            
            # 添加适当的文件扩展名
            file_name += self.file_extensions.get(detected_language, '.py')
            found_files.add(file_name)
        
        # 创建FileRequirement对象
        for file_name in found_files:
            # 确保文件名有正确的扩展名
            if not any(file_name.endswith(ext) for ext in self.file_extensions.values()):
                file_name += self.file_extensions.get(detected_language, '.py')
            
            files.append(FileRequirement(
                path=file_name,
                language=detected_language,
                description=requirement,
                dependencies=[],  # TODO: 实现依赖项提取
                is_test=is_test
            ))
        
        return files

    def _detect_language(self, requirement: str) -> str:
        """
        从需求中检测编程语言
        
        Args:
            requirement: 需求描述
            
        Returns:
            str: 检测到的编程语言
        """
        requirement_lower = requirement.lower()
        
        # 检查每种语言的关键词
        for language, keywords in self.language_keywords.items():
            if any(keyword in requirement_lower for keyword in keywords):
                return language
        
        # 默认返回python
        return 'python'

    def _extract_modification_details(self, requirement: str) -> str:
        """
        提取修改详情
        
        Args:
            requirement: 需求描述
            
        Returns:
            str: 修改详情描述
        """
        # 查找修改相关的描述
        patterns = [
            r'(?:修改|更新|改变|优化|重构|修复)[:：\s]+(.+?)(?:\.。$|$)',
            r'(?:modify|update|change|optimize|refactor|fix)[:：\s]+(.+?)(?:\.。$|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, requirement)
            if match:
                return match.group(1).strip()
        
        # 如果没有找到特定的修改描述，返回完整的需求描述
        return requirement