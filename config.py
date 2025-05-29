# Copyright: (c) OpenChiip Organization. https://github.com/OpenChiip/Chiip
# Copyright: (c) <aigc@openchiip.com>
# Generated model: Qwen2.5-coder
# Released under the AIGCGPL-1.0 License.

"""
配置管理模块，负责处理程序的配置信息
"""
import copy
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Config:
    """配置管理类"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        # 基本设置
        'workspace_dir': 'workspace',
        'log_level': 'INFO',
        'log_file': 'chiip.log',
        
        # AI模型设置
        'model': {
            'name': 'qwen2.5-coder-7b-instruct',
            'type': 'api',
            'api_key': 'None',
            'api_endpoint': 'http://172.19.0.1:12345/v1',
            'temperature': 0.6,
            'max_tokens': 20480
        },
        
        # 代码生成设置
        'code_generation': {
            'add_comments': True,
            'add_docstrings': True,
            'code_style': 'pep8'
        },
        
        # 文件操作设置
        'file_operations': {
            'backup_before_modify': True,
            'backup_dir': '.backups'
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，如果为None则使用默认路径
        """
        import threading
        self.config_file = config_file or 'config.json'
        self._lock = threading.Lock()
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        logger.info(f"初始化配置，model.temperature={self.config['model']['temperature']}")
        self.load()
    
    def load(self) -> bool:
        """
        从配置文件加载配置
        
        Returns:
            bool: 是否成功加载
        """
        try:
            config_path = Path(self.config_file)
            
            if not config_path.exists():
                logger.info(f"配置文件不存在，将使用默认配置: {self.config_file}")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # 更新配置，保留默认值
            self._update_config(self.config, user_config)
            
            logger.info(f"已从 {self.config_file} 加载配置")
            return True
            
        except Exception as e:
            logger.error(f"加载配置文件时出错: {e}", exc_info=True)
            return False
    
    def save(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            bool: 是否成功保存
        """
        try:
            config_path = Path(self.config_file)
            
            # 确保目录存在
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"已保存配置到 {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置文件时出错: {e}", exc_info=True)
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置项键名，支持点号分隔的嵌套键
            default: 默认值，如果配置项不存在则返回此值
            
        Returns:
            Any: 配置项的值
        """
        try:
            value = self.config
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def _is_valid_key(self, key: str) -> bool:
        """
        检查键名是否有效
        
        Args:
            key: 要检查的键名
            
        Returns:
            bool: 是否是有效键名
        """
        if key is None:
            return False
            
        if not isinstance(key, str) or not key.strip():
            return False
            
        # 允许任意格式的点分隔键名
        return True

    def set(self, key: str, value: Any) -> None:
        """
        设置配置项
        
        Args:
            key: 配置项键名，支持点号分隔的嵌套键
            value: 配置项的值
            
        Raises:
            ValueError: 如果键名无效
        """
        if not self._is_valid_key(key):
            raise ValueError(f"无效的配置键: {key}")
            
        keys = key.split('.')
        config = self.config
        
        # 遍历到最后一个键之前的所有键
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # 设置最后一个键的值
        config[keys[-1]] = value
    
    def reset(self) -> None:
        """重置为默认配置"""
        import copy
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        logger.info("配置已重置为默认值")
    
    def _update_config(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        递归更新配置字典
        
        Args:
            target: 目标配置字典
            source: 源配置字典
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_config(target[key], value)
            else:
                target[key] = value

def load_config(config_file: Optional[str] = None) -> Config:
    """
    加载配置的便捷函数
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        Config: 配置管理器实例
    """
    return Config(config_file)