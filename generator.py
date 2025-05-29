# Copyright: (c) OpenChiip Organization. https://github.com/OpenChiip/Chiip
# Copyright: (c) <aigc@openchiip.com>
# Generated model: Qwen2.5-coder
# Released under the AIGCGPL-1.0 License.

"""
代码生成与修改模块，负责生成新代码或修改现有代码
"""
import logging
from dataclasses import dataclass
from difflib import unified_diff
from pathlib import Path
from typing import List, Optional, Dict, Any

from parser import ParsedRequirement, RequirementType, FileRequirement
from prompts import get_code_templates

logger = logging.getLogger(__name__)

@dataclass
class CodeChange:
    """代码修改信息"""
    file_path: str           # 文件路径
    original_content: str    # 原始内容
    new_content: str        # 新内容
    description: str        # 修改描述

@dataclass
class GenerationResult:
    """代码生成结果"""
    created_files: List[str]          # 创建的文件列表
    modified_files: List[str]         # 修改的文件列表
    changes: List[CodeChange]         # 具体的修改内容
    errors: List[str]                # 错误信息列表

class CodeGenerator:
    """代码生成器"""
    
    def __init__(self, workspace_dir: str):
        """
        初始化代码生成器
        
        Args:
            workspace_dir: 工作目录路径
        """
        self.workspace_dir = Path(workspace_dir)
        self.templates = get_code_templates()
        
    def generate(self, requirement: ParsedRequirement) -> GenerationResult:
        """
        根据需求生成或修改代码
        
        Args:
            requirement: 解析后的需求信息
            
        Returns:
            GenerationResult: 代码生成结果
        """
        result = GenerationResult(
            created_files=[],
            modified_files=[],
            changes=[],
            errors=[]
        )
        
        try:
            if requirement.type == RequirementType.CREATE:
                self._handle_creation(requirement, result)
            elif requirement.type == RequirementType.MODIFY:
                self._handle_modification(requirement, result)
            else:
                result.errors.append(f"未知的需求类型: {requirement.type}")
        
        except Exception as e:
            logger.error(f"代码生成过程中出现错误: {e}", exc_info=True)
            result.errors.append(str(e))
            
        return result
    
    def _handle_creation(self, requirement: ParsedRequirement, result: GenerationResult):
        """
        处理代码创建需求
        
        Args:
            requirement: 解析后的需求信息
            result: 代码生成结果
        """
        for file_req in requirement.files:
            try:
                # 生成代码内容
                content = self._generate_code(file_req)
                
                # 准备文件路径
                file_path = self.workspace_dir / file_req.path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 记录变更
                change = CodeChange(
                    file_path=str(file_path),
                    original_content="",
                    new_content=content,
                    description=f"创建新文件: {file_req.path}"
                )
                result.changes.append(change)
                result.created_files.append(file_req.path)
                
                # 写入文件
                file_path.write_text(content, encoding='utf-8')
                
                logger.info(f"已创建文件: {file_path}")
                
            except Exception as e:
                error_msg = f"创建文件 {file_req.path} 时出错: {e}"
                logger.error(error_msg)
                result.errors.append(error_msg)
    
    def _handle_modification(self, requirement: ParsedRequirement, result: GenerationResult):
        """
        处理代码修改需求
        
        Args:
            requirement: 解析后的需求信息
            result: 代码生成结果
        """
        for file_req in requirement.files:
            try:
                file_path = self.workspace_dir / file_req.path
                
                if not file_path.exists():
                    raise FileNotFoundError(f"要修改的文件不存在: {file_path}")
                
                # 读取原始内容
                original_content = file_path.read_text(encoding='utf-8')
                
                # 生成新内容
                new_content = self._modify_code(
                    original_content,
                    file_req,
                    requirement.modification_details
                )
                
                # 如果内容有变化
                if new_content != original_content:
                    # 记录变更
                    change = CodeChange(
                        file_path=str(file_path),
                        original_content=original_content,
                        new_content=new_content,
                        description=f"修改文件: {file_req.path}"
                    )
                    result.changes.append(change)
                    result.modified_files.append(file_req.path)
                    
                    # 写入文件
                    file_path.write_text(new_content, encoding='utf-8')
                    
                    logger.info(f"已修改文件: {file_path}")
                else:
                    logger.info(f"文件内容未发生变化: {file_path}")
                
            except Exception as e:
                error_msg = f"修改文件 {file_req.path} 时出错: {e}"
                logger.error(error_msg)
                result.errors.append(error_msg)
    
    def _generate_code(self, file_req: FileRequirement) -> str:
        """
        生成代码内容
        
        Args:
            file_req: 文件需求信息
            
        Returns:
            str: 生成的代码内容
        """
        # 获取适当的模板
        template_key = self._get_template_key(file_req)
        template = self.templates.get(template_key, self.templates['python_script'])
        
        # 准备模板变量
        template_vars = self._prepare_template_vars(file_req)
        
        # 填充模板
        try:
            content = template.format(**template_vars)
        except KeyError as e:
            logger.error(f"模板变量缺失: {e}")
            content = template.format(
                description="TODO: 添加描述",
                class_name="MainClass"
            )
        
        return content
    
    def _modify_code(self, original_content: str, file_req: FileRequirement, modification_details: str) -> str:
        """
        修改代码内容
        
        Args:
            original_content: 原始代码内容
            file_req: 文件需求信息
            modification_details: 修改详情
            
        Returns:
            str: 修改后的代码内容
        """
        # TODO: 实现更智能的代码修改逻辑
        # 当前实现仅添加注释说明修改内容
        
        lines = original_content.splitlines()
        
        # 在文件开头添加修改说明
        comment_char = '#' if file_req.language == 'python' else '//'
        modification_comment = f"{comment_char} 修改说明: {modification_details}\n"
        
        return modification_comment + original_content
    
    def _get_template_key(self, file_req: FileRequirement) -> str:
        """
        获取模板键名
        
        Args:
            file_req: 文件需求信息
            
        Returns:
            str: 模板键名
        """
        if file_req.is_test:
            return f"{file_req.language}_test"
        
        # 检查文件名是否暗示这是一个类文件
        if any(hint in file_req.path.lower() for hint in ['class', 'cls']):
            return f"{file_req.language}_class"
        
        return f"{file_req.language}_script"
    
    def _prepare_template_vars(self, file_req: FileRequirement) -> Dict[str, Any]:
        """
        准备模板变量
        
        Args:
            file_req: 文件需求信息
            
        Returns:
            Dict[str, Any]: 模板变量字典
        """
        # 从文件路径中提取类名
        class_name = Path(file_req.path).stem
        class_name = ''.join(word.capitalize() for word in class_name.split('_'))
        
        return {
            'description': file_req.description,
            'class_name': class_name
        }
    
    def get_diff(self, original: str, modified: str, file_path: str) -> str:
        """
        生成差异对比
        
        Args:
            original: 原始内容
            modified: 修改后的内容
            file_path: 文件路径
            
        Returns:
            str: 差异对比文本
        """
        diff = unified_diff(
            original.splitlines(keepends=True),
            modified.splitlines(keepends=True),
            fromfile=f'a/{file_path}',
            tofile=f'b/{file_path}',
            n=3
        )
        return ''.join(diff)