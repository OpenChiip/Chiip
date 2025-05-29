# Copyright: (c) OpenChiip Organization. https://github.com/OpenChiip/Chiip
# Copyright: (c) <aigc@openchiip.com>
# Generated model: Qwen2.5-coder
# Released under the AIGCGPL-1.0 License.

"""
文件系统操作模块，负责管理workspace目录中的文件操作
"""
import logging
import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class FileManager:
    """文件系统管理器"""
    
    def __init__(self, workspace_dir: str):
        """
        初始化文件管理器
        
        Args:
            workspace_dir: 工作目录路径
        """
        self.workspace_dir = Path(workspace_dir)
        if not self.workspace_dir.exists():
            self.workspace_dir.mkdir(parents=True)
            logger.info(f"创建工作目录: {self.workspace_dir.absolute()}")
    
    def create_file(self, path: str, content: str) -> bool:
        """
        创建文件
        
        Args:
            path: 相对于workspace的文件路径
            content: 文件内容
            
        Returns:
            bool: 是否成功创建
        """
        try:
            file_path = self._get_absolute_path(path)
            
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件内容
            file_path.write_text(content, encoding='utf-8')
            
            logger.info(f"已创建文件: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"创建文件 {path} 时出错: {e}", exc_info=True)
            return False
    
    def modify_file(self, path: str, modifications: List[Dict[str, Any]]) -> bool:
        """
        修改文件
        
        Args:
            path: 相对于workspace的文件路径
            modifications: 修改内容列表，每个修改包含：
                - start_line: 开始行号
                - end_line: 结束行号
                - new_content: 新内容
                
        Returns:
            bool: 是否成功修改
        """
        try:
            file_path = self._get_absolute_path(path)
            
            if not file_path.exists():
                logger.error(f"要修改的文件不存在: {file_path}")
                return False
            
            # 读取原始内容
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 应用修改
            for mod in sorted(modifications, key=lambda m: m['start_line'], reverse=True):
                start_line = mod['start_line'] - 1  # 转换为0-based索引
                end_line = mod['end_line']  # end_line是不包含的
                new_content = mod['new_content']
                
                # 验证行号
                if start_line < 0 or end_line > len(lines) or start_line >= end_line:
                    logger.warning(f"无效的行号范围: {start_line+1}-{end_line}")
                    continue
                
                # 替换内容
                new_lines = new_content.splitlines(True)
                lines[start_line:end_line] = new_lines
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            logger.info(f"已修改文件: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"修改文件 {path} 时出错: {e}", exc_info=True)
            return False
    
    def read_file(self, path: str) -> Optional[str]:
        """
        读取文件内容
        
        Args:
            path: 相对于workspace的文件路径
            
        Returns:
            Optional[str]: 文件内容，如果读取失败则返回None
        """
        try:
            file_path = self._get_absolute_path(path)
            
            if not file_path.exists():
                logger.error(f"要读取的文件不存在: {file_path}")
                return None
            
            content = file_path.read_text(encoding='utf-8')
            return content
            
        except Exception as e:
            logger.error(f"读取文件 {path} 时出错: {e}", exc_info=True)
            return None
    
    def file_exists(self, path: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            path: 相对于workspace的文件路径
            
        Returns:
            bool: 文件是否存在
        """
        file_path = self._get_absolute_path(path)
        return file_path.exists() and file_path.is_file()

    def directory_exists(self, path: str) -> bool:
        """
        检查目录是否存在
        
        Args:
            path: 相对于workspace的目录路径
            
        Returns:
            bool: 目录是否存在
        """
        dir_path = self._get_absolute_path(path)
        return dir_path.exists() and dir_path.is_dir()

    def get_file_size(self, path: str) -> int:
        """
        获取文件大小(字节)
        
        Args:
            path: 相对于workspace的文件路径
            
        Returns:
            int: 文件大小(字节)
        """
        file_path = self._get_absolute_path(path)
        return file_path.stat().st_size if self.file_exists(path) else -1

    def get_file_modification_time(self, path: str) -> float:
        """
        获取文件最后修改时间(时间戳)
        
        Args:
            path: 相对于workspace的文件路径
            
        Returns:
            float: 最后修改时间的时间戳
        """
        file_path = self._get_absolute_path(path)
        return file_path.stat().st_mtime if self.file_exists(path) else 0.0

    def list_files(self, path: str = '.', pattern: str = None) -> List[str]:
        """
        列出目录中的文件
        
        Args:
            path: 相对于workspace的目录路径
            pattern: 文件名匹配模式(如'*.txt')
            
        Returns:
            List[str]: 文件路径列表
        """
        try:
            dir_path = self._get_absolute_path(path)
            
            if not dir_path.exists() or not dir_path.is_dir():
                logger.error(f"目录不存在或不是一个目录: {dir_path}")
                return []
            
            # 根据是否有pattern选择不同的glob方法
            if pattern:
                search_pattern = f'**/{pattern}' if pattern.startswith('*') else pattern
                items = dir_path.glob(search_pattern)
            else:
                items = dir_path.glob('**/*')
            
            # 获取所有文件
            files = []
            for item in items:
                if item.is_file():
                    # 转换为相对于workspace的路径
                    rel_path = item.relative_to(self.workspace_dir)
                    files.append(str(rel_path))
            
            return files
            
        except Exception as e:
            logger.error(f"列出目录 {path} 中的文件时出错: {e}", exc_info=True)
            return []

    def backup_file(self, file_path: str, suffix: str = '.bak') -> str:
        """
        备份文件
        
        Args:
            file_path: 要备份的文件路径
            suffix: 备份文件后缀，默认为'.bak'
            
        Returns:
            str: 备份文件路径，失败返回None
        """
        try:
            if not self.file_exists(file_path):
                logger.error(f"要备份的文件不存在: {file_path}")
                return None
                
            backup_path = file_path + suffix
            if self.file_exists(backup_path):
                logger.warning(f"备份文件已存在，将被覆盖: {backup_path}")
                
            src = self._get_absolute_path(file_path)
            dst = self._get_absolute_path(backup_path)
            
            shutil.copy2(src, dst)
            logger.info(f"成功备份文件: {file_path} -> {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"备份文件 {file_path} 时出错: {e}", exc_info=True)
            return None

    def list_directories(self, path: str = '.') -> List[str]:
        """
        列出目录中的子目录
        
        Args:
            path: 相对于workspace的目录路径
            
        Returns:
            List[str]: 子目录路径列表
        """
        try:
            dir_path = self._get_absolute_path(path)
            
            if not dir_path.exists() or not dir_path.is_dir():
                logger.error(f"目录不存在或不是一个目录: {dir_path}")
                return []
            
            # 获取所有子目录
            directories = []
            for item in dir_path.iterdir():
                if item.is_dir():
                    # 转换为相对于workspace的路径
                    rel_path = item.relative_to(self.workspace_dir)
                    directories.append(str(rel_path))
            
            return directories
            
        except Exception as e:
            logger.error(f"列出目录 {path} 中的子目录时出错: {e}", exc_info=True)
            return []

    def write_file(self, file_path: str, content: str) -> bool:
        """
        写入文件(create_file的别名)
        
        Args:
            file_path: 文件路径
            content: 要写入的内容
            
        Returns:
            bool: 是否写入成功
        """
        return self.create_file(file_path, content)
        try:
            dir_path = self._get_absolute_path(path)
            
            if not dir_path.exists() or not dir_path.is_dir():
                logger.error(f"目录不存在或不是一个目录: {dir_path}")
                return []
            
            # 获取所有文件和目录
            files = []
            for item in dir_path.glob('**/*'):
                if item.is_file():
                    # 转换为相对于workspace的路径
                    rel_path = item.relative_to(self.workspace_dir)
                    files.append(str(rel_path))
            
            return files
            
        except Exception as e:
            logger.error(f"列出目录 {path} 中的文件时出错: {e}", exc_info=True)
            return []
    
    def delete_file(self, path: str) -> bool:
        """
        删除文件
        
        Args:
            path: 相对于workspace的文件路径
            
        Returns:
            bool: 是否成功删除
        """
        try:
            file_path = self._get_absolute_path(path)
            
            if not file_path.exists():
                logger.error(f"要删除的文件不存在: {file_path}")
                return False
            
            file_path.unlink()
            logger.info(f"已删除文件: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"删除文件 {path} 时出错: {e}", exc_info=True)
            return False
    
    def create_directory(self, path: str) -> bool:
        """
        创建目录
        
        Args:
            path: 相对于workspace的目录路径
            
        Returns:
            bool: 是否成功创建
        """
        try:
            dir_path = self._get_absolute_path(path)
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"已创建目录: {dir_path}")
            return True
            
        except Exception as e:
            logger.error(f"创建目录 {path} 时出错: {e}", exc_info=True)
            return False
    
    def copy_file(self, src_path: str, dst_path: str) -> bool:
        """
        复制文件
        
        Args:
            src_path: 相对于workspace的源文件路径
            dst_path: 相对于workspace的目标文件路径
            
        Returns:
            bool: 是否成功复制
        """
        try:
            src_file_path = self._get_absolute_path(src_path)
            dst_file_path = self._get_absolute_path(dst_path)
            
            if not src_file_path.exists():
                logger.error(f"要复制的源文件不存在: {src_file_path}")
                return False
            
            # 确保目标目录存在
            dst_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src_file_path, dst_file_path)
            logger.info(f"已复制文件: {src_file_path} -> {dst_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"复制文件 {src_path} 到 {dst_path} 时出错: {e}", exc_info=True)
            return False
    
    def move_file(self, src_path: str, dst_path: str) -> bool:
        """
        移动文件
        
        Args:
            src_path: 相对于workspace的源文件路径
            dst_path: 相对于workspace的目标文件路径
            
        Returns:
            bool: 是否成功移动
        """
        try:
            src_file_path = self._get_absolute_path(src_path)
            dst_file_path = self._get_absolute_path(dst_path)
            
            if not src_file_path.exists():
                logger.error(f"要移动的源文件不存在: {src_file_path}")
                return False
            
            # 确保目标目录存在
            dst_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(src_file_path, dst_file_path)
            logger.info(f"已移动文件: {src_file_path} -> {dst_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"移动文件 {src_path} 到 {dst_path} 时出错: {e}", exc_info=True)
            return False
    
    def _get_absolute_path(self, path: str) -> Path:
        """
        获取绝对路径
        
        Args:
            path: 相对于workspace的路径
            
        Returns:
            Path: 绝对路径
        """
        # 规范化路径，移除开头的 ./ 或 /
        norm_path = os.path.normpath(path)
        if norm_path.startswith('/'):
            norm_path = norm_path[1:]
        
        # 组合工作目录和相对路径
        return self.workspace_dir / norm_path