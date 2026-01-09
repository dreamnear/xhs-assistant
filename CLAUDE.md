# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个小红书创作者平台数据抓取工具，使用 Playwright 进行浏览器自动化，从 https://creator.xiaohongshu.com/ 抓取笔记数据和粉丝数据。

## 运行环境要求

**重要：必须使用虚拟环境**

项目依赖 tkinter，系统 Python 通常缺少此模块。虚拟环境已配置完整依赖。

```bash
# 推荐方式 - 使用启动脚本
./run.sh

# 手动启动
source venv/bin/activate
export PLAYWRIGHT_BROWSERS_PATH=./browsers
python main.py
```

## 常用命令

### 运行主程序
```bash
./run.sh                    # 使用启动脚本（推荐）
python main.py              # 需先激活虚拟环境
```

### 测试
```bash
# 测试脚本位于 tests/ 目录
python tests/test_core.py               # 测试核心模块
python tests/test_complete_export.py    # 测试完整导出流程
```

### 浏览器管理
```bash
export PLAYWRIGHT_BROWSERS_PATH=./browsers
playwright install chromium    # 安装 Chromium 浏览器到 browsers/ 目录
```

### 环境配置
```bash
cp .env.example .env          # 创建配置文件
# 然后编辑 .env 文件修改配置
```

## 核心架构

### 配置系统 (config.py)
- **Config 类**：集中管理所有配置
- 支持从 `.env` 文件加载环境变量
- 处理 PyInstaller 打包后的路径问题
- 关键配置项：
  - `SESSION_MAX_AGE`: 会话有效期（默认 24 小时）
  - `HEADLESS`: 是否无头模式（默认 false）
  - `DEFAULT_FOLLOWER_DAYS`: 默认抓取天数（默认 30）

### 核心模块 (core/)

**browser.py - 浏览器管理**
- 单例模式管理浏览器实例
- 使用 Playwright 的 `storage_state` 保存会话
- 会话文件：`.sessions/storage_state.json`
- 浏览器路径：`browsers/chromium-xxx`

**auth.py - 认证模块**
- 支持两种登录方式：二维码登录、手机号+验证码登录
- 登录状态检测：检查 `is-logged` 类
- 自动保存登录会话到 `.sessions/` 目录

**exporter.py - 数据导出**
- Excel 格式导出（使用 openpyxl）
- 自动调整列宽
- 输出到 `data/output/` 目录

### 功能模块 (modules/)

**notes_exporter.py - 笔记数据导出**
- 导出页面：https://creator.xiaohongshu.com/statistics/data-analysis
- 日期范围筛选
- 导出按钮处理和文件下载

**followers_scraper.py - 粉丝数据抓取**
- 抓取页面：https://creator.xiaohongshu.com/statistics/fans-data
- 按天抓取新增粉丝数、掉丝数、粉丝总数
- 支持自定义天数（默认 30 天）

**unified_exporter.py - 统一导出器**
- 整合笔记数据和粉丝数据的导出流程

### GUI 界面 (gui/)

**main_window.py - 主窗口**
- Tkinter GUI 界面
- 三个标签页：登录、笔记数据导出、粉丝数据抓取
- 实时进度显示和日志输出

**login_dialog.py - 登录对话框**
- 二维码登录界面
- 手机号+验证码登录界面

## 项目结构

```
xiaohongshu/
├── main.py                  # 主程序入口
├── config.py                # 配置管理（处理环境变量和路径）
├── run.sh                   # 启动脚本
│
├── core/                    # 核心模块
│   ├── browser.py          # 浏览器管理（单例模式）
│   ├── auth.py             # 登录认证（会话管理）
│   └── exporter.py         # Excel 导出
│
├── modules/                 # 功能模块
│   ├── notes_exporter.py   # 笔记数据导出
│   ├── followers_scraper.py # 粉丝数据抓取
│   └── unified_exporter.py # 统一导出器
│
├── gui/                     # GUI 界面
│   ├── main_window.py      # 主窗口
│   └── login_dialog.py     # 登录对话框
│
├── utils/                   # 工具模块
│   └── logger.py           # 日志工具
│
├── data/                    # 数据目录
│   ├── output/             # 导出文件（Excel）
│   └── temp/               # 临时文件
│
├── tests/                   # 测试脚本
├── debug/                   # 调试脚本
├── reports/                 # 文档和报告
├── .sessions/               # 登录会话（storage_state.json）
├── logs/                    # 日志文件
└── browsers/                # Playwright 浏览器驱动
```

## 关键设计模式

1. **单例模式**：`browser.py` 中的 BrowserManager 确保只有一个浏览器实例
2. **会话持久化**：使用 Playwright 的 `storage_state` 保存登录状态
3. **配置分离**：所有配置集中在 `config.py`，支持环境变量覆盖
4. **模块化设计**：core、modules、gui 清晰分层

## 重要文件和目录

- **`.env`**: 环境配置（需从 `.env.example` 复制）
- **`.sessions/storage_state.json`**: 登录会话文件（自动生成，有效期 24 小时）
- **`data/output/`**: 导出的 Excel 文件存放目录
- **`logs/xhs_YYYYMMDD.log`**: 当天日志文件
- **`browsers/`**: Playwright 浏览器驱动目录

## 开发注意事项

1. **会话管理**：登录会话保存在 `.sessions/storage_state.json`，有效期 24 小时
2. **浏览器路径**：必须设置 `PLAYWRIGHT_BROWSERS_PATH` 环境变量指向 `browsers/` 目录
3. **页面选择器**：小红书页面结构可能变化，选择器需要定期维护
4. **虚拟环境**：系统 Python 缺少 tkinter，必须使用虚拟环境
5. **数据导出**：默认导出为 Excel 格式，输出到 `data/output/` 目录

## 打包构建

项目支持使用 PyInstaller 打包成独立可执行文件：

```bash
# Windows
build_windows.bat

# 或手动打包
pyinstaller build/build_onefile.spec
```

打包后的配置：
- 入口点：`main.py`
- 浏览器路径打包处理：`sys._MEIPASS`
- 会话和输出目录在可执行文件同级

## 故障排查

- **登录失败**：删除 `.sessions/storage_state.json` 重新登录
- **浏览器未安装**：运行 `playwright install chromium`
- **无法启动**：确保在虚拟环境中运行
- **抓取失败**：查看 `logs/` 目录中的日志文件
