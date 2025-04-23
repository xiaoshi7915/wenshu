#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM服务，处理自然语言到SQL的转换
"""

import os
import json
import logging
import requests
import anthropic
from anthropic import Anthropic
import time

class LLMService:
    """提供自然语言处理相关的服务"""
    
    def __init__(self):
        """初始化LLM服务"""
        self.logger = logging.getLogger(__name__)
        
        # 获取API密钥
        self.anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY')
        
        # 判断使用哪个LLM服务
        self.llm_provider = os.environ.get('LLM_PROVIDER', 'anthropic').lower()
        
        # 初始化客户端
        self.client = None
        if self.llm_provider == 'anthropic' and self.anthropic_api_key:
            self.client = Anthropic(api_key=self.anthropic_api_key)
            self.logger.info("已初始化Anthropic API客户端")
        elif self.llm_provider == 'deepseek' and self.deepseek_api_key:
            # DeepSeek使用REST API而不是SDK客户端
            self.deepseek_api_url = "https://api.deepseek.com/v1/chat/completions"
            self.logger.info("已初始化DeepSeek API客户端")
        else:
            self.logger.warning(f"未能初始化{self.llm_provider}客户端，请检查API密钥配置")
    
    def _generate_system_message(self, metadata, sample_data=None):
        """
        生成系统消息，用于指导LLM生成SQL
        
        Args:
            metadata (dict): 数据库元数据
            sample_data (dict, optional): 样本数据
            
        Returns:
            str: 系统消息
        """
        system_message = """你是一个专业的数据库查询助手，能够将自然语言转换为精确的SQL查询。
        
你的主要职责是：
1. 理解用户的自然语言查询意图
2. 根据提供的数据库结构生成符合语法的SQL查询
3. 解释SQL查询的逻辑和预期结果

生成SQL时应遵循以下原则：
- 仅使用SELECT语句进行查询，不执行任何修改数据的操作
- 确保SQL语法正确，考虑表关系和字段类型
- 优先使用表的主键或索引字段进行JOIN和WHERE条件
- 对于复杂查询，添加注释说明查询逻辑
- 必要时使用子查询、GROUP BY、HAVING等高级功能
- 如果存在多种可能的理解，选择最合理的一种并说明原因

输出格式要求：
1. 首先给出生成的SQL语句，使用```sql ```代码块格式
2. 然后解释SQL语句的逻辑和预期结果
3. 如果无法生成SQL或需要更多信息，清晰说明原因

