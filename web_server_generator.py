# Copyright: (c) OpenChiip Organization. https://github.com/OpenChiip/Chiip
# Copyright: (c) <aigc@openchiip.com>
# Generated model: Qwen2.5-coder
# Released under the AIGCGPL-1.0 License.

"""
Web服务器生成器
负责生成简单的Web服务器代码
"""
from file_manager import FileManager
import logging

logger = logging.getLogger(__name__)

def generate_web_server():
    """
    生成简单的Web服务器代码
    """
    # 初始化文件管理器，指定workspace目录
    file_manager = FileManager('workspace')
    
    # 创建requirements.txt
    requirements_content = "Flask==3.0.0"
    if file_manager.create_file('requirements.txt', requirements_content):
        logger.info("成功创建requirements.txt")
    
    # 创建app.py
    app_content = '''from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)
'''
    if file_manager.create_file('app.py', app_content):
        logger.info("成功创建app.py")

    return True

if __name__ == '__main__':
    generate_web_server()