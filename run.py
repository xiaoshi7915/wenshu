#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WenShu应用程序入口文件
"""

import os
from dotenv import load_dotenv
from app import create_app

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = create_app()

if __name__ == '__main__':
    # 获取环境变量中的端口，如果没有则使用默认值5043
    port = int(os.environ.get('PORT', 5043))
    
    # 如果是开发环境，则开启debug模式
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # 启动应用
    app.run(host='0.0.0.0', port=port, debug=debug) 