数据库结构信息如下：
"""
        
        # 添加表和字段信息
        if metadata and "tables" in metadata:
            for table in metadata["tables"]:
                table_name = table.get("name", "")
                table_comment = table.get("comment", "")
                
                # 添加表信息
                system_message += f"\n表名: {table_name}"
                if table_comment:
                    system_message += f" (说明: {table_comment})"
                system_message += "\n"
                
                # 添加字段信息
                if "columns" in table and table["columns"]:
                    system_message += "字段:\n"
                    for column in table["columns"]:
                        col_name = column.get("name", "")
                        col_type = column.get("type", "")
                        col_comment = column.get("comment", "")
                        is_pk = "是" if column.get("is_primary", False) else "否"
                        nullable = "可空" if column.get("nullable", True) else "非空"
                        
                        system_message += f"- {col_name} ({col_type}, {nullable}, 主键: {is_pk})"
                        if col_comment:
                            system_message += f" 说明: {col_comment}"
                        
                        # 如果有外键信息，添加外键说明
                        if "foreign_key" in column:
                            fk = column["foreign_key"]
                            system_message += f" 外键 -> {fk['table']}.{fk['column']}"
                        
                        system_message += "\n"
                
                system_message += "\n"
        
        # 如果有样本数据，添加样本数据
        if sample_data:
            system_message += "\n部分表的样本数据:\n"
            
            # 限制只显示前几个表的样本数据，避免系统消息过长
            sample_tables = list(sample_data.keys())[:3]
            
            for table_name in sample_tables:
                rows = sample_data.get(table_name, [])
                if not rows:
                    continue
                
                system_message += f"\n表 {table_name} 样本数据:\n"
                
                # 添加表头
                if rows:
                    columns = list(rows[0].keys())
                    system_message += "| " + " | ".join(columns) + " |\n"
                    system_message += "| " + " | ".join(["---" for _ in columns]) + " |\n"
                    
                    # 添加数据行
                    for row in rows:
                        system_message += "| " + " | ".join([str(row.get(col, "")) for col in columns]) + " |\n"
                
                system_message += "\n"
        
        return system_message

    def _call_anthropic_api(self, system, messages, max_tokens=2000, temperature=0.0):
        """
        调用Anthropic Claude API
        
        Args:
            system (str): 系统消息
            messages (list): 消息列表
            max_tokens (int): 最大token数
            temperature (float): 温度参数
            
        Returns:
            dict: API响应
        """
        if not self.client:
            raise ValueError("未初始化Anthropic客户端")
            
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            system=system,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.content[0].text
    
    def _call_deepseek_api(self, system, messages, max_tokens=2000, temperature=0.0):
        """
        调用DeepSeek API
        
        Args:
            system (str): 系统消息
            messages (list): 消息列表
            max_tokens (int): 最大token数
            temperature (float): 温度参数
            
        Returns:
            dict: API响应
        """
        if not self.deepseek_api_key:
            raise ValueError("未配置DeepSeek API密钥")
            
        # 格式化消息，包括系统消息
        formatted_messages = [{"role": "system", "content": system}]
        
        # 添加用户和助手的消息
        for message in messages:
            formatted_messages.append(message)
        
        # 准备请求体
        request_body = {
            "model": "deepseek-chat",  # 使用DeepSeek Chat模型
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # 发送请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.deepseek_api_key}"
        }
        
        response = requests.post(self.deepseek_api_url, headers=headers, json=request_body)
        
        # 检查响应
        if response.status_code != 200:
            raise Exception(f"DeepSeek API请求失败: {response.text}")
            
        response_data = response.json()
        if "choices" not in response_data or len(response_data["choices"]) == 0:
            raise Exception("DeepSeek API响应格式错误")
            
        return response_data["choices"][0]["message"]["content"]
        
    def _call_llm_api(self, system, messages, max_tokens=2000, temperature=0.0):
        """
        根据配置调用相应的LLM API
        
        Args:
            system (str): 系统消息
            messages (list): 消息列表
            max_tokens (int): 最大token数
            temperature (float): 温度参数
            
        Returns:
            str: 模型返回的文本
        """
        if self.llm_provider == 'anthropic' and self.client:
            return self._call_anthropic_api(system, messages, max_tokens, temperature)
        elif self.llm_provider == 'deepseek' and self.deepseek_api_key:
            return self._call_deepseek_api(system, messages, max_tokens, temperature)
        else:
            raise ValueError(f"不支持的LLM提供商: {self.llm_provider}")

    def natural_language_to_sql(self, query, metadata, sample_data=None, conversation_history=None):
        """
        将自然语言转换为SQL查询
        
        Args:
            query (str): 用户的自然语言查询
            metadata (dict): 数据库元数据
            sample_data (dict, optional): 样本数据
            conversation_history (list, optional): 对话历史
            
        Returns:
            dict: 包含生成的SQL和解释的字典
        """
        try:
            if (self.llm_provider == 'anthropic' and not self.anthropic_api_key) or (self.llm_provider == 'deepseek' and not self.deepseek_api_key):
                return {
                    "error": f"未配置{self.llm_provider.capitalize()} API密钥，无法使用LLM功能",
                    "sql": None,
                    "explanation": None
                }
            
            # 生成系统消息
            system_message = self._generate_system_message(metadata, sample_data)
            
            # 准备消息历史
            messages = []
            
            # 添加对话历史（如果有）
            if conversation_history:
                for message in conversation_history:
                    role = "user" if message.get("role") == "user" else "assistant"
                    content = message.get("content", "")
                    messages.append({"role": role, "content": content})
            
            # 添加当前查询
            messages.append({"role": "user", "content": query})
            
            # 调用LLM API
            content = self._call_llm_api(system_message, messages, 2000, 0.0)
            
            # 提取SQL语句（查找第一个SQL代码块）
            sql = None
            explanation = content
            
            # 查找```sql```代码块
            import re
            sql_block_pattern = r'```sql\s+(.*?)\s+```'
            sql_blocks = re.findall(sql_block_pattern, content, re.DOTALL)
            
            if sql_blocks:
                sql = sql_blocks[0].strip()
            
            return {
                "sql": sql,
                "explanation": explanation
            }
            
        except Exception as e:
            self.logger.error(f"LLM处理失败: {str(e)}")
            return {
                "error": f"LLM处理失败: {str(e)}",
                "sql": None,
                "explanation": None
            }
    
    def revise_sql(self, original_sql, error_message, metadata, sample_data=None, user_query=None):
        """
        修正有问题的SQL语句
        
        Args:
            original_sql (str): 原始SQL语句
            error_message (str): 错误信息
            metadata (dict): 数据库元数据
            sample_data (dict, optional): 样本数据
            user_query (str, optional): 用户的原始查询
            
        Returns:
            dict: 包含修正后的SQL和解释的字典
        """
        try:
            if (self.llm_provider == 'anthropic' and not self.anthropic_api_key) or (self.llm_provider == 'deepseek' and not self.deepseek_api_key):
                return {
                    "error": f"未配置{self.llm_provider.capitalize()} API密钥，无法使用LLM功能",
                    "sql": None,
                    "explanation": None
                }
            
            # 生成系统消息
            system_message = self._generate_system_message(metadata, sample_data)
            system_message += "\n你的任务是修正有问题的SQL语句，确保修正后的SQL语句可以正确执行。"
            
            # 构建用户消息
            user_message = f"我需要修正以下SQL语句:\n\n```sql\n{original_sql}\n```\n\n这个SQL执行时出现了以下错误:\n\n```\n{error_message}\n```\n\n"
            
            if user_query:
                user_message += f"\n我原本想要查询的是: {user_query}\n"
                
            user_message += "\n请帮我修正SQL语句，使其能够正确执行。"
            
            # 调用LLM API
            content = self._call_llm_api(system_message, [{"role": "user", "content": user_message}], 2000, 0.0)
            
            # 提取修正后的SQL语句
            sql = None
            explanation = content
            
            # 查找```sql```代码块
            import re
            sql_block_pattern = r'```sql\s+(.*?)\s+```'
            sql_blocks = re.findall(sql_block_pattern, content, re.DOTALL)
            
            if sql_blocks:
                sql = sql_blocks[0].strip()
            
            return {
                "sql": sql,
                "explanation": explanation
            }
            
        except Exception as e:
            self.logger.error(f"SQL修正失败: {str(e)}")
            return {
                "error": f"SQL修正失败: {str(e)}",
                "sql": None,
                "explanation": None
            }
    
    def explain_results(self, query, sql, results, metadata):
        """
        解释查询结果
        
        Args:
            query (str): 用户的自然语言查询
            sql (str): 执行的SQL语句
            results (dict): 查询结果
            metadata (dict): 数据库元数据
            
        Returns:
            str: 结果解释
        """
        try:
            if (self.llm_provider == 'anthropic' and not self.anthropic_api_key) or (self.llm_provider == 'deepseek' and not self.deepseek_api_key):
                return f"未配置{self.llm_provider.capitalize()} API密钥，无法使用LLM功能进行结果解释"
            
            # 构建系统消息
            system_message = """你是一个专业的数据分析师，能够清晰解释SQL查询结果。
            
