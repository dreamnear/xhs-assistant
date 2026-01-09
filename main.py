"""
小红书创作者平台数据抓取工具 - 主程序入口
"""
import sys
import os

# 确保当前目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def setup_environment():
    """
    设置运行环境
    处理PyInstaller打包后的路径问题
    """
    # 设置浏览器路径环境变量（在config.py中也会设置）
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的路径
        base_path = sys._MEIPASS
    else:
        # 开发环境路径
        base_path = os.path.dirname(os.path.abspath(__file__))

    # 设置浏览器路径
    browsers_path = os.path.join(base_path, 'browsers')
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_path

    print(f"浏览器路径设置为: {browsers_path}")


def check_dependencies():
    """检查依赖是否已安装"""
    missing = []

    try:
        import playwright
    except ImportError:
        missing.append('playwright')

    try:
        import tkinter
    except ImportError:
        missing.append('tkinter')

    try:
        import openpyxl
    except ImportError:
        missing.append('openpyxl')

    if missing:
        print("错误：缺少必要的依赖包：")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\n请运行以下命令安装依赖：")
        print("  pip install -r requirements.txt")
        print("\n或者使用PyInstaller重新打包程序")
        return False

    return True


def check_browser_installation():
    """检查浏览器是否已安装"""
    from pathlib import Path

    browsers_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '')
    chromium_path = Path(browsers_path) / 'chromium' if browsers_path else None

    if chromium_path and chromium_path.exists():
        return True

    print("警告：未检测到Chromium浏览器")
    print("如果程序无法正常运行，请执行以下命令安装浏览器：")
    print("  playwright install chromium")
    print()

    return False


def main():
    """主函数"""
    print("=" * 60)
    print("小红书创作者平台数据抓取工具")
    print("=" * 60)
    print()

    # 设置环境
    setup_environment()

    # 检查依赖
    if not check_dependencies():
        input("按任意键退出...")
        sys.exit(1)

    # 检查浏览器（仅警告，不退出）
    check_browser_installation()

    try:
        # 导入GUI模块
        from gui.main_window import MainWindow
        from config import Config
        from utils.logger import get_logger

        logger = get_logger(__name__)

        logger.info("=" * 60)
        logger.info("应用程序启动")
        logger.info(f"版本: 1.0.0")
        logger.info(f"输出目录: {Config.OUTPUT_DIR}")
        logger.info(f"日志目录: {Config.LOG_DIR}")
        logger.info("=" * 60)

        # 创建并运行主窗口
        app = MainWindow()
        app.run()

    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)

    except Exception as e:
        print(f"\n程序运行出错: {e}")
        import traceback
        traceback.print_exc()

        try:
            # 尝试显示错误对话框
            import tkinter as tk
            from tkinter import messagebox

            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口

            messagebox.showerror(
                "程序错误",
                f"程序运行出错：\n\n{str(e)}\n\n请查看日志文件获取详细信息"
            )

            root.destroy()
        except:
            pass

        input("按任意键退出...")
        sys.exit(1)


if __name__ == '__main__':
    main()
