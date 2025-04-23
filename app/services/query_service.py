#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
查询服务，集成LLM服务与MCP服务
"""

import json
import logging
import traceback
from app.services.llm_service import LLMService
from app.mcp import MCPServerFactory

class QueryService:
    """
    查询服务，负责协调自然语言查询处理过程
    """
    
    def __init__(self):
        """初始化查询服务"""
        self.logger = logging.getLogger(__name__)
        self.llm_service = LLMService()
        self.mcp_servers = {}  # 存储已连接的MCP服务器实例
    
    def connect_database(self, db_type, **connection_params):
        """
        连接到指定的数据库
        
        Args:
            db_type (str): 数据库类型
            **connection_params: 连接参数
            
        Returns:
            dict: 连接结果
        """
        try:
            # 生成连接ID
            connection_id = f"{db_type}_{connection_params.get('host')}_{connection_params.get('database')}"
            
            # 创建MCP服务器实例
            mcp_server = MCPServerFactory.create_server(db_type, **connection_params)
            
            # 存储MCP服务器实例
            self.mcp_servers[connection_id] = mcp_server
            
            # 获取元数据
            metadata_str = mcp_server.get_database_metadata()
            metadata = json.loads(metadata_str)
            
            # 获取样本数据
            sample_data_str = mcp_server.get_sample_data(limit=3)
            sample_data = json.loads(sample_data_str)
            
            return {
                "status": "success",
                "connection_id": connection_id,
                "message": f"成功连接到 {db_type} 数据库",
                "metadata": metadata,
                "sample_data": sample_data
            }
        except Exception as e:
            self.logger.error(f"连接数据库失败: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"连接数据库失败: {str(e)}"
            }
    
    def process_query(self, connection_id, query, conversation_history=None):
        """
        处理自然语言查询
        
        Args:
            connection_id (str): 数据库连接ID
            query (str): 用户的自然语言查询
            conversation_history (list, optional): 对话历史
            
        Returns:
            dict: 查询结果
        """
        try:
            # 检查连接是否存在
            if connection_id not in self.mcp_servers:
                return {
                    "status": "error",
                    "message": f"未找到连接ID: {connection_id}，请先连接数据库"
                }
            
            # 获取MCP服务器实例
            mcp_server = self.mcp_servers[connection_id]
            
            # 获取元数据
            metadata_str = mcp_server.get_database_metadata()
            metadata = json.loads(metadata_str)
            
            # 获取样本数据
            sample_data_str = mcp_server.get_sample_data(limit=3)
            sample_data = json.loads(sample_data_str)
            
            # 调用LLM服务转换自然语言为SQL
            llm_response = self.llm_service.natural_language_to_sql(
                query=query,
                metadata=metadata,
                sample_data=sample_data,
                conversation_history=conversation_history
            )
            
            # 检查是否成功生成SQL
            if "error" in llm_response:
                return {
                    "status": "error",
                    "message": llm_response["error"],
                    "query": query,
                    "explanation": llm_response.get("explanation")
                }
            
            sql = llm_response.get("sql")
            explanation = llm_response.get("explanation")
            
            if not sql:
                return {
                    "status": "error",
                    "message": "无法从LLM响应中提取SQL语句",
                    "query": query,
                    "explanation": explanation
                }
            
            # 执行SQL查询
            results_str = mcp_server.execute_readonly_query(sql)
            results = json.loads(results_str)
            
            # 检查执行结果是否有错误
            if "error" in results:
                # 尝试修正SQL
                revised_response = self.llm_service.revise_sql(
                    original_sql=sql,
                    error_message=results["error"],
                    metadata=metadata,
                    sample_data=sample_data,
                    user_query=query
                )
                
                revised_sql = revised_response.get("sql")
                revised_explanation = revised_response.get("explanation")
                
                if revised_sql and revised_sql != sql:
                    # 执行修正后的SQL
                    revised_results_str = mcp_server.execute_readonly_query(revised_sql)
                    revised_results = json.loads(revised_results_str)
                    
                    # 如果修正后的SQL执行成功
                    if "error" not in revised_results:
                        # 解释结果
                        result_explanation = self.llm_service.explain_results(
                            query=query,
                            sql=revised_sql,
                            results=revised_results,
                            metadata=metadata
                        )
                        
                        return {
                            "status": "success",
                            "message": "查询执行成功（已修正SQL）",
                            "query": query,
                            "original_sql": sql,
                            "sql": revised_sql,
                            "results": revised_results,
                            "original_explanation": explanation,
                            "explanation": revised_explanation,
                            "result_explanation": result_explanation,
                            "revised": True
                        }
                
                # 如果无法修正SQL或修正后仍有错误
                return {
                    "status": "error",
                    "message": f"SQL执行失败: {results.get('error')}",
                    "query": query,
                    "sql": sql,
                    "explanation": explanation,
                    "revised_sql": revised_sql,
                    "revised_explanation": revised_explanation
                }
            
            # 解释结果
            result_explanation = self.llm_service.explain_results(
                query=query,
                sql=sql,
                results=results,
                metadata=metadata
            )
            
            # 返回成功结果
            return {
                "status": "success",
                "message": "查询执行成功",
                "query": query,
                "sql": sql,
                "results": results,
                "explanation": explanation,
                "result_explanation": result_explanation,
                "revised": False
            }
            
        except Exception as e:
            self.logger.error(f"处理查询失败: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"处理查询失败: {str(e)}",
                "query": query
            }
    
    def execute_sql(self, connection_id, sql):
        """
        直接执行SQL语句
        
        Args:
            connection_id (str): 数据库连接ID
            sql (str): SQL语句
            
        Returns:
            dict: 执行结果
        """
        try:
            # 检查连接是否存在
            if connection_id not in self.mcp_servers:
                return {
                    "status": "error",
                    "message": f"未找到连接ID: {connection_id}，请先连接数据库"
                }
            
            # 获取MCP服务器实例
            mcp_server = self.mcp_servers[connection_id]
            
            # 执行SQL查询
            results_str = mcp_server.execute_readonly_query(sql)
            results = json.loads(results_str)
            
            # 检查执行结果是否有错误
            if "error" in results:
                return {
                    "status": "error",
                    "message": f"SQL执行失败: {results.get('error')}",
                    "sql": sql
                }
            
            # 返回成功结果
            return {
                "status": "success",
                "message": "SQL执行成功",
                "sql": sql,
                "results": results
            }
            
        except Exception as e:
            self.logger.error(f"执行SQL失败: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"执行SQL失败: {str(e)}",
                "sql": sql
            }
    
    def disconnect_database(self, connection_id):
        """
        断开数据库连接
        
        Args:
            connection_id (str): 数据库连接ID
            
        Returns:
            dict: 断开连接结果
        """
        try:
            # 检查连接是否存在
            if connection_id not in self.mcp_servers:
                return {
                    "status": "warning",
                    "message": f"未找到连接ID: {connection_id}"
                }
            
            # 移除MCP服务器实例
            del self.mcp_servers[connection_id]
            
            return {
                "status": "success",
                "message": f"已断开连接: {connection_id}"
            }
            
        except Exception as e:
            self.logger.error(f"断开连接失败: {str(e)}")
            return {
                "status": "error",
                "message": f"断开连接失败: {str(e)}"
            } 