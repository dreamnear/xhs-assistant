# 小红书创作者平台数据抓取工具

## 项目简介

这是一个用于从小红书创作者平台（https://creator.xiaohongshu.com/）抓取数据的工具。

### 核心功能

1. **登录功能**
   - 支持二维码登录（推荐）
   - 支持手机号+验证码登录
   - 自动保存登录会话，下次启动免登录

2. **笔记数据导出**
   - 导出"内容分析-笔记数据"
   - 支持日期范围筛选
   - 自动生成Excel文件

3. **粉丝数据抓取**
   - 抓取每日新增粉丝数
   - 抓取每日掉丝数
   - 抓取粉丝总数
   - 支持自定义天数（默认30天）

## 快速开始

### ⚠️ 重要：使用虚拟环境

由于系统Python环境的限制，**必须使用虚拟环境运行此程序**。

### 1. 使用启动脚本（推荐）

```bash
./run.sh
```

### 2. 手动启动

```bash
# 激活虚拟环境
source venv/bin/activate

# 设置浏览器路径
export PLAYWRIGHT_BROWSERS_PATH=./browsers

# 运行程序
python main.py
```

**详细说明请查看：[QUICKSTART.md](QUICKSTART.md)**

### 2. 登录账号

- 点击"登录账号"按钮
- 选择登录方式：
  - **二维码登录**：使用小红书APP扫描二维码
  - **手机号登录**：输入手机号和验证码

### 3. 导出数据

#### 笔记数据导出
1. 切换到"笔记数据导出"标签页
2. （可选）选择日期范围
3. 点击"开始导出笔记数据"
4. 等待导出完成

#### 粉丝数据抓取
1. 切换到"粉丝数据抓取"标签页
2. 选择要抓取的天数（默认30天）
3. 点击"开始抓取粉丝数据"
4. 等待抓取完成

### 4. 查看数据

导出的数据保存在 `data/output/` 文件夹中：
- 笔记数据：`notes_data_YYYYMMDD_HHMMSS.xlsx`
- 粉丝数据：`followers_data_YYYYMMDD_HHMMSS.xlsx`

## 项目结构

```
xiaohongshu/
├── main.py                      # 程序入口
├── config.py                    # 配置管理
├── requirements.txt             # 依赖清单
│
├── core/                        # 核心模块
│   ├── browser.py              # 浏览器管理
│   ├── auth.py                 # 登录认证
│   └── exporter.py             # Excel导出
│
├── modules/                     # 功能模块
│   ├── notes_exporter.py       # 笔记数据导出
│   └── followers_scraper.py    # 粉丝数据抓取
│
├── gui/                         # GUI界面
│   ├── main_window.py          # 主窗口
│   └── login_dialog.py         # 登录对话框
│
├── utils/                       # 工具函数
│   └── logger.py               # 日志工具
│
├── data/                        # 数据目录
│   ├── output/                 # 导出文件
│   └── temp/                   # 临时文件
│
├── .sessions/                   # 登录会话
├── logs/                        # 日志文件
└── browsers/                    # 浏览器驱动
```

## 技术栈

- **Python 3.9+**
- **Playwright**：浏览器自动化
- **Tkinter**：GUI界面
- **openpyxl**：Excel操作
- **pandas**：数据处理

## 配置说明

编辑 `.env.example` 文件并重命名为 `.env` 来修改配置：

```bash
# 浏览器配置
HEADLESS=false              # 是否无头模式
BROWSER_WIDTH=1280          # 浏览器宽度
BROWSER_HEIGHT=720          # 浏览器高度

# 会话配置
SESSION_MAX_AGE=24          # 会话有效期（小时）

# 数据配置
DEFAULT_FOLLOWER_DAYS=30    # 默认抓取天数
EXPORT_FORMAT=excel         # 导出格式
```

## 注意事项

1. **首次登录**：需要使用二维码或验证码登录
2. **会话保持**：登录后会话保存24小时，之后需要重新登录
3. **网络要求**：需要能够访问 creator.xiaohongshu.com
4. **使用频率**：建议不要过于频繁使用，避免触发反爬虫机制
5. **数据准确性**：粉丝数据通过页面抓取，可能因页面结构变化而失效

## 常见问题

### Q: 登录后提示"未登录"怎么办？
A: 点击"登录账号"重新登录即可，会话可能已过期。

### Q: 粉丝数据抓取失败怎么办？
A: 可能是页面结构变化，查看日志文件了解详细错误信息。

### Q: 如何查看运行日志？
A: 日志保存在 `logs/` 文件夹中，文件名格式为 `xhs_YYYYMMDD.log`

### Q: 程序无法启动怎么办？
A: 检查是否安装了所有依赖：
```bash
pip install -r requirements.txt
```

## 开发与贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
