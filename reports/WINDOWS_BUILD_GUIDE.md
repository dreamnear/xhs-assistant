# Windows可执行文件打包指南

## 重要说明

**PyInstaller必须在Windows系统上运行才能生成Windows可执行文件。**

由于您当前在macOS系统上，您需要在Windows系统上执行打包操作。

---

## 方案1：使用Windows系统打包（推荐）

### 准备工作

1. **准备Windows电脑**
   - Windows 10/11 64位系统
   - 安装Python 3.10或更高版本
   - 下载地址：https://www.python.org/downloads/

2. **安装Python时注意**
   - ✅ 勾选 "Add Python to PATH"
   - ✅ 勾选 "Install for all users"

### 打包步骤

#### 方法A：自动打包脚本（推荐）

1. 将整个项目文件夹复制到Windows电脑

2. 双击运行 `build_windows.bat`

3. 等待打包完成（可能需要5-10分钟）

4. 完成后，可执行文件在 `dist\小红书数据抓取工具.exe`

#### 方法B：手动打包

1. 打开命令提示符（CMD）

2. 进入项目目录：
```cmd
cd C:\Users\YourName\Downloads\xiaohongshu
```

3. 创建虚拟环境：
```cmd
python -m venv venv
```

4. 激活虚拟环境：
```cmd
venv\Scripts\activate
```

5. 安装依赖：
```cmd
pip install -r requirements.txt
```

6. 安装Playwright浏览器：
```cmd
playwright install chromium
```

7. 执行打包：
```cmd
pyinstaller build/windows.spec --clean
```

8. 等待完成，可执行文件在 `dist\小红书数据抓取工具.exe`

---

## 方案2：使用虚拟机或远程服务器

如果您没有Windows电脑，可以使用以下方法：

### 选项A：使用Windows虚拟机

1. **下载Windows 10虚拟机镜像**
   - 微软官方提供免费的开发者虚拟机
   - 下载：https://developer.microsoft.com/en-us/windows/downloads/virtual-machines/

2. **在Mac上运行虚拟机软件**
   - VMware Fusion
   - Parallels Desktop
   - VirtualBox（免费）

3. **在虚拟机中执行打包步骤**

### 选项B：使用云服务器

1. **租用Windows云服务器**
   - Azure：https://azure.microsoft.com/
   - AWS EC2：https://aws.amazon.com/ec2/
   - 阿里云：https://www.aliyun.com/

2. **远程连接到服务器**
   - 使用远程桌面连接（RDP）

3. **上传项目并打包**

---

## 打包文件说明

### 生成的文件结构

```
dist/
└── 小红书数据抓取工具.exe    # 主程序（单个可执行文件）
```

### 运行时自动创建的目录

```
小红书数据抓取工具.exe
├── .sessions/                 # 会话存储目录（自动创建）
│   └── storage_state.json    # 登录会话
├── data/                      # 数据目录（自动创建）
│   ├── output/               # 导出文件输出
│   └── temp/                 # 临时文件
└── logs/                      # 日志目录（自动创建）
```

---

## 分发给用户

### 单文件版本

`dist\小红书数据抓取工具.exe` 是独立的可执行文件，可以直接分发给用户。

### 用户使用步骤

1. 双击运行 `小红书数据抓取工具.exe`

2. 首次使用：
   - 点击"登录账号"
   - 选择二维码登录
   - 用小红书APP扫码

3. 后续使用：
   - 程序自动加载上次登录
   - 直接选择要导出的数据
   - 点击"开始导出"

4. 查看导出文件：
   - 打开程序目录下的 `data\output` 文件夹
   - 笔记数据：Excel文件
   - 粉丝数据：CSV文件

---

## 常见问题

### Q1: 打包后运行报错"找不到模块"

**A**: 检查 `build/windows.spec` 中的 `hiddenimports` 是否包含所有依赖

### Q2: 打包后文件太大

**A**:
- 使用UPX压缩（已在spec中配置）
- 移除不必要的依赖
- 可以考虑使用 `--onefile` 模式（已配置）

### Q3: 运行时提示缺少浏览器

**A**: Playwright浏览器已打包在程序内，但首次运行需要一些时间解压

### Q4: 杀毒软件报毒

**A**:
- PyInstaller打包的程序可能被误报
- 可以添加数字签名（需要购买证书）
- 或让用户添加信任

### Q5: 在macOS上如何打包Windows程序？

**A**:
- PyInstaller不支持跨平台打包
- 必须在Windows系统上打包Windows程序
- 必须在macOS系统上打包macOS程序

---

## 文件清单

### 打包相关文件

- `build/windows.spec` - PyInstaller配置文件
- `build_windows.bat` - Windows自动打包脚本
- `requirements.txt` - Python依赖清单
- `main_v2.py` - 程序入口

### 输出文件

- `dist/小红书数据抓取工具.exe` - 最终可执行文件

---

## 下一步

### 在Windows系统上执行

1. 复制项目到Windows电脑
2. 双击运行 `build_windows.bat`
3. 等待打包完成
4. 测试 `dist\小红书数据抓取工具.exe`

### 或者使用虚拟机

1. 在Mac上安装Windows虚拟机
2. 在虚拟机中执行打包
3. 将生成的exe文件复制回Mac

---

## 需要帮助？

如果在打包过程中遇到问题，请提供：
- 错误信息截图
- 打包日志
- Windows版本和Python版本

---

**祝打包顺利！** 🎉
