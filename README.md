# Chiip - AI编程助手

Chiip是一个强大的AI编程助手工具，它提供了交互式命令行界面，能够帮助开发者完成各种编程任务。

## 功能特点

- 🤖 智能AI对话：支持与AI助手进行自然语言交互
- 💻 代码生成：自动生成代码片段和完整程序
- 📁 文件操作：支持创建、修改和管理项目文件
- 🔧 灵活配置：支持自定义AI模型、工作目录等配置
- 🎨 美观界面：使用Rich库提供清晰的终端输出展示

## 系统要求

- Python 3.7+
- 相关依赖包（见requirements.txt）

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行程序：
```bash
python main.py
```

## 使用说明

### 基本命令
- 直接输入编程需求进行对话
- `/help` - 显示帮助信息
- `/clear` - 清除对话历史
- `/config` - 显示当前配置
- `/set <key> <value>` - 设置配置项
- `exit` 或 `Ctrl+C` 两次 - 退出程序

### 示例需求
- 创建一个简单的Web服务器
- 编写一个文件处理函数
- 实现数据库连接模块

## 项目结构

```
├── ai_interface.py    # AI模型接口实现
├── cli.py            # 命令行界面
├── config.py         # 配置管理
├── file_manager.py   # 文件管理
├── generator.py      # 代码生成器
├── main.py          # 主程序入口
├── parser.py        # 解析器
├── project.py       # 项目管理
├── prompts.py       # 提示词管理
├── utils/           # 工具函数
│   ├── logger.py    # 日志工具
│   ├── text_processing.py  # 文本处理
│   └── validation.py      # 验证工具
```

## 配置说明

支持通过命令行参数或配置文件进行配置：

- `--config` - 指定配置文件路径
- `--workspace` - 设置工作目录
- `--log-level` - 设置日志级别
- `--log-file` - 设置日志文件路径

## 开发说明

项目使用模块化设计，主要组件包括：

- AI接口模块：支持本地模型和API型模型
- 命令行界面：提供交互式操作体验
- 配置管理：灵活的配置系统
- 工具模块：提供日志、文本处理等功能

## 许可证

[许可证信息待补充]