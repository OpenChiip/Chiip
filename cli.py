# Copyright: (c) OpenChiip Organization. https://github.com/OpenChiip/Chiip
# Copyright: (c) <aigc@openchiip.com>
# Generated model: Qwen2.5-coder
# Released under the AIGCGPL-1.0 License.

"""
命令行界面模块，提供交互式命令行界面
"""
import argparse
import asyncio
import logging
import os
import sys
import json
import subprocess
from typing import Dict, Any
from file_manager import FileManager
from pathlib import Path
from typing import Optional, List, Dict, Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.table import Table

from ai_interface import AIAssistant
from config import Config, load_config
from utils import setup_logger, process_json_string

logger = logging.getLogger(__name__)
console = Console()

class CLI:
    """命令行界面类"""
    
    def __init__(self):
        """初始化命令行界面"""
        self.config = self._load_config()
        self.assistant = AIAssistant(self.config)
        
        # 获取工作目录
        workspace_dir = self.config.get('workspace_dir', 'workspace')
        if not Path(workspace_dir).exists():
            Path(workspace_dir).mkdir(parents=True)
            
        self.file_manager = FileManager(str(workspace_dir))
        
        # 设置日志
        log_level = self.config.get('log_level', 'INFO')
        log_file = self.config.get('log_file')
        setup_logger(level=log_level, log_file=log_file)
    
    def _load_config(self) -> Config:
        """
        加载配置
        
        Returns:
            Config: 配置管理器实例
        """
        parser = argparse.ArgumentParser(description='Chiip - AI编程助手')
        parser.add_argument(
            '--config',
            type=str,
            help='配置文件路径'
        )
        parser.add_argument(
            '--workspace',
            type=str,
            help='工作目录路径'
        )
        parser.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            help='日志级别'
        )
        parser.add_argument(
            '--log-file',
            type=str,
            help='日志文件路径'
        )
        
        args = parser.parse_args()
        
        # 加载配置文件
        config = load_config(args.config)
        
        # 命令行参数覆盖配置文件
        if args.workspace:
            config.set('workspace_dir', args.workspace)
        if args.log_level:
            config.set('log_level', args.log_level)
        if args.log_file:
            config.set('log_file', args.log_file)
        
        return config
    
    async def run(self) -> None:
        """运行命令行界面"""
        self._print_welcome()
        
        while True:
            try:
                # 获取用户输入
                request = self._get_user_input()
                
                # 检查退出命令
                if request.lower() in ['exit', 'quit', 'q']:
                    break
                
                # 处理特殊命令
                if request.startswith('/'):
                    self._handle_command(request[1:])
                    continue
                
                # 处理正常请求
                await self._handle_request(request)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]按Ctrl+C再次退出程序[/yellow]")
                try:
                    input()
                    continue
                except KeyboardInterrupt:
                    break
            except Exception as e:
                logger.error(f"处理请求时出错: {e}", exc_info=True)
                console.print(f"[red]错误: {e}[/red]")
    
    def _print_welcome(self) -> None:
        """打印欢迎信息"""
        welcome_text = """
# Chiip AI编程助手

## 使用说明
- 直接输入您的编程需求
- 使用 /help 查看帮助
- 使用 /clear 清除对话历史
- 使用 exit 或 Ctrl+C 退出

## 示例需求
- 创建一个简单的Web服务器
- 编写一个文件处理函数
- 实现数据库连接模块
        """
        
        console.print(Markdown(welcome_text))
        console.print("\n当前工作目录:", self.config.get('workspace_dir'))
        console.print("=" * 50 + "\n")
    
    def _get_user_input(self) -> str:
        """
        获取用户输入
        
        Returns:
            str: 用户输入的内容
        """
        return Prompt.ask("\n[bold green]Chiip AI 助手=>请输入您的需求[/bold green]")
    
    def _handle_command(self, command: str) -> None:
        """
        处理特殊命令
        
        Args:
            command: 命令内容（不包含前导斜杠）
        """
        command = command.lower().strip()
        
        if command == 'help':
            self._show_help()
        elif command == 'clear':
            self.assistant.clear_conversation()
            console.print("[green]已清除对话历史[/green]")
        elif command == 'config':
            self._show_config()
        elif command.startswith('set '):
            self._handle_set_command(command[4:])
        else:
            console.print(f"[red]未知命令: {command}[/red]")
    
    async def _handle_request(self, request: str) -> None:
        """
        处理用户请求
        
        Args:
            request: 用户请求内容
        """
        with console.status("[bold yellow]思考中...[/bold yellow]"):
            try:
                # 处理请求
                result = await self.assistant.process_request(request)

                # 显示响应
                self._display_result(result)

                # 解析 JSON 响应
                processed_json = process_json_string(result['response'])
                result_json = json.loads(processed_json)

                # 创建工作目录（使用项目ID作为目录名）
                workspace_dir = os.path.join('workspace', result_json['id'])
                if not os.path.exists(workspace_dir):
                    os.makedirs(workspace_dir)
                
                # 切换到工作目录
                original_dir = os.getcwd()
                os.chdir(workspace_dir)
                
                print(f"\nInitializing project: {result_json['title']} ({result_json['id']})")
                print(f"Working directory: {workspace_dir}")
                
                try:
                    # 遍历所有项目
                    for project in result_json['artifact']:
                        print(f"\nProcessing {project['type']} project: {project['name']} ({project['id']})")
                        
                        # 遍历项目中的所有操作
                        for action in project['actions']:
                            if action['type'] == 'file':
                                try:
                                    # 创建文件
                                    # 确保目录存在
                                    file_path = action['filePath']
                                    directory = os.path.dirname(file_path)
                                    if directory and not os.path.exists(directory):
                                        os.makedirs(directory)
                                    
                                    # 使用 file_manager 创建文件
                                    self.file_manager.create_file(file_path, action['content'])
                                    print(f"Created file: {file_path}")
                                except Exception as e:
                                    print(f"Error creating file {file_path}: {e}")
                                    raise
                            
                            elif action['type'] == 'shell':
                                # 执行 shell 命令
                                command = action['command']
                                print(f"Executing command: {command}")
                                try:
                                    result = subprocess.run(command, shell=True, check=True, 
                                                        capture_output=True, text=True)
                                    if result.stdout:
                                        print(f"Command output:\n{result.stdout}")
                                except subprocess.CalledProcessError as e:
                                    print(f"Error executing command: {e}")
                                    if e.output:
                                        print(f"Command output:\n{e.output}")
                                    if e.stderr:
                                        print(f"Command error:\n{e.stderr}")
                                    raise
                    
                    print(f"\nProject {result_json['title']} setup completed successfully!")
                    
                finally:
                    # 恢复原始工作目录
                    os.chdir(original_dir)
        
                
            except Exception as e:
                logger.error(f"处理请求时出错: {e}", exc_info=True)
                console.print(f"[red]处理请求时出错: {e}[/red]")
    
    def _display_result(self, result: Dict[str, Any]) -> None:
        """
        显示处理结果
        
        Args:
            result: 处理结果
        """
        # 显示原始响应
        console.print("\n[bold]AI响应:[/bold]")
        console.print(result['response'])
        
        # 显示代码块
        # if result['code_blocks']:
        #     console.print("\n[bold]代码块:[/bold]")
        #     for block in result['code_blocks']:
        #         console.print(Panel(
        #             Syntax(
        #                 block['code'],
        #                 block['language'],
        #                 theme='monokai',
        #                 line_numbers=True
        #             ),
        #             title=f"[{block['language']}]"
        #         ))
        
        # 显示文件操作
        # if result['file_operations']:
        #     console.print("\n[bold]文件操作:[/bold]")
        #     table = Table(show_header=True)
        #     table.add_column("操作")
        #     table.add_column("文件路径")
            
        #     for op in result['file_operations']:
        #         table.add_row(
        #             op['operation'],
        #             op['path']
        #         )
            
        #     console.print(table)
        
        # 显示依赖需求
        # if result['requirements']:
        #     console.print("\n[bold]依赖需求:[/bold]")
        #     for req in result['requirements']:
        #         console.print(f"- {req}")
    
    def _show_help(self) -> None:
        """显示帮助信息"""
        help_text = """
# 命令帮助

## 基本命令
- /help: 显示此帮助信息
- /clear: 清除对话历史
- /config: 显示当前配置
- /set <key> <value>: 设置配置项

## 配置命令示例
- /set workspace_dir /path/to/workspace
- /set log_level DEBUG
- /set model.temperature 0.8

## 退出程序
- 输入 exit, quit 或 q
- 按两次 Ctrl+C
        """
        
        console.print(Markdown(help_text))
    
    def _show_config(self) -> None:
        """显示当前配置"""
        console.print("\n[bold]当前配置:[/bold]")
        
        table = Table(show_header=True)
        table.add_column("配置项")
        table.add_column("值")
        
        def add_config_rows(config: Dict[str, Any], prefix: str = ""):
            for key, value in config.items():
                full_key = f"{prefix}{key}" if prefix else key
                if isinstance(value, dict):
                    add_config_rows(value, f"{full_key}.")
                else:
                    table.add_row(full_key, str(value))
        
        add_config_rows(self.config.config)
        console.print(table)
    
    def _handle_set_command(self, command: str) -> None:
        """
        处理set命令
        
        Args:
            command: set命令的参数部分
        """
        try:
            key, value = command.strip().split(maxsplit=1)
            
            # 尝试转换为适当的类型
            try:
                # 尝试转换为数字
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                # 如果不是数字，检查是否是布尔值
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                # 否则保持字符串
            
            self.config.set(key, value)
            console.print(f"[green]已设置 {key} = {value}[/green]")
            
        except ValueError:
            console.print("[red]无效的set命令格式。使用: /set <key> <value>[/red]")

def main():
    """主函数"""
    cli = CLI()
    asyncio.run(cli.run())

if __name__ == '__main__':
    main()