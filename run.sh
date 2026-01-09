#!/bin/bash

# 小红书数据抓取工具启动脚本

echo "============================================================"
echo "小红书创作者平台数据抓取工具"
echo "============================================================"
echo ""

# 激活虚拟环境
if [ ! -d "venv" ]; then
    echo "错误: 虚拟环境不存在"
    echo "请先运行: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

# 设置浏览器路径
export PLAYWRIGHT_BROWSERS_PATH=./browsers

# 检查浏览器
if [ ! -d "browsers/chromium-1140" ]; then
    echo "警告: Chromium浏览器未安装"
    echo "正在安装浏览器..."
    playwright install chromium
fi

# 运行程序
echo "正在启动程序..."
echo ""

python main.py
