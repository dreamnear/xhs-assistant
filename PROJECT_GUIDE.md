# 小红书创作者平台数据抓取工具 - 项目说明文档

## 📖 项目简介

这是一个用于从小红书创作者平台（https://creator.xiaohongshu.com/）抓取数据的桌面应用程序，支持导出笔记数据和粉丝数据。

### 核心功能

- ✅ **登录管理**
  - 二维码登录（推荐，使用小红书APP扫码）
  - 手机号+验证码登录
  - 自动保存登录会话（24小时免登录）

- ✅ **笔记数据导出**
  - 导出"内容分析-笔记数据"
  - 支持日期范围筛选
  - 自动生成Excel文件

- ✅ **粉丝数据抓取**
  - 抓取每日新增粉丝数
  - 抓取每日掉丝数
  - 抓取粉丝总数
  - 支持自定义天数（默认30天）

## 🛠️ 技术栈

- **Python 3.9+** - 主要开发语言
- **Playwright** - 浏览器自动化框架
- **Tkinter** - GUI界面框架
- **openpyxl** - Excel文件操作
- **pandas** - 数据处理

## 📋 环境要求

### 必需环境

1. **Python 3.9 或更高版本**
   ```bash
   python --version  # 检查版本
   ```

2. **网络连接**
   - 能够访问 creator.xiaohongshu.com
   - 稳定的网络环境

### 推荐配置

- **操作系统**：macOS、Linux、Windows
- **内存**：建议 4GB 以上
- **磁盘空间**：至少 500MB（包含浏览器驱动）

## 🚀 安装步骤

### 1. 克隆或下载项目

```bash
cd /path/to/your/workspace
# 如果是 git 仓库
git clone <repository-url>
cd xhs-assistant
```

### 2. 创建虚拟环境

**重要：必须使用虚拟环境，系统Python可能缺少tkinter模块**

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

依赖包包括：
- playwright==1.48.0
- pyinstaller==6.11.0
- openpyxl==3.1.5
- python-dotenv==1.0.1
- pandas

### 4. 安装浏览器

```bash
# 设置浏览器路径
export PLAYWRIGHT_BROWSERS_PATH=./browsers

# 安装Chromium浏览器
playwright install chromium
```

浏览器将安装到 `browsers/` 目录（约300MB）。

### 5. 配置环境变量（可选）

```bash
# 复制配置文件模板
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用其他编辑器
```

常用配置项：
```bash
# 浏览器配置
HEADLESS=false              # 是否无头模式（true=不显示浏览器窗口）
BROWSER_WIDTH=1280          # 浏览器宽度
BROWSER_HEIGHT=720          # 浏览器高度

# 会话配置
SESSION_MAX_AGE=24          # 会话有效期（小时）

# 数据配置
DEFAULT_FOLLOWER_DAYS=30    # 默认抓取天数
```

## 📝 使用说明

### 方法1：使用启动脚本（推荐）

```bash
./run.sh
```

启动脚本会自动：
- 检查虚拟环境
- 激活虚拟环境
- 设置浏览器路径
- 检查浏览器安装
- 启动程序

### 方法2：手动启动

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 设置浏览器路径
export PLAYWRIGHT_BROWSERS_PATH=./browsers

# 3. 运行程序
python main.py
```

### 操作步骤

#### 1. 登录账号
- 点击"登录账号"按钮
- 选择登录方式：
  - **二维码登录**：使用小红书APP扫描二维码（推荐）
  - **手机号登录**：输入手机号和验证码
- 等待登录完成（会话自动保存）

#### 2. 导出笔记数据
- 切换到"笔记数据导出"标签页
- （可选）选择日期范围
- 点击"开始导出笔记数据"
- 等待导出完成

#### 3. 抓取粉丝数据
- 切换到"粉丝数据抓取"标签页
- 选择要抓取的天数（默认30天）
- 点击"开始抓取粉丝数据"
- 等待抓取完成

#### 4. 查看导出文件
导出的文件保存在 `data/output/` 目录：
- 笔记数据：`notes_data_YYYYMMDD_HHMMSS.xlsx`
- 粉丝数据：`followers_data_YYYYMMDD_HHMMSS.xlsx`

## 📦 打包说明

### macOS/Linux 打包

#### 1. 确保环境准备就绪

```bash
# 激活虚拟环境
source venv/bin/activate

# 确认依赖已安装
pip list | grep -E "playwright|pyinstaller|openpyxl"
```

#### 2. 运行打包命令

```bash
# 方式1：使用PyInstaller直接打包
pyinstaller --onefile --windowed \
  --name "小红书数据助手" \
  --add-data "browsers:browsers" \
  --add-data "core:core" \
  --add-data "modules:modules" \
  --add-data "gui:gui" \
  --add-data "utils:utils" \
  --hidden-import playwright \
  --hidden-import playwright.sync_api \
  main.py
```

或使用打包配置文件（如果有）：
```bash
# 使用 spec 文件打包（推荐）
pyinstaller build/build_onefile.spec
```

#### 3. 打包输出

打包完成后，可执行文件位于：
- `dist/小红书数据助手` (macOS/Linux单文件)
- 或 `dist/main` (使用默认名称)

#### 4. 测试打包结果

```bash
# 运行打包后的程序
./dist/小红书数据助手

# 或
./dist/main
```

### Windows 打包

#### 1. 准备环境

在Windows系统上或使用Windows虚拟机：

```cmd
# 激活虚拟环境
venv\Scripts\activate

# 确认依赖
pip list
```

#### 2. 运行打包脚本

项目提供了Windows打包脚本：

```cmd
build_windows.bat
```

或手动执行：

```cmd
pyinstaller --onefile --windowed ^
  --name "小红书数据助手" ^
  --add-data "browsers;browsers" ^
  --add-data "core;core" ^
  --add-data "modules;modules" ^
  --add-data "gui;gui" ^
  --add-data "utils;utils" ^
  --hidden-import playwright ^
  --hidden-import playwright.sync_api ^
  main.py
