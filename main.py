#!/usr/bin/env python3
# Copyright: (c) OpenChiip Organization. https://github.com/OpenChiip/Chiip
# Copyright: (c) <aigc@openchiip.com>
# Generated model: Qwen2.5-coder
# Released under the AIGCGPL-1.0 License.

"""
Chiip - AI编程助手
主程序入口
"""
import argparse
import asyncio
import logging
import sys
from pathlib import Path

from ai_interface import AIAssistant, AIModelFactory
from cli import CLI
from config import Config, load_config
from file_manager import FileManager
from project import Project
from utils.logger import setup_logger

logger = logging.getLogger(__name__)

class CodeGenerator:
    def __init__(self, config: Config, workspace_dir: str = None):
        """
        初始化代码生成器
        
        Args:
            config: 配置对象
            workspace_dir: 工作目录路径（可选，如果不提供则使用配置中的值）
        """
        self.config = config
        self.workspace_dir = Path(workspace_dir or config.get('workspace_dir'))
        if not self.workspace_dir.exists():
            self.workspace_dir.mkdir(parents=True)
        
        self.file_manager = FileManager(str(self.workspace_dir))
        self.project = Project(str(self.workspace_dir))
        self.ai_assistant = AIAssistant(config)
        
        logger.info(f"工作目录: {self.workspace_dir.absolute()}")

    async def process_requirement(self, requirement: str):
        """
        处理用户需求
        
        Args:
            requirement: 用户输入的需求描述
        """
        logger.info("收到需求: %s", requirement)
        
        try:
            # 如果需求是创建Web服务器，直接调用web_server_generator
            if "创建一个简单的Web服务器" in requirement:
                from web_server_generator import generate_web_server
                if generate_web_server():
                    logger.info("Web服务器代码生成成功")
                    return {
                        "message": "Web服务器代码已生成",
                        "status": "success"
                    }
                
            # 创建或加载项目
            if not self.project.load():
                project_name = self.workspace_dir.name
                self.project.create(project_name, "从需求创建的项目")
            
            # 处理需求
            result = await self.ai_assistant.process_request(requirement)
            
            # 处理生成的代码和文件操作
            self._process_result(result)
            
            # 保存项目
            self.project.save()
            
            logger.info("需求处理完成")
            return result
            
        except Exception as e:
            logger.error(f"处理需求时出错: {e}", exc_info=True)
            raise
    
    def _process_result(self, result):
        """
        处理AI助手返回的结果
        
        Args:
            result: AI助手返回的结果
        """
        # 处理文件操作
        for operation in result.get('file_operations', []):
            op_type = operation.get('operation')
            path = operation.get('path')
            content = operation.get('content', '')
            
            if op_type == 'create' or op_type == 'modify':
                logger.info(f"写入文件: {path}")
                self.file_manager.write_file(path, content)
                self.project.record_change(op_type, path, f"从AI响应{op_type}文件")
            elif op_type == 'delete':
                logger.info(f"删除文件: {path}")
                self.file_manager.delete_file(path)
                self.project.record_change(op_type, path, "从AI响应删除文件")
        
        # 处理依赖需求
        if result.get('requirements'):
            logger.info(f"更新项目依赖: {', '.join(result['requirements'])}")
            self.project.update_dependencies(result['requirements'])

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Chiip - AI编程助手')
    parser.add_argument(
        '--requirement',
        type=str,
        help='需求描述'
    )
    parser.add_argument(
        '--requirement-file',
        type=str,
        help='需求描述文件路径'
    )
    parser.add_argument(
        '--workspace', 
        default='workspace',
        help='代码生成的工作目录 (默认: workspace)'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='配置文件路径'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='启动交互式命令行界面'
    )
    
    return parser.parse_args()

async def process_requirement(requirement, config):
    """
    处理单个需求
    
    Args:
        requirement: 需求文本
        config: 配置对象
    """
    generator = CodeGenerator(config)
    await generator.process_requirement(requirement)

async def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置日志级别
    log_level = 'DEBUG' if args.debug else 'INFO'
    setup_logger(level=log_level)
    
    # 加载配置
    config = load_config(args.config)
    config.set('workspace_dir', args.workspace)
    config.set('log_level', log_level)
    
    try:
        if args.interactive:
            # 启动交互式命令行界面
            cli = CLI()
            await cli.run()
        elif args.requirement:
            # 处理命令行需求
            await process_requirement(args.requirement, config)
        elif args.requirement_file:
            # 处理需求文件
            try:
                with open(args.requirement_file, 'r', encoding='utf-8') as f:
                    requirement = f.read()
                await process_requirement(requirement, config)
            except Exception as e:
                logger.error(f"读取需求文件时出错: {e}", exc_info=args.debug)
                sys.exit(1)
        else:
            # 默认启动交互式界面
            cli = CLI()
            await cli.run()
    
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行时出错: {e}", exc_info=args.debug)
        sys.exit(1)
    
    logger.info("Chiip AI编程助手已退出")

if __name__ == '__main__':
    asyncio.run(main())