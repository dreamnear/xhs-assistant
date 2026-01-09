"""
快速测试脚本
验证程序的基本功能是否正常
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """测试所有模块是否能正常导入"""
    print("测试1: 检查模块导入...")
    try:
        import config
        print("  ✓ config.py 导入成功")

        from core.browser import browser_manager
        print("  ✓ core/browser.py 导入成功")

        from core.auth import AuthManager
        print("  ✓ core/auth.py 导入成功")

        from core.exporter import ExcelExporter
        print("  ✓ core/exporter.py 导入成功")

        from modules.notes_exporter import NotesExporter
        print("  ✓ modules/notes_exporter.py 导入成功")

        from modules.followers_scraper import FollowersScraper
        print("  ✓ modules/followers_scraper.py 导入成功")

        from gui.main_window import MainWindow
        print("  ✓ gui/main_window.py 导入成功")

        from gui.login_dialog import LoginDialog
        print("  ✓ gui/login_dialog.py 导入成功")

        print("\n✅ 所有模块导入成功！\n")
        return True

    except Exception as e:
        print(f"\n❌ 模块导入失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """测试配置是否正确"""
    print("测试2: 检查配置...")
    try:
        import config

        print(f"  基础路径: {config.Config.BASE_DIR}")
        print(f"  输出目录: {config.Config.OUTPUT_DIR}")
        print(f"  会话目录: {config.Config.SESSION_DIR}")
        print(f"  日志目录: {config.Config.LOG_DIR}")
        print(f"  浏览器路径: {config.Config.get_browser_path()}")
        print(f"  创作者平台URL: {config.Config.CREATOR_PLATFORM_URL}")

        # 检查目录是否存在
        if config.Config.OUTPUT_DIR.exists():
            print("  ✓ 输出目录存在")
        else:
            print("  ⚠ 输出目录不存在")

        if config.Config.SESSION_DIR.exists():
            print("  ✓ 会话目录存在")
        else:
            print("  ⚠ 会话目录不存在")

        print("\n✅ 配置检查完成！\n")
        return True

    except Exception as e:
        print(f"\n❌ 配置检查失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies():
    """测试依赖是否安装"""
    print("测试3: 检查依赖包...")
    try:
        import playwright
        print(f"  ✓ playwright 已安装")

        import openpyxl
        print(f"  ✓ openpyxl 版本: {openpyxl.__version__}")

        from tkinter import Tk
        print(f"  ✓ tkinter 可用")

        import pandas
        print(f"  ✓ pandas 版本: {pandas.__version__}")

        print("\n✅ 依赖包检查完成！\n")
        return True

    except ImportError as e:
        print(f"\n❌ 依赖包缺失: {e}\n")
        return False


def test_browser():
    """测试浏览器是否可用"""
    print("测试4: 检查浏览器...")
    try:
        import os
        browsers_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '')
        print(f"  浏览器路径: {browsers_path}")

        from pathlib import Path
        chromium_path = Path(browsers_path) / 'chromium-1140'

        if chromium_path.exists():
            print(f"  ✓ Chromium浏览器已安装")
            print(f"    路径: {chromium_path}")
            return True
        else:
            print(f"  ⚠ Chromium浏览器未找到")
            print(f"    请运行: playwright install chromium")
            return False

    except Exception as e:
        print(f"\n❌ 浏览器检查失败: {e}\n")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("小红书数据抓取工具 - 功能测试")
    print("=" * 60)
    print()

    results = []

    # 运行测试
    results.append(("依赖检查", test_dependencies()))
    results.append(("模块导入", test_imports()))
    results.append(("配置检查", test_config()))
    results.append(("浏览器检查", test_browser()))

    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")

    print()
    print(f"总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！程序可以正常运行。")
        print("\n请运行以下命令启动程序：")
        print("  python main.py")
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息。")

    print("=" * 60)


if __name__ == '__main__':
    main()
