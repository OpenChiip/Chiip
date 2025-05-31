# Chiip - AI编程助手

Chiip是一个强大的AI编程助手工具，旨在通过AI技术辅助开发者完成编程任务。它能够理解自然语言需求，并生成相应的代码实现。

## 主要特性

- 🤖 **AI驱动**：利用先进的AI模型理解和处理编程需求
- 💻 **交互式界面**：提供友好的命令行交互界面
- � **多种输入方式**：支持直接输入需求或从文件读取需求
- � **项目管理**：自动管理生成的代码文件和项目结构
- 🛠️ **可配置**：支持自定义配置以适应不同的开发需求

## 安装指南

### 系统要求

- Python 3.9+
- Git（用于版本控制）

### 安装步骤

1. 克隆项目仓库：
```bash
git clone https://github.com/OpenChiip/Chiip.git
cd Chiip
```

2. 创建并激活虚拟环境（可选但推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用说明

### 命令行参数

```bash
python main.py [选项]

选项：
  --requirement TEXT        直接输入需求描述
  --requirement-file PATH   从文件读取需求描述
  --workspace PATH         指定工作目录（默认：workspace）
  --config PATH           指定配置文件路径
  --debug                启用调试模式
  --interactive          启动交互式命令行界面
```

### 交互式模式

启动交互式模式：
```bash
python main.py --interactive
```

### 使用示例

1. 直接处理需求：
```bash
python main.py --requirement "创建一个简单的Web服务器"
```

2. 从文件读取需求：
```bash
python main.py --requirement-file requirements.txt
```

3. 指定工作目录：
```bash
python main.py --workspace my_project --interactive
```

## 项目结构

```
.
├── ai_interface.py      # AI接口实现
├── cli.py              # 命令行界面
├── config.py           # 配置管理
├── file_manager.py     # 文件操作管理
├── generator.py        # 代码生成器
├── main.py            # 主程序入口
├── parser.py          # 需求解析器
├── project.py         # 项目管理
├── prompts.py         # AI提示模板
└── utils/             # 工具函数
    ├── logger.py      # 日志工具
    ├── text_processing.py  # 文本处理
    └── validation.py  # 输入验证
```

### 主要模块说明

- **ai_interface.py**: 实现与AI模型的交互
- **cli.py**: 提供交互式命令行界面
- **config.py**: 管理配置信息
- **file_manager.py**: 处理文件操作
- **generator.py**: 负责代码生成
- **project.py**: 管理项目结构和依赖

## 贡献指南

我们欢迎所有形式的贡献，包括但不限于：

- 提交问题和建议
- 改进文档
- 提交代码修复或新功能
- 分享使用经验

### 代码规范

- 遵循PEP 8 Python代码风格指南
- 提供适当的文档字符串
- 确保代码通过现有测试
- 为新功能添加测试用例

## 许可证

本项目采用 AIGCGPL-1.0 许可证。详情请参见 [LICENSE](LICENSE) 文件。

## 版权信息

Copyright: (c) OpenChiip Organization. https://github.com/OpenChiip/Chiip
Copyright: (c) <aigc@openchiip.com>

---

更多信息和更新，请访问我们的 [GitHub仓库](https://github.com/OpenChiip/Chiip)。