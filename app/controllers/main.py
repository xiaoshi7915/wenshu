#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主控制器，提供Web页面
"""

import os
import logging
from flask import Blueprint, render_template, send_from_directory

# 创建蓝图
main_bp = Blueprint('main', __name__)

# 获取日志记录器
logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    """
    首页
    """
    return render_template('index.html')

@main_bp.route('/favicon.ico')
def favicon():
    """
    网站图标
    """
    return send_from_directory(
        os.path.join(main_bp.root_path, '../static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    ) 