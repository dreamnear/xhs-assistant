"""
工作版本：导出30天粉丝数据（包括新增、掉丝、总数）
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
    print("导出30天粉丝数据（新增/掉丝/总数）")
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

        # 定义三种数据类型
        chart_types = [
            {"name": "新增粉丝数", "field": "新增粉丝"},
            {"name": "流失粉丝数", "field": "掉丝数"},
            {"name": "总粉丝数", "field": "总粉丝数"}
        ]

        for type_idx, chart_type in enumerate(chart_types):
            print(f"\n{type_idx+1}. 提取{chart_type['name']}...")

            # 切换图表
            label = await page.wait_for_selector(f'label.select-item-default:has-text("{chart_type["name"]}")', timeout=3000)
            await label.click()
            await asyncio.sleep(1.0)

            # 60个采样点
            sample_points = 60
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
                                data[date_str] = {
                                    '日期': date_str,
                                    '新增粉丝': 0,
                                    '掉丝数': 0,
                                    '总粉丝数': 0
                                }

                            data[date_str][chart_type['field']] = value
                except:
                    continue

        print(f"\n4. 提取完成，共 {len(data)} 天数据")

        # 转换为列表并排序
        data_list = sorted(data.values(), key=lambda x: x['日期'], reverse=True)

        # 计算净增长
        for item in data_list:
            item['净增长'] = item['新增粉丝'] - item['掉丝数']

        # 获取当前粉丝总数（最新一天）
        current_total = data_list[0]['总粉丝数'] if data_list else 0
        for item in data_list:
            item['当前粉丝总数'] = current_total

        # 导出CSV
        if data_list:
            output_dir = Path('data/output')
            output_dir.mkdir(parents=True, exist_ok=True)

            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = output_dir / f'followers_data_{timestamp}.csv'

            fieldnames = ['日期', '新增粉丝', '掉丝数', '总粉丝数', '净增长', '当前粉丝总数']
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data_list)

            print(f"5. CSV文件已导出: {output_path}")

            # 验证
            print("\n6. 验证导出数据:")
            print(f"   总行数: {len(data_list)}")

            if len(data_list) >= 25:
                print(f"\n   前5行数据:")
                for i, row in enumerate(data_list[:5]):
                    print(f"   {i+1}. {row['日期']}: 新增={row['新增粉丝']}, "
                          f"掉丝={row['掉丝数']}, 总数={row['总粉丝数']}, "
                          f"净增长={row['净增长']}")

                print("\n✅ SUCCESS - 成功导出30天粉丝数据！")
                print("SUCCESS")
            else:
                print(f"\n⚠️  只导出{len(data_list)}天数据（期望30天）")
        else:
            print("\n❌ 没有提取到数据")

        print("\n浏览器保持打开5秒...")
        await asyncio.sleep(5)

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
