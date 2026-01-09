"""
调试版本：详细显示tooltip提取过程
"""
import asyncio
import sys
sys.path.insert(0, '.')

from playwright.async_api import async_playwright
from config import Config
from pathlib import Path


async def main():
    print("=" * 60)
    print("调试：30天数据提取")
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
        try:
            label = await page.wait_for_selector('label.select-item-default:has-text("近30天")', timeout=5000)
            await label.click()
            await asyncio.sleep(2)
        except:
            pass

        # 等待图表加载
        await asyncio.sleep(2)

        print("\n3. 开始数据提取...")

        # 查找图表
        chart = await page.wait_for_selector('.chart-container', timeout=5000)
        box = await chart.bounding_box()
        print(f"   图表位置: x={box['x']}, y={box['y']}, width={box['width']}, height={box['height']}")

        # 存储数据
        data = {}

        # 只测试总粉丝数
        chart_types = [{"name": "总粉丝数", "field": "总粉丝数"}]

        for type_idx, chart_type in enumerate(chart_types):
            print(f"\n处理: {chart_type['name']}")

            # 切换选项
            label_selector = f'label.select-item-default:has-text("{chart_type["name"]}")'
            label = await page.wait_for_selector(label_selector, timeout=3000)
            await label.click()
            await asyncio.sleep(1.0)

            # 测试10个点
            days_to_test = 10
            for i in range(days_to_test):
                # 从右到左均匀分布
                x = box['x'] + box['width'] - (i * (box['width'] / days_to_test))
                y = box['y'] + box['height'] / 2

                print(f"\n   [{i+1}/{days_to_test}] 移动鼠标到: x={x:.1f}, y={y:.1f}")
                await page.mouse.move(x, y)
                await asyncio.sleep(0.5)

                # 查找tooltip
                try:
                    tooltip = await page.wait_for_selector('[class*="tooltip"]', timeout=1000, state='visible')
                    if tooltip:
                        tooltip_text = await tooltip.inner_text()
                        print(f"   ✅ Tooltip: {repr(tooltip_text)}")

                        lines = tooltip_text.strip().split('\n')
                        if len(lines) >= 3:
                            date_str = lines[0].strip()
                            value_str = lines[2].strip()

                            import re
                            numbers = re.findall(r'(\d+)', value_str)
                            value = int(numbers[0]) if numbers else 0

                            if date_str not in data:
                                data[date_str] = {'日期': date_str, '总粉丝数': 0}

                            data[date_str][chart_type['field']] = value
                            print(f"   → 提取: {date_str} = {value}")
                except Exception as e:
                    print(f"   ❌ 失败: {e}")

        print(f"\n{'='*60}")
        print("提取的数据汇总：")
        print(f"共 {len(data)} 天")
        for date, item in sorted(data.items(), reverse=True):
            print(f"{date}: {item}")

        print("\n浏览器保持打开10秒...")
        await asyncio.sleep(10)

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
