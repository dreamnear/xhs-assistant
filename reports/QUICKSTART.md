# 快速开始指南

## ⚠️ 重要提示

由于系统Python环境的限制，**强烈建议使用虚拟环境运行此程序**。

## 📋 前置要求

1. **Python 3.9+** - 检查版本：`python --version`
2. **网络连接** - 能够访问 creator.xiaohongshu.com

## 🚀 快速启动

### 方法1：使用启动脚本（推荐）

```bash
# 1. 进入项目目录
cd /Users/kevin/study/xiaohongshu

# 2. 运行启动脚本
./run.sh
```

### 方法2：手动启动

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 设置浏览器路径
export PLAYWRIGHT_BROWSERS_PATH=./browsers

# 3. 运行程序
python main.py
```

## 📝 使用说明

### 1. 登录账号

1. 点击"登录账号"按钮
2. 选择登录方式：
   - **二维码登录**（推荐）：使用小红书APP扫描二维码
   - **手机号登录**：输入手机号和验证码
3. 等待登录完成（会话自动保存）

### 2. 导出笔记数据

1. 切换到"笔记数据导出"标签页
2. （可选）选择日期范围
3. 点击"开始导出笔记数据"
4. 等待导出完成

### 3. 抓取粉丝数据

1. 切换到"粉丝数据抓取"标签页
2. 选择要抓取的天数（默认30天）
3. 点击"开始抓取粉丝数据"
4. 等待抓取完成

### 4. 查看导出文件

导出的文件保存在：`data/output/` 文件夹

- 笔记数据：`notes_data_YYYYMMDD_HHMMSS.xlsx`
- 粉丝数据：`followers_data_YYYYMMDD_HHMMSS.xlsx`

## ⚙️ 配置说明

编辑 `.env` 文件（复制自 `.env.example`）来自定义配置：

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置
nano .env
```

### 常用配置项

- `HEADLESS=false` - 是否无头模式（显示浏览器窗口）
- `SESSION_MAX_AGE=24` - 会话有效期（小时）
- `DEFAULT_FOLLOWER_DAYS=30` - 默认抓取天数
- `LOG_LEVEL=INFO` - 日志级别

## 📂 目录结构

```
xiaohongshu/
├── data/
│   ├── output/          # 导出的Excel文件
│   └── temp/            # 临时文件
├── .sessions/           # 登录会话
├── logs/                # 日志文件
└── browsers/            # 浏览器驱动
```

## 🔧 常见问题

### Q: 程序无法启动？
A: 确保已激活虚拟环境：
```bash
source venv/bin/activate
```

### Q: 提示浏览器未安装？
A: 运行以下命令安装：
```bash
export PLAYWRIGHT_BROWSERS_PATH=./browsers
playwright install chromium
```

### Q: 登录后提示"未登录"？
A: 会话可能已过期（24小时），重新登录即可。

### Q: 数据抓取失败？
A: 查看日志文件了解详细错误：
```bash
cat logs/xhs_$(date +%Y%m%d).log
```

### Q: 如何退出虚拟环境？
A: 运行：
```bash
deactivate
```

## 📚 更多信息

详细文档请查看：[README.md](README.md)

## ⚠️ 注意事项

1. **首次使用**：需要登录账号
2. **会话保持**：登录后会话保存24小时
3. **网络要求**：确保能访问小红书平台
4. **使用频率**：建议不要过于频繁使用
5. **数据备份**：定期备份导出的数据

## 🆘 获取帮助

如遇到问题，请：
1. 查看日志文件
2. 检查网络连接
3. 确认账号状态
4. 尝试重新登录

---

祝您使用愉快！🎉
