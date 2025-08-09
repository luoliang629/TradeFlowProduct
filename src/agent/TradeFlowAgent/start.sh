#!/bin/bash

# TradeFlow Agent 快速启动脚本

echo "=== TradeFlow Agent (Google ADK) 启动脚本 ==="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "提示：未找到 .env 文件，正在从模板创建..."
    cp .env.example .env
    echo "已创建 .env 文件，请编辑该文件设置你的 API Key"
    echo ""
fi

# 检查依赖
echo "正在检查依赖..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "正在安装依赖..."
    pip install -r requirements.txt
fi

# 启动选项
echo ""
echo "请选择启动方式："
echo "1. Web 界面 (推荐)"
echo "2. 命令行演示"
echo "3. 运行测试"
echo "4. 退出"
echo ""

read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo "正在启动 Web 服务器..."
        echo "访问地址: http://localhost:8000"
        echo "API 文档: http://localhost:8000/docs"
        echo ""
        python3 web_app.py
        ;;
    2)
        echo "正在运行命令行演示..."
        echo ""
        python3 run_demo.py
        ;;
    3)
        echo "正在运行测试..."
        echo ""
        python3 -m pytest test/ -v
        ;;
    4)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac