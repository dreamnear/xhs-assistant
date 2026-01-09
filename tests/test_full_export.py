"""
完整测试：导出30天粉丝数据为CSV格式
"""
import asyncio
import sys
sys.path.insert(0, '.')

from playwright.async_api import async_playwright
from modules.followers_scraper import FollowersScraper
from config import Config
from pathlib import Path


async def main():
    print("=" * 60)
    print("完整测试：导出30天粉丝数据")
    print("=" * 60)

    async with async_playwright() as p:
        session_file = Path('.sessions/storage_state.json')

        browser = await p.chromium.launch(headless=False)

        if session_file.exists():
            context = await browser.new_context(storage_state=str(session_file))
        else:
            context = await browser.new_context()

        page = await context.new_page()

        print(f"\n1. 初始化抓取器...")
        scraper = FollowersScraper()
        scraper.page = page

        print("2. 开始抓取30天数据...")
        output_path = await scraper.scrape_followers_data(days=30)

        print(f"\n3. 导出完成！")
        print(f"   文件路径: {output_path}")

        # 读取并显示前几行
        print("\n4. 验证导出数据:")
        print("-" * 60)

        import csv
        with open(output_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            print(f"   总行数: {len(rows)}")
            print(f"\n   前5行数据:")
            for i, row in enumerate(rows[:5]):
                print(f"   {i+1}. {row['日期']}: 新增={row['新增粉丝']}, "
                      f"掉丝={row['掉丝数']}, 总数={row['总粉丝数']}, "
                      f"净增长={row['净增长']}")

            if len(rows) >= 30:
                print(f"\n✅ 成功导出30天数据！")
                print("SUCCESS")
            else:
                print(f"\n⚠️  导出{len(rows)}天数据（期望30天）")

        print("-" * 60)

        print("\n浏览器将保持打开5秒...")
        await asyncio.sleep(5)

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