```

#### 3. 打包输出

Windows可执行文件位于：
- `dist/小红书数据助手.exe`

### 打包注意事项

1. **浏览器驱动**：
   - 打包时会包含 `browsers/` 目录
   - 如果浏览器未安装，用户首次运行时需要安装

2. **依赖处理**：
   - PyInstaller会自动处理大部分Python依赖
   - 使用 `--hidden-import` 显式导入可能被遗漏的模块

3. **单文件 vs 目录模式**：
   - `--onefile`：打包成单个可执行文件（启动较慢）
   - `--onedir`：打包成目录（启动较快，文件较多）

4. **GUI模式**：
   - `--windowed`：不显示控制台窗口（适用于GUI程序）
   - 如需调试，去掉此选项以查看控制台输出

5. **图标设置**（可选）：
   ```bash
   --icon=app.icn  # macOS
   --icon=app.ico  # Windows
   ```

### 打包后的目录结构

```
dist/
├── 小红书数据助手        # macOS/Linux 可执行文件
└── 小红书数据助手.exe    # Windows 可执行文件
```

首次运行时会自动创建：
- `data/` - 数据目录
- `.sessions/` - 会话目录
- `logs/` - 日志目录

## 🔧 常见问题

### Q1: 程序无法启动？

**A:** 检查以下几点：
```bash
# 1. 确认虚拟环境已激活
source venv/bin/activate

# 2. 确认依赖已安装
pip install -r requirements.txt

# 3. 确认浏览器已安装
export PLAYWRIGHT_BROWSERS_PATH=./browsers
playwright install chromium
```

### Q2: 提示缺少tkinter模块？

**A:** 必须使用虚拟环境：
```bash
# 重新创建虚拟环境
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Q3: 登录后提示"未登录"？

**A:** 会话可能已过期（24小时），重新登录即可：
```bash
# 删除旧会话
rm .sessions/storage_state.json

# 重新运行程序登录
./run.sh
```

### Q4: 数据抓取失败？

**A:** 查看日志文件：
```bash
# 查看当天日志
cat logs/xhs_$(date +%Y%m%d).log

# 或查看最新日志
tail -f logs/xhs_*.log
```

常见原因：
- 网络连接不稳定
- 页面结构变化（选择器失效）
- 登录状态过期

### Q5: 打包后的文件无法运行？

**A:** 检查打包配置：
1. 确认所有必要文件都已打包（使用 `--add-data`）
2. 检查隐藏导入（使用 `--hidden-import`）
3. 查看PyInstaller日志中的警告信息

### Q6: 如何查看程序日志？

**A:** 日志文件位置：
```bash
# 查看所有日志
ls -lh logs/

# 实时监控日志
tail -f logs/xhs_$(date +%Y%m%d).log

# 搜索错误信息
grep ERROR logs/xhs_*.log
```

## ⚠️ 注意事项

### 使用建议

1. **首次使用**：需要登录账号（二维码或手机号）
2. **会话保持**：登录后会话保存24小时，之后需要重新登录
3. **网络要求**：确保能访问 creator.xiaohongshu.com
4. **使用频率**：建议不要过于频繁使用，避免触发反爬虫机制
5. **数据备份**：定期备份 `data/output/` 目录中的导出文件

### 开发建议

1. **虚拟环境**：始终在虚拟环境中开发和测试
2. **日志查看**：遇到问题首先查看日志文件
3. **浏览器模式**：开发时使用 `HEADLESS=false` 查看浏览器操作
4. **代码修改**：修改代码后需重新打包才能生效

### 安全建议

1. **不要分享**：`.sessions/` 目录包含登录会话，不要分享给他人
2. **定期更换密码**：定期更换小红书账号密码
3. **隐私保护**：导出的数据包含个人隐私，注意保管
4. **合法使用**：仅用于个人数据分析，不要用于商业用途

## 📚 项目结构

```
xiaohongshu/
├── main.py                  # 主程序入口
├── config.py                # 配置管理
├── requirements.txt         # 依赖清单
├── run.sh                   # 启动脚本
├── build_windows.bat        # Windows打包脚本
│
├── core/                    # 核心模块
│   ├── browser.py          # 浏览器管理
│   ├── auth.py             # 登录认证
│   └── exporter.py         # Excel导出
│
├── modules/                 # 功能模块
│   ├── notes_exporter.py   # 笔记数据导出
│   ├── followers_scraper.py # 粉丝数据抓取
│   └── unified_exporter.py # 统一导出器
│
├── gui/                     # GUI界面
│   ├── main_window.py      # 主窗口
│   └── login_dialog.py     # 登录对话框
│
├── utils/                   # 工具函数
│   └── logger.py           # 日志工具
│
├── tests/                   # 测试脚本
├── debug/                   # 调试脚本
├── reports/                 # 文档和报告
│
├── data/                    # 数据目录
│   ├── output/             # 导出文件
│   └── temp/               # 临时文件
│
├── .sessions/               # 登录会话
├── logs/                    # 日志文件
└── browsers/                # 浏览器驱动
```

## 🆘 获取帮助

如遇到问题：

1. **查看日志**：`logs/xhs_YYYYMMDD.log`
2. **检查网络**：确认能访问小红书平台
3. **重新登录**：删除 `.sessions/storage_state.json` 后重新登录
4. **查看文档**：`reports/` 目录下的详细文档

## 📄 许可证

MIT License

---

**文档版本**: 1.0
**更新日期**: 2025-01-09
**项目状态**: ✅ 开发完成，可用
