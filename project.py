# Copyright: (c) OpenChiip Organization. https://github.com/OpenChiip/Chiip
# Copyright: (c) <aigc@openchiip.com>
# Generated model: Qwen2.5-coder
# Released under the AIGCGPL-1.0 License.

"""
项目管理模块，负责管理项目元数据和文件变更
"""
import json
import logging
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

from file_manager import FileManager
from utils.validation import validate_project_structure

logger = logging.getLogger(__name__)

@dataclass
class FileChange:
    """文件变更记录"""
    timestamp: float           # 变更时间戳
    operation: str            # 操作类型：create/modify/delete
    path: str                # 文件路径
    description: str         # 变更描述
    content_hash: Optional[str] = None  # 文件内容的哈希值（用于检测变化）

@dataclass
class ProjectMetadata:
    """项目元数据"""
    name: str                # 项目名称
    description: str         # 项目描述
    created_at: float       # 创建时间戳
    updated_at: float       # 最后更新时间戳
    version: str            # 项目版本
    language: str           # 主要编程语言
    dependencies: List[str]  # 项目依赖
    tags: List[str]         # 项目标签

class Project:
    """项目管理类"""
    
    def __init__(self, workspace_dir: str):
        """
        初始化项目管理器
        
        Args:
            workspace_dir: 工作目录路径
        """
        self.workspace_dir = Path(workspace_dir)
        self.file_manager = FileManager(workspace_dir)
        self.metadata: Optional[ProjectMetadata] = None
        self.changes: List[FileChange] = []
        self.tracked_files: Set[str] = set()
        
        # 确保项目目录存在
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
    
    def create(self, name: str, description: str = "", **kwargs) -> None:
        """
        创建新项目
        
        Args:
            name: 项目名称
            description: 项目描述
            **kwargs: 其他元数据字段
        """
        current_time = time.time()
        
        self.metadata = ProjectMetadata(
            name=name,
            description=description,
            created_at=current_time,
            updated_at=current_time,
            version=kwargs.get('version', '0.1.0'),
            language=kwargs.get('language', 'python'),
            dependencies=kwargs.get('dependencies', []),
            tags=kwargs.get('tags', [])
        )
        
        # 保存项目元数据
        self._save_metadata()
        
        logger.info(f"已创建项目: {name}")
    
    def load(self) -> bool:
        """
        加载项目
        
        Returns:
            bool: 是否成功加载
        """
        try:
            # 加载元数据
            metadata_path = self.workspace_dir / '.chiip' / 'metadata.json'
            if not metadata_path.exists():
                logger.error(f"项目元数据文件不存在: {metadata_path}")
                return False
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.metadata = ProjectMetadata(**data)
            
            # 加载变更历史
            changes_path = self.workspace_dir / '.chiip' / 'changes.json'
            if changes_path.exists():
                with open(changes_path, 'r', encoding='utf-8') as f:
                    changes_data = json.load(f)
                    self.changes = [FileChange(**change) for change in changes_data]
            
            # 更新跟踪的文件列表
            self._update_tracked_files()
            
            logger.info(f"已加载项目: {self.metadata.name}")
            return True
            
        except Exception as e:
            logger.error(f"加载项目时出错: {e}", exc_info=True)
            return False
    
    def save(self) -> bool:
        """
        保存项目
        
        Returns:
            bool: 是否成功保存
        """
        try:
            if not self.metadata:
                logger.error("没有项目元数据可保存")
                return False
            
            # 更新最后修改时间
            self.metadata.updated_at = time.time()
            
            # 保存元数据和变更历史
            self._save_metadata()
            self._save_changes()
            
            logger.info(f"已保存项目: {self.metadata.name}")
            return True
            
        except Exception as e:
            logger.error(f"保存项目时出错: {e}", exc_info=True)
            return False
    
    def record_change(self, operation: str, path: str, description: str) -> None:
        """
        记录文件变更
        
        Args:
            operation: 操作类型
            path: 文件路径
            description: 变更描述
        """
        content_hash = None
        if operation != 'delete':
            content = self.file_manager.read_file(path)
            if content:
                import hashlib
                content_hash = hashlib.md5(content.encode()).hexdigest()
        
        change = FileChange(
            timestamp=time.time(),
            operation=operation,
            path=path,
            description=description,
            content_hash=content_hash
        )
        
        self.changes.append(change)
        self._update_tracked_files()
        self._save_changes()
    
    def create_from_template(self, template: Dict[str, Any]) -> bool:
        """
        从模板创建项目结构
        
        Args:
            template: 项目结构模板
            
        Returns:
            bool: 是否成功创建
        """
        try:
            # 验证模板结构
            validation_result = validate_project_structure(template)
            if not validation_result['is_valid']:
                logger.error(f"无效的项目结构模板: {validation_result['errors']}")
                return False
            
            def create_structure(structure: Dict[str, Any], current_path: Path) -> None:
                """递归创建目录结构"""
                for name, content in structure.items():
                    path = current_path / name
                    
                    if isinstance(content, dict):
                        # 创建目录
                        path.mkdir(exist_ok=True)
                        create_structure(content, path)
                    elif isinstance(content, str):
                        # 创建文件
                        path.write_text(content, encoding='utf-8')
                        self.record_change('create', str(path.relative_to(self.workspace_dir)), '从模板创建文件')
                    elif isinstance(content, list):
                        # 创建多个文件
                        for item in content:
                            if isinstance(item, str):
                                file_path = path / item
                                file_path.touch()
                                self.record_change('create', str(file_path.relative_to(self.workspace_dir)), '从模板创建文件')
            
            # 创建项目结构
            create_structure(template, self.workspace_dir)
            
            logger.info("已从模板创建项目结构")
            return True
            
        except Exception as e:
            logger.error(f"从模板创建项目结构时出错: {e}", exc_info=True)
            return False
    
    def get_file_history(self, path: str) -> List[FileChange]:
        """
        获取文件的变更历史
        
        Args:
            path: 文件路径
            
        Returns:
            List[FileChange]: 变更历史列表
        """
        return [change for change in self.changes if change.path == path]
    
    def get_recent_changes(self, limit: int = 10) -> List[FileChange]:
        """
        获取最近的变更记录
        
        Args:
            limit: 返回的记录数量
            
        Returns:
            List[FileChange]: 变更记录列表
        """
        return sorted(
            self.changes,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
    
    def update_dependencies(self, dependencies: List[str]) -> None:
        """
        更新项目依赖
        
        Args:
            dependencies: 新的依赖列表
        """
        if not self.metadata:
            logger.error("没有项目元数据")
            return
        
        self.metadata.dependencies = list(set(self.metadata.dependencies + dependencies))
        self._save_metadata()
    
    def _save_metadata(self) -> None:
        """保存项目元数据"""
        if not self.metadata:
            return
        
        metadata_dir = self.workspace_dir / '.chiip'
        metadata_dir.mkdir(exist_ok=True)
        
        metadata_path = metadata_dir / 'metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.metadata), f, indent=2)
    
    def _save_changes(self) -> None:
        """保存变更历史"""
        changes_dir = self.workspace_dir / '.chiip'
        changes_dir.mkdir(exist_ok=True)
        
        changes_path = changes_dir / 'changes.json'
        with open(changes_path, 'w', encoding='utf-8') as f:
            json.dump([asdict(change) for change in self.changes], f, indent=2)
    
    def _update_tracked_files(self) -> None:
        """更新跟踪的文件列表"""
        self.tracked_files = {
            change.path
            for change in self.changes
            if change.operation != 'delete'
        }
    
    def get_project_info(self) -> Dict[str, Any]:
        """
        获取项目信息
        
        Returns:
            Dict[str, Any]: 项目信息字典
        """
        if not self.metadata:
            return {}
        
        return {
            **asdict(self.metadata),
            'tracked_files': list(self.tracked_files),
            'recent_changes': [
                asdict(change)
                for change in self.get_recent_changes(5)
            ]
        }
    
    def export_project(self, output_dir: str) -> bool:
        """
        导出项目
        
        Args:
            output_dir: 输出目录路径
            
        Returns:
            bool: 是否成功导出
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 复制项目文件
            for file_path in self.tracked_files:
                src_path = self.workspace_dir / file_path
                dst_path = output_path / file_path
                
                if src_path.exists():
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    import shutil
                    shutil.copy2(src_path, dst_path)
            
            # 导出项目信息
            project_info = self.get_project_info()
            with open(output_path / 'project_info.json', 'w', encoding='utf-8') as f:
                json.dump(project_info, f, indent=2)
            
            logger.info(f"已导出项目到: {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"导出项目时出错: {e}", exc_info=True)
            return False