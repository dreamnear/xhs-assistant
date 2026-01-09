"""
测试：导出7天粉丝数据
"""
import asyncio
import sys
sys.path.insert(0, '.')

from modules.followers_scraper import FollowersScraper
from playwright.async_api import async_playwright
from config import Config
from pathlib import Path


async def main():
    print("=" * 60)
    print("测试：导出7天粉丝数据")
    print("=" * 60)

    async with async_playwright() as p:
        session_file = Path('.sessions/storage_state.json')

        browser = await p.chromium.launch(headless=False)

        if session_file.exists():
            context = await browser.new_context(storage_state=str(session_file))
        else:
            context = await browser.new_context()

        page = await context.new_page()

        scraper = FollowersScraper()
        scraper.page = page

        print("\n开始抓取7天数据...")
        output_path = await scraper.scrape_followers_data(days=7)

        print(f"\n✅ 导出完成: {output_path}")

        # 验证
        import csv
        with open(output_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            print(f"\n总行数: {len(rows)}")

            if 5 <= len(rows) <= 10:
                print(f"\n✅ SUCCESS - 7天数据导出成功（实际{len(rows)}天）")
                print("SUCCESS")
            else:
                print(f"\n⚠️  导出{len(rows)}天数据（期望7天左右）")

        await asyncio.sleep(3)
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
