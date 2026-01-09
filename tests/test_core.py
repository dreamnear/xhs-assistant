"""
核心功能测试（不使用GUI）
测试登录、浏览器管理等核心模块
"""
import sys
import os
import asyncio

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_browser():
    """测试浏览器功能"""
    print("=" * 60)
    print("测试1: 浏览器管理")
    print("=" * 60)

    try:
        from core.browser import browser_manager
        from config import Config

        print(f"✓ 模块导入成功")
        print(f"✓ 浏览器路径: {Config.get_browser_path()}")
        print(f"✓ 会话文件: {Config.SESSION_FILE}")

        # 启动浏览器
        print("\n正在启动浏览器...")
        await browser_manager.launch()
        print("✓ 浏览器启动成功")

        # 创建上下文
        print("\n正在创建浏览器上下文...")
        await browser_manager.create_context()
        print("✓ 浏览器上下文创建成功")

        # 创建页面
        print("\n正在创建新页面...")
        page = await browser_manager.new_page()
        print("✓ 页面创建成功")

        # 导航到测试页面
        print("\n正在导航到百度...")
        await page.goto("https://www.baidu.com")
        print(f"✓ 导航成功，标题: {await page.title()}")

        # 保存会话
        print("\n正在保存会话...")
        await browser_manager.save_session()
        print("✓ 会话保存成功")

        # 关闭浏览器
        print("\n正在关闭浏览器...")
        await browser_manager.close_browser()
        print("✓ 浏览器关闭成功")

        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_exporter():
    """测试Excel导出功能"""
    print("\n" + "=" * 60)
    print("测试2: Excel导出功能")
    print("=" * 60)

    try:
        from core.exporter import ExcelExporter

        print("✓ 模块导入成功")

        # 创建测试数据
        test_data = [
            {'日期': '2025-01-08', '新增粉丝': 10, '掉丝数': 2, '净增长': 8},
            {'日期': '2025-01-07', '新增粉丝': 15, '掉丝数': 3, '净增长': 12},
            {'日期': '2025-01-06', '新增粉丝': 20, '掉丝数': 5, '净增长': 15},
        ]

        print("\n正在导出测试数据...")
        exporter = ExcelExporter()
        output_path = exporter.export(test_data, 'test_export', sheet_name='测试数据')

        print(f"✓ 测试数据导出成功: {output_path}")

        # 验证文件
        import pandas as pd
        df = pd.read_excel(output_path)
        print(f"✓ 验证成功，共 {len(df)} 条记录")

        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_xiaohongshu_navigation():
    """测试小红书平台导航"""
    print("\n" + "=" * 60)
    print("测试3: 小红书平台导航")
    print("=" * 60)

    try:
        from core.browser import browser_manager
        from config import Config

        print("✓ 模块导入成功")

        print(f"\n正在启动浏览器...")
        await browser_manager.launch()
        await browser_manager.create_context()
        page = await browser_manager.new_page()
        print("✓ 浏览器启动成功")

        print(f"\n正在导航到小红书创作者平台...")
        print(f"URL: {Config.CREATOR_PLATFORM_URL}")

        await page.goto(Config.CREATOR_PLATFORM_URL)
        await page.wait_for_load_state('networkidle')

        title = await page.title()
        url = page.url

        print(f"✓ 导航成功")
        print(f"  标题: {title}")
        print(f"  URL: {url}")

        # 检查是否有登录按钮
        print("\n正在检查页面元素...")
        try:
            # 尝试截图
            screenshot_path = "data/temp/test_screenshot.png"
            os.makedirs("data/temp", exist_ok=True)
            await page.screenshot(path=screenshot_path)
            print(f"✓ 页面截图已保存: {screenshot_path}")
        except Exception as e:
            print(f"⚠ 截图失败: {e}")

        print("\n⚠ 注意: 程序将保持浏览器打开30秒，请查看页面")
        print("  你可以看到浏览器窗口打开并显示小红书创作者平台")

        await asyncio.sleep(30)

        # 关闭浏览器
        await browser_manager.close_browser()
        print("\n✓ 浏览器已关闭")

        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

        try:
            await browser_manager.close_browser()
        except:
            pass

        return False


async def main():
    """主测试函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "小红书数据抓取工具 - 核心功能测试" + " " * 10 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    results = []

    # 测试1: 浏览器管理
    result1 = await test_browser()
    results.append(("浏览器管理", result1))

    # 测试2: Excel导出
    result2 = await test_exporter()
    results.append(("Excel导出", result2))

    # 测试3: 小红书平台导航（可选，需要较长时间）
    print("\n" + "=" * 60)
    choice = input("是否测试小红书平台导航？(y/n): ").strip().lower()

    if choice == 'y':
        result3 = await test_xiaohongshu_navigation()
        results.append(("平台导航", result3))
    else:
        print("跳过平台导航测试")

    # 总结
    print("\n" + "=" * 60)
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
        print("\n🎉 所有核心功能测试通过！")
        print("\n注意: 由于tkinter模块不可用，GUI界面无法启动。")
        print("核心功能（浏览器管理、数据导出）运行正常。")
        print("\n建议:")
        print("1. 使用带有GUI界面的环境（如Windows或某些Linux发行版）")
        print("2. 或者继续开发基于命令行界面的版本")
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息")

    print("=" * 60)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试出错: {e}")
        import traceback
        traceback.print_exc()
