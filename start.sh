#!/bin/bash

# 使用颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== WenShu 自然语言数据库查询智能体 ===${NC}"
echo -e "${BLUE}正在准备启动环境...${NC}"

# 检查Python版本
python_version=$(python --version 2>&1)
if [[ $python_version != *"Python 3"* ]]; then
    echo -e "${RED}错误: 未检测到Python 3${NC}"
    echo -e "${YELLOW}请安装Python 3.10+后重试${NC}"
    exit 1
fi

echo -e "${GREEN}检测到 $python_version${NC}"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}未检测到虚拟环境，正在创建...${NC}"
    python -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}创建虚拟环境失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}虚拟环境创建成功${NC}"
else
    echo -e "${GREEN}检测到现有虚拟环境${NC}"
fi

# 激活虚拟环境
echo -e "${BLUE}激活虚拟环境...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}激活虚拟环境失败${NC}"
    exit 1
fi

# 安装依赖
echo -e "${BLUE}检查依赖...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}安装依赖失败${NC}"
    exit 1
fi
echo -e "${GREEN}依赖安装完成${NC}"

# 检查.env文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}未检测到.env文件，使用示例配置...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env文件创建成功${NC}"
else
    echo -e "${GREEN}检测到.env文件${NC}"
fi

# 启动应用
echo -e "${BLUE}正在启动WenShu应用...${NC}"
echo -e "${YELLOW}应用将在 http://localhost:5000 上运行${NC}"
echo -e "${BLUE}按Ctrl+C可停止应用${NC}"
python run.py 