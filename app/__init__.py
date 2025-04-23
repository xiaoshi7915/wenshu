#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WenShu应用程序初始化文件
"""

import os
import logging
from flask import Flask
from flask_cors import CORS

def create_app():
    """
    创建并配置Flask应用
    """
    # 创建Flask应用
    app = Flask(__name__)
    
    # 从环境变量加载配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
    
    # 配置Jinja2模板引擎
    app.jinja_env.autoescape = True
    
    # 配置日志
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 启用CORS
    CORS(app)
    
    # 注册蓝图
    from app.controllers.main import main_bp
    from app.controllers.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 返回应用实例
    return app 