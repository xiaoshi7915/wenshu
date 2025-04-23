#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API控制器，提供REST API接口
"""

import json
import logging
from flask import Blueprint, request, jsonify
from app.services.query_service import QueryService

# 创建蓝图
api_bp = Blueprint('api', __name__)

# 获取日志记录器
logger = logging.getLogger(__name__)

# 创建查询服务实例
query_service = QueryService()

@api_bp.route('/connect', methods=['POST'])
def connect_database():
    """
    连接数据库API
    
    请求体格式:
    {
        "db_type": "mysql",
        "host": "localhost",
        "user": "root",
        "password": "password",
        "database": "my_database",
        "port": 3306
    }
    """
    try:
        # 获取请求数据
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "缺少请求数据"
            }), 400
        
        # 提取连接参数
        db_type = data.get('db_type')
        connection_params = {
            'host': data.get('host'),
            'user': data.get('user'),
            'password': data.get('password'),
            'database': data.get('database'),
            'port': data.get('port')
        }
        
        # 验证必要参数
        if not db_type:
            return jsonify({
                "status": "error",
                "message": "缺少必要参数: db_type"
            }), 400
        
        if not connection_params['host'] or not connection_params['user'] or not connection_params['database']:
            return jsonify({
                "status": "error",
                "message": "缺少必要参数: host, user, database"
            }), 400
        
        # 连接数据库
        result = query_service.connect_database(db_type, **connection_params)
        
        # 根据结果返回响应
        if result.get('status') == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"连接数据库API错误: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"处理请求时出错: {str(e)}"
        }), 500

@api_bp.route('/query', methods=['POST'])
def process_query():
    """
    处理自然语言查询API
    
    请求体格式:
    {
        "connection_id": "mysql_localhost_my_database",
        "query": "查询所有用户",
        "conversation_history": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }
    """
    try:
        # 获取请求数据
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "缺少请求数据"
            }), 400
        
        # 提取参数
        connection_id = data.get('connection_id')
        query = data.get('query')
        conversation_history = data.get('conversation_history')
        
        # 验证必要参数
        if not connection_id:
            return jsonify({
                "status": "error",
                "message": "缺少必要参数: connection_id"
            }), 400
        
        if not query:
            return jsonify({
                "status": "error",
                "message": "缺少必要参数: query"
            }), 400
        
        # 处理查询
        result = query_service.process_query(
            connection_id=connection_id,
            query=query,
            conversation_history=conversation_history
        )
        
        # 根据结果返回响应
        if result.get('status') == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"处理查询API错误: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"处理请求时出错: {str(e)}"
        }), 500

@api_bp.route('/execute', methods=['POST'])
def execute_sql():
    """
    直接执行SQL语句API
    
    请求体格式:
    {
        "connection_id": "mysql_localhost_my_database",
        "sql": "SELECT * FROM users LIMIT 10"
    }
    """
    try:
        # 获取请求数据
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "缺少请求数据"
            }), 400
        
        # 提取参数
        connection_id = data.get('connection_id')
        sql = data.get('sql')
        
        # 验证必要参数
        if not connection_id:
            return jsonify({
                "status": "error",
                "message": "缺少必要参数: connection_id"
            }), 400
        
        if not sql:
            return jsonify({
                "status": "error",
                "message": "缺少必要参数: sql"
            }), 400
        
        # 执行SQL
        result = query_service.execute_sql(
            connection_id=connection_id,
            sql=sql
        )
        
        # 根据结果返回响应
        if result.get('status') == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"执行SQL API错误: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"处理请求时出错: {str(e)}"
        }), 500

@api_bp.route('/disconnect', methods=['POST'])
def disconnect_database():
    """
    断开数据库连接API
    
    请求体格式:
    {
        "connection_id": "mysql_localhost_my_database"
    }
    """
    try:
        # 获取请求数据
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "缺少请求数据"
            }), 400
        
        # 提取参数
        connection_id = data.get('connection_id')
        
        # 验证必要参数
        if not connection_id:
            return jsonify({
                "status": "error",
                "message": "缺少必要参数: connection_id"
            }), 400
        
        # 断开连接
        result = query_service.disconnect_database(connection_id)
        
        # 根据结果返回响应
        if result.get('status') in ['success', 'warning']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"断开连接API错误: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"处理请求时出错: {str(e)}"
        }), 500 