你的任务是解释SQL查询结果，使非技术用户能够理解。请遵循以下原则：
1. 简明扼要地总结结果内容
2. 指出结果中的关键信息或模式
3. 如果结果为空，分析可能的原因
4. 使用自然语言描述，避免技术术语
5. 必要时进行数据统计分析
6. 若有异常值或意外结果，指出并提供可能的解释

输出格式要求清晰、结构化，便于用户快速理解查询结果的含义。
"""
            
            # 构建用户消息
            user_message = f"我的查询是: {query}\n\n"
            user_message += f"执行的SQL是:\n```sql\n{sql}\n```\n\n"
            
            # 添加结果信息
            if isinstance(results, dict):
                user_message += "查询结果:\n"
                
                if "error" in results:
                    user_message += f"查询出错: {results['error']}\n"
                else:
                    # 添加结果统计
                    row_count = results.get("rowCount", 0)
                    user_message += f"返回了 {row_count} 条记录\n"
                    
                    # 添加统计信息
                    if "statistics" in results:
                        user_message += "\n统计信息:\n"
                        for col, stats in results["statistics"].items():
                            user_message += f"- {col}: 最小值={stats.get('min')}, 最大值={stats.get('max')}, 平均值={stats.get('mean')}, 空值数={stats.get('null_count')}\n"
                    
                    # 添加结果数据
                    if "columns" in results and "rows" in results and results["rows"]:
                        user_message += "\n数据示例:\n"
                        columns = results["columns"]
                        
                        # 表头
                        user_message += "| " + " | ".join(columns) + " |\n"
                        user_message += "| " + " | ".join(["---" for _ in columns]) + " |\n"
                        
                        # 数据行（最多显示10行）
                        for idx, row in enumerate(results["rows"]):
                            if idx >= 10:
                                user_message += "| ... | ... | ... |\n"
                                break
                            user_message += "| " + " | ".join([str(row.get(col, "")) for col in columns]) + " |\n"
            else:
                user_message += f"查询结果: {results}\n"
            
            user_message += "\n请帮我解释这个查询结果的含义，使我能够理解查询返回了什么信息。"
            
            # 调用LLM API
            content = self._call_llm_api(system_message, [{"role": "user", "content": user_message}], 2000, 0.0)
            
            # 返回结果解释
            return content
            
        except Exception as e:
            self.logger.error(f"结果解释失败: {str(e)}")
            return f"结果解释失败: {str(e)}" 