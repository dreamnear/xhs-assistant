"""
测试脚本：验证粉丝数据提取功能
"""
import asyncio
import sys
sys.path.insert(0, '.')

from playwright.async_api import async_playwright
from config import Config
from pathlib import Path


async def main():
    print("=" * 60)
    print("测试粉丝数据提取功能")
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

        print("\n3. 开始数据提取测试...")

        # 查找图表
        chart = await page.wait_for_selector('.chart-container', timeout=5000)
        if not chart:
            print("❌ 未找到图表！")
            return

        box = await chart.bounding_box()
        print(f"   图表位置: x={box['x']}, y={box['y']}, width={box['width']}, height={box['height']}")

        # 存储数据
        data = {}

        # 测试三个选项
        chart_types = [
            {"name": "新增粉丝数", "field": "新增粉丝"},
            {"name": "流失粉丝数", "field": "掉丝数"},
            {"name": "总粉丝数", "field": "总粉丝数"}
        ]

        for type_idx, chart_type in enumerate(chart_types):
            print(f"\n{'='*60}")
            print(f"[{type_idx+1}/3] 处理: {chart_type['name']}")
            print(f"{'='*60}")

            # 切换选项
            try:
                label_selector = f'label.select-item-default:has-text("{chart_type["name"]}")'
                label = await page.wait_for_selector(label_selector, timeout=3000)

                if label:
                    class_name = await label.get_attribute('class') or ''
                    if 'item-active' not in class_name:
                        await label.click()
                        await asyncio.sleep(1.0)  # 增加等待时间
                        print(f"✅ 已切换到: {chart_type['name']}")
                    else:
                        print(f"✅ 已经在: {chart_type['name']}")
            except Exception as e:
                print(f"❌ 切换失败: {e}")
                continue

            # 切换后截图
            screenshot_path = f"data/temp/chart_{type_idx+1}_{chart_type['name']}.png"
            Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=screenshot_path)
            print(f"   📸 已保存截图: {screenshot_path}")

            # 提取前5天的数据
            days_to_test = 5
            for i in range(days_to_test):
                x = box['x'] + box['width'] - (i * (box['width'] / days_to_test))
                y = box['y'] + box['height'] / 2

                print(f"   移动鼠标到: x={x:.1f}, y={y:.1f}")
                await page.mouse.move(x, y)
                await asyncio.sleep(0.5)  # 增加等待时间

                # 尝试多个tooltip选择器
                tooltip_selectors = [
                    '.tooltip',
                    '[class*="tooltip"]',
                    '.chart-tooltip',
                    '[role="tooltip"]'
                ]

                tooltip_found = False
                for selector in tooltip_selectors:
                    try:
                        tooltip = await page.wait_for_selector(selector, timeout=1000, state='visible')
                        if tooltip:
                            tooltip_text = await tooltip.inner_text()
                            # 打印原始tooltip内容用于调试
                            print(f"   📝 Tooltip原始内容: {repr(tooltip_text)}")

                            lines = tooltip_text.strip().split('\n')

                            if len(lines) >= 3:
                                date_str = lines[0].strip()
                                # 第3行才是数值
                                value_str = lines[2].strip() if len(lines) > 2 else '0'

                                # 提取数字
                                import re
                                numbers = re.findall(r'\d+', value_str)
                                value = int(numbers[0]) if numbers else 0

                                # 存储数据
                                if date_str not in data:
                                    data[date_str] = {
                                        '日期': date_str,
                                        '新增粉丝': 0,
                                        '掉丝数': 0,
                                        '总粉丝数': 0
                                    }

                                data[date_str][chart_type['field']] = value
                                print(f"   ✅ Day {i+1}: {date_str} → {chart_type['field']} = {value} (selector: {selector})")
                                tooltip_found = True
                                break
                    except:
                        continue

                if not tooltip_found:
                    print(f"   ❌ Day {i+1}: 所有tooltip选择器都失败")

        print(f"\n{'='*60}")
        print("提取的数据汇总：")
        print(f"{'='*60}")

        # 按日期排序
        sorted_data = sorted(data.values(), key=lambda x: x['日期'], reverse=True)

        for item in sorted_data:
            print(f"\n日期: {item['日期']}")
            print(f"  新增粉丝: {item['新增粉丝']}")
            print(f"  掉丝数: {item['掉丝数']}")
            print(f"  总粉丝数: {item['总粉丝数']}")

        print(f"\n{'='*60}")
        print(f"✅ 共提取 {len(sorted_data)} 天的数据")
        print(f"{'='*60}")

        print("\n浏览器将保持打开10秒，请观察...")
        await asyncio.sleep(10)

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
