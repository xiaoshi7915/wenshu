#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MySQL数据库MCP服务器实现
"""

import json
import logging
import pandas as pd
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.exc import SQLAlchemyError

class MySQLMCPServer:
    """MySQL MCP服务器类，实现MCP协议与MySQL数据库的交互"""
    
    def __init__(self, host, user, password, database, port=3306):
        """
        初始化MySQL MCP服务器
        
        Args:
            host (str): 数据库主机地址
            user (str): 数据库用户名
            password (str): 数据库密码
            database (str): 数据库名称
            port (int, optional): 数据库端口. 默认为3306.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.engine = None
        self.logger = logging.getLogger(__name__)
        
        # 连接到MySQL数据库
        self._connect()
        
    def _connect(self):
        """建立与MySQL数据库的连接"""
        try:
            # 创建SQLAlchemy引擎，使用mysql-connector-python
            connection_string = f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            self.engine = create_engine(connection_string)
            self.logger.info(f"成功连接到MySQL数据库: {self.host}:{self.port}/{self.database}")
        except SQLAlchemyError as e:
            self.logger.error(f"连接MySQL数据库失败: {str(e)}")
            raise

    # MCP工具函数 - 获取数据库元数据
    def get_database_metadata(self):
        """
        获取数据库的元数据信息，包括表名、列名、注释等
        
        Returns:
            str: 格式化的元数据信息
        """
        try:
            # 获取SQLAlchemy元数据对象
            metadata = {}
            inspector = inspect(self.engine)
            
            # 获取所有表名
            table_names = inspector.get_table_names()
            metadata["tables"] = []
            
            # 为每个表获取列信息
            for table_name in table_names:
                table_info = {"name": table_name, "columns": []}
                
                # 获取主键
                primary_keys = inspector.get_pk_constraint(table_name).get('constrained_columns', [])
                
                # 获取外键
                foreign_keys = []
                for fk in inspector.get_foreign_keys(table_name):
                    for col in fk['constrained_columns']:
                        foreign_keys.append({
                            'column': col, 
                            'references': {
                                'table': fk['referred_table'], 
                                'column': fk['referred_columns'][0]
                            }
                        })
                
                # 获取索引
                indices = inspector.get_indexes(table_name)
                
                # 获取列信息
                columns = inspector.get_columns(table_name)
                for column in columns:
                    col_name = column['name']
                    col_info = {
                        "name": col_name,
                        "type": str(column['type']),
                        "nullable": column.get('nullable', True),
                        "default": str(column.get('default', '')),
                        "is_primary": col_name in primary_keys
                    }
                    
                    # 添加外键信息
                    for fk in foreign_keys:
                        if fk['column'] == col_name:
                            col_info['foreign_key'] = fk['references']
                    
                    # 添加注释信息（如果有）
                    try:
                        comment_query = text(
                            f"SELECT COLUMN_COMMENT FROM INFORMATION_SCHEMA.COLUMNS "
                            f"WHERE TABLE_SCHEMA = '{self.database}' AND TABLE_NAME = '{table_name}' "
                            f"AND COLUMN_NAME = '{col_name}'"
                        )
                        with self.engine.connect() as conn:
                            result = conn.execute(comment_query).fetchone()
                            if result and result[0]:
                                col_info['comment'] = result[0]
                    except Exception as e:
                        self.logger.warning(f"获取列注释失败: {str(e)}")
                    
                    table_info["columns"].append(col_info)
                
                # 添加表注释信息（如果有）
                try:
                    comment_query = text(
                        f"SELECT TABLE_COMMENT FROM INFORMATION_SCHEMA.TABLES "
                        f"WHERE TABLE_SCHEMA = '{self.database}' AND TABLE_NAME = '{table_name}'"
                    )
                    with self.engine.connect() as conn:
                        result = conn.execute(comment_query).fetchone()
                        if result and result[0]:
                            table_info['comment'] = result[0]
                except Exception as e:
                    self.logger.warning(f"获取表注释失败: {str(e)}")
                
                metadata["tables"].append(table_info)
            
            return json.dumps(metadata, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"获取数据库元数据失败: {str(e)}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # MCP工具函数 - 获取样本数据
    def get_sample_data(self, limit=3):
        """
        获取每个表的样本数据
        
        Args:
            limit (int, optional): 每个表返回的样本数据数量. 默认为3.
            
        Returns:
            str: 包含所有表样本数据的JSON字符串
        """
        try:
            # 获取所有表名
            inspector = inspect(self.engine)
            table_names = inspector.get_table_names()
            
            sample_data = {}
            
            # 为每个表获取样本数据
            for table_name in table_names:
                query = text(f"SELECT * FROM `{table_name}` LIMIT {limit}")
                
                with self.engine.connect() as conn:
                    result = conn.execute(query)
                    columns = result.keys()
                    rows = []
                    
                    for row in result:
                        rows.append(dict(zip(columns, row)))
                    
                    sample_data[table_name] = rows
            
            return json.dumps(sample_data, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"获取样本数据失败: {str(e)}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # MCP工具函数 - 执行只读SQL查询
    def execute_readonly_query(self, query, max_rows=100):
        """
        在只读事务中执行SQL查询
        
        Args:
            query (str): 要执行的SQL查询语句
            max_rows (int, optional): 返回的最大行数. 默认为100.
            
        Returns:
            str: 查询结果的JSON字符串
        """
        try:
            # 检查SQL语句是否为只读
            if not self._is_readonly_query(query):
                error_msg = "不允许执行修改数据的SQL语句"
                self.logger.warning(f"尝试执行非只读查询: {query}")
                return json.dumps({"error": error_msg}, ensure_ascii=False)
            
            # 执行查询
            with self.engine.connect() as conn:
                # 开启只读事务
                with conn.begin():
                    # 执行查询
                    result = conn.execute(text(query))
                    columns = result.keys()
                    
                    # 获取结果
                    rows = []
                    for idx, row in enumerate(result):
                        if idx >= max_rows:
                            break
                        rows.append(dict(zip(columns, row)))
                    
                    # 构建结果
                    result_data = {
                        "columns": list(columns),
                        "rows": rows,
                        "rowCount": len(rows),
                        "truncated": result.rowcount > max_rows if result.rowcount >= 0 else False
                    }
                    
                    # 如果结果可以被Pandas处理，尝试添加基本的统计信息
                    if len(rows) > 0:
                        try:
                            df = pd.DataFrame(rows)
                            numeric_columns = df.select_dtypes(include=['number']).columns
                            
                            if not numeric_columns.empty:
                                result_data["statistics"] = {}
                                for col in numeric_columns:
                                    result_data["statistics"][col] = {
                                        "min": float(df[col].min()) if not df[col].isnull().all() else None,
                                        "max": float(df[col].max()) if not df[col].isnull().all() else None,
                                        "mean": float(df[col].mean()) if not df[col].isnull().all() else None,
                                        "null_count": int(df[col].isnull().sum())
                                    }
                        except Exception as e:
                            self.logger.warning(f"生成统计信息失败: {str(e)}")
                    
                    return json.dumps(result_data, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"执行查询失败: {str(e)}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    def _is_readonly_query(self, query):
        """
        检查SQL查询是否为只读查询
        
        Args:
            query (str): SQL查询语句
            
        Returns:
            bool: 如果是只读查询返回True，否则返回False
        """
        # 转换为小写以便进行不区分大小写的比较
        query_lower = query.lower().strip()
        
        # 定义可能修改数据的SQL关键字
        modifying_keywords = [
            'insert', 'update', 'delete', 'drop', 'alter', 'create', 
            'truncate', 'replace', 'rename', 'grant', 'revoke'
        ]
        
        # 检查查询是否以这些关键字开头
        for keyword in modifying_keywords:
            if query_lower.startswith(keyword):
                return False
            
            # 也检查是否在查询中间包含这些关键字（可能是多语句查询）
            if f"; {keyword} " in query_lower:
                return False
        
        return True 