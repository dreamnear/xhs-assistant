"""
测试天数验证功能
验证选择7天导出7天，选择30天导出30天
"""
import asyncio
import sys
sys.path.insert(0, '.')

from modules.followers_scraper import FollowersScraper
from playwright.async_api import async_playwright
from pathlib import Path
import pandas as pd


async def test_days_export(days: int):
    """测试指定天数的导出"""
    print("=" * 60)
    print(f"测试：导出最近{days}天的粉丝数据")
    print("=" * 60)

    async with async_playwright() as p:
        session_file = Path('.sessions/storage_state.json')

        browser = await p.chromium.launch(headless=False)

        if session_file.exists():
            context = await browser.new_context(storage_state=str(session_file))
        else:
            context = await browser.new_context()

        page = await context.new_page()

        # 初始化导出器
        scraper = FollowersScraper()
        scraper.page = page

        def update_progress(msg, progress):
            print(f"[{progress}%] {msg}")

        try:
            print(f"\n开始导出{days}天数据...")
            csv_path = await scraper.scrape_followers_data(days=days, progress_callback=update_progress)

            print(f"\n✅ 导出完成!")
            print(f"文件路径: {csv_path}")

            # 验证文件
            print("\n验证数据:")
            df = pd.read_csv(csv_path, encoding='utf-8-sig')

            print(f"  实际导出天数: {len(df)}")
            print(f"  期望天数: {days}")

            # 检查数据行数是否符合预期（允许±1天的误差）
            if abs(len(df) - days) <= 1:
                print(f"  ✅ 天数验证通过")
            else:
                print(f"  ❌ 天数不符合预期: 期望{days}天，实际{len(df)}天")

            print(f"\n前3行数据:")
            print(df.head(3).to_string(index=False))

            # 检查字段完整性
            required_fields = ['日期', '新增粉丝', '掉丝数', '总粉丝数', '净增长', '当前粉丝总数']
            missing_fields = [f for f in required_fields if f not in df.columns]
            if missing_fields:
                print(f"\n❌ 缺少字段: {missing_fields}")
            else:
                print(f"\n✅ 所有必需字段都存在")

            # 检查数据有效性
            valid_data = df[df['总粉丝数'] > 0]
            if len(valid_data) > 0:
                print(f"✅ 有效数据: {len(valid_data)}天")
            else:
                print(f"❌ 所有数据的总粉丝数都为0")

            print("\n浏览器保持打开3秒...")
            await asyncio.sleep(3)

        except Exception as e:
            print(f"\n❌ 导出失败: {e}")
            import traceback
            traceback.print_exc()

        await browser.close()


async def main():
    # 测试7天
    await test_days_export(7)

    print("\n" * 3)

    # 测试30天
    await test_days_export(30)


if __name__ == '__main__':
    asyncio.run(main())
