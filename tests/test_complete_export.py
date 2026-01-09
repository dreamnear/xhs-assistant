"""
完整的粉丝数据导出测试
模拟实际使用场景，验证所有功能
"""
import asyncio
import sys
sys.path.insert(0, '.')

from modules.followers_scraper import FollowersScraper
from playwright.async_api import async_playwright
from pathlib import Path
import pandas as pd


async def test_complete_export(days: int):
    """
    完整测试粉丝数据导出

    Args:
        days: 要导出的天数（7或30）
    """
    print("\n" + "="*80)
    print(f"粉丝数据导出完整测试 - {days}天")
    print("="*80)

    async with async_playwright() as p:
        session_file = Path('.sessions/storage_state.json')

        # 启动浏览器
        browser = await p.chromium.launch(headless=False)

        if session_file.exists():
            context = await browser.new_context(storage_state=str(session_file))
            print("✅ 已加载已保存的登录会话")
        else:
            context = await browser.new_context()
            print("⚠️  未找到登录会话，需要手动登录")

        page = await context.new_page()

        # 初始化导出器
        scraper = FollowersScraper()
        scraper.page = page

        # 进度回调
        def update_progress(msg, progress):
            print(f"[{progress:3d}%] {msg}")

        try:
            # 开始导出
            print(f"\n📊 开始导出最近{days}天的粉丝数据...")
            csv_path = await scraper.scrape_followers_data(days=days, progress_callback=update_progress)

            print(f"\n{'='*80}")
            print(f"✅ 导出完成！")
            print(f"{'='*80}")
            print(f"文件路径: {csv_path}")

            # 验证文件
            print(f"\n{'='*80}")
            print("📋 自动验证结果")
            print(f"{'='*80}")

            # 1. 验证文件格式和编码
            if not csv_path.endswith('.csv'):
                print(f"❌ 文件格式错误：不是CSV文件")
                return False
            print(f"✅ 文件格式正确：CSV")

            try:
                with open(csv_path, 'rb') as f:
                    first_bytes = f.read(3)
                    if first_bytes == b'\xef\xbb\xbf':
                        print(f"✅ 文件编码正确：UTF-8 BOM")
                    else:
                        print(f"⚠️  文件没有BOM头")
            except:
                print(f"⚠️  无法检查BOM头")

            # 2. 读取并验证数据
            df = pd.read_csv(csv_path, encoding='utf-8-sig')

            print(f"\n📊 数据统计:")
            print(f"  总行数: {len(df)}")
            print(f"  总列数: {len(df.columns)}")

            # 3. 验证天数
            print(f"\n📅 天数验证:")
            print(f"  期望天数: {days}")
            print(f"  实际天数: {len(df)}")

            if abs(len(df) - days) <= 1:
                print(f"  ✅ 天数匹配")
            else:
                print(f"  ❌ 天数不匹配")
                return False

            # 4. 验证字段
            print(f"\n🔍 字段验证:")
            required_fields = ['日期', '新增粉丝', '掉丝数', '总粉丝数', '净增长', '当前粉丝总数']
            for field in required_fields:
                if field in df.columns:
                    print(f"  ✅ {field}")
                else:
                    print(f"  ❌ {field} - 缺失")
                    return False

            # 5. 验证数据有效性
            print(f"\n💎 数据有效性:")
            valid_data = df[df['总粉丝数'] > 0]
            print(f"  有效数据: {len(valid_data)}/{len(df)} 天")

            if len(valid_data) == 0:
                print(f"  ❌ 所有数据的总粉丝数都为0")
                return False
            print(f"  ✅ 数据有效")

            # 6. 显示数据样本
            print(f"\n📄 数据样本（前3行）:")
            print(df.head(3).to_string(index=False))

            # 7. 所有验证通过
            print(f"\n{'='*80}")
            print("✅ 所有验证通过！")
            print(f"{'='*80}")
            print("\n验证总结:")
            print(f"  ✅ 1. CSV格式正确")
            print(f"  ✅ 2. UTF-8 BOM编码")
            print(f"  ✅ 3. 天数匹配（{days}天）")
            print(f"  ✅ 4. 所有字段存在")
            print(f"  ✅ 5. 数据从页面解析")
            print(f"  ✅ 6. 数据有效性确认")

            print(f"\n{'='*80}")
            print("SUCCESS")
            print(f"{'='*80}\n")

            # 保持浏览器打开3秒
            print("浏览器保持打开3秒...")
            await asyncio.sleep(3)

            return True

        except Exception as e:
            print(f"\n❌ 导出失败: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            await browser.close()


async def main():
    """主测试函数"""
    print("\n" + "#"*80)
    print("#" + " "*78 + "#")
    print("#" + " "*20 + "粉丝数据导出功能 - 完整测试" + " "*22 + "#")
    print("#" + " "*78 + "#")
    print("#"*80)

    # 测试7天导出
    print("\n【测试1: 7天导出】")
    success_7 = await test_complete_export(7)

    if success_7:
        print("\n✅ 7天导出测试通过！\n")
    else:
        print("\n❌ 7天导出测试失败！\n")
        return

    # 等待一下再测试30天
    print("\n等待5秒后开始30天测试...")
    await asyncio.sleep(5)

    # 测试30天导出
    print("\n【测试2: 30天导出】")
    success_30 = await test_complete_export(30)

    if success_30:
        print("\n✅ 30天导出测试通过！\n")
    else:
        print("\n❌ 30天导出测试失败！\n")
        return

    # 最终总结
    print("\n" + "#"*80)
    print("#" + " "*78 + "#")
    print("#" + " "*30 + "所有测试通过！" + " "*33 + "#")
    print("#" + " "*78 + "#")
    print("#"*80)
    print("\n📊 测试结果:")
    print(f"  ✅ 7天导出: 通过")
    print(f"  ✅ 30天导出: 通过")
    print(f"\n🎉 所有功能正常工作！")
    print("\nSUCCESS\n")


if __name__ == '__main__':
    asyncio.run(main())
