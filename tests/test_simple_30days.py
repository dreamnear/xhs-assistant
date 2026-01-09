"""
简化测试：只提取总粉丝数30天
"""
import asyncio
import sys
sys.path.insert(0, '.')

from playwright.async_api import async_playwright
from config import Config
from pathlib import Path
import csv


async def main():
    print("=" * 60)
    print("简化测试：提取30天总粉丝数")
    print("=" * 60)

    async with async_playwright() as p:
        session_file = Path('.sessions/storage_state.json')

        browser = await p.chromium.launch(headless=False)

        if session_file.exists():
            context = await browser.new_context(storage_state=str(session_file))
        else:
            context = await browser.new_context()

        page = await context.new_page()

        print(f"\n1. 导航到粉丝数据页面...")
        await page.goto(Config.FOLLOWERS_DATA_URL, wait_until='domcontentloaded')
        await asyncio.sleep(3)

        # 选择30天
        print("2. 选择近30天...")
        label = await page.wait_for_selector('label.select-item-default:has-text("近30天")', timeout=5000)
        await label.click()
        await asyncio.sleep(2)

        # 等待图表加载
        await asyncio.sleep(2)

        print("\n3. 开始数据提取...")

        # 查找图表
        chart = await page.wait_for_selector('.chart-container', timeout=5000)
        box = await chart.bounding_box()

        # 存储数据
        data = {}

        # 只提取总粉丝数
        print("4. 切换到总粉丝数...")
        label = await page.wait_for_selector('label.select-item-default:has-text("总粉丝数")', timeout=3000)
        await label.click()
        await asyncio.sleep(1.0)

        # 60个采样点
        sample_points = 60
        print(f"5. 开始遍历{sample_points}个采样点...")

        for i in range(sample_points):
            x = box['x'] + box['width'] - (i * (box['width'] / sample_points))
            y = box['y'] + box['height'] / 2

            await page.mouse.move(x, y)
            await asyncio.sleep(0.3)

            try:
                tooltip = await page.wait_for_selector('[class*="tooltip"]', timeout=500, state='visible')
                if tooltip:
                    tooltip_text = await tooltip.inner_text()

                    lines = tooltip_text.strip().split('\n')
                    if len(lines) >= 3:
                        date_str = lines[0].strip()
                        value_str = lines[2].strip()

                        import re
                        numbers = re.findall(r'(\d+)', value_str)
                        value = int(numbers[0]) if numbers else 0

                        if date_str not in data:
                            data[date_str] = {'日期': date_str, '总粉丝数': value}
                            print(f"   [{len(data)}] {date_str} = {value}")

            except:
                continue

        print(f"\n6. 提取完成，共 {len(data)} 天数据")

        # 导出CSV
        if data:
            output_dir = Path('data/output')
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / 'test_30days.csv'

            fieldnames = ['日期', '总粉丝数']
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(sorted(data.values(), key=lambda x: x['日期'], reverse=True))

            print(f"7. CSV文件已导出: {output_path}")

            if len(data) >= 25:
                print("\n✅ SUCCESS - 提取到足够的数据（25天以上）")
            else:
                print(f"\n⚠️  只提取到{len(data)}天数据")

        print("\n浏览器保持打开5秒...")
        await asyncio.sleep(5)

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
