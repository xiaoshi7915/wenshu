# WenShu 项目设置指南

本指南介绍如何使用Python 3.12设置和运行WenShu自然语言数据库查询智能体项目。

## 1. Python 环境设置

### 1.1 安装Python 3.12

确保您的系统已安装Python 3.12。可以从[Python官网](https://www.python.org/downloads/)下载并安装。

### 1.2 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 在Linux/macOS上激活虚拟环境
source venv/bin/activate

# 在Windows上激活虚拟环境
venv\Scripts\activate
```

### 1.3 安装依赖

```bash
# 安装项目依赖
pip install -r requirements.txt
```

## 2. 环境变量配置

### 2.1 设置环境变量

项目的环境变量已在`.env`文件中配置。如需修改，可编辑该文件：

```
# 修改LLM提供商（可选：anthropic, deepseek）
LLM_PROVIDER=deepseek  # 或 anthropic
```

## 3. 启动项目

### 3.1 使用Python直接启动

```bash
# 确保激活了虚拟环境后，运行
python run.py
```

### 3.2 使用Gunicorn启动（仅限Linux/macOS）

```bash
gunicorn --bind 0.0.0.0:5000 run:app
```

### 3.3 使用Docker启动

```bash
# 构建并启动容器
docker-compose up -d
```

## 4. 访问应用

启动后，在浏览器中访问：http://localhost:5000

## 5. MCP功能说明

WenShu项目使用MCP（Model Context Protocol）实现多种数据库连接器：

1. 目前已实现MySQL连接器
2. 未来将支持PostgreSQL、SQL Server和Oracle连接器

MCP服务器负责：
- 获取数据库元数据
- 执行只读SQL查询
- 返回查询结果和统计信息

## 6. LLM功能说明

项目支持多种LLM服务提供商：

1. Anthropic Claude - 通过`ANTHROPIC_API_KEY`环境变量配置
2. DeepSeek - 通过`DEEPSEEK_API_KEY`环境变量配置

可以通过`LLM_PROVIDER`环境变量选择使用哪种LLM服务。 