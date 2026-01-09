"""
调试脚本 - 查找粉丝数据页面的详细数据
"""
import asyncio
import sys
sys.path.insert(0, '.')

from playwright.async_api import async_playwright
from config import Config
from pathlib import Path


async def main():
    print("正在启动浏览器...")

    async with async_playwright() as p:
        session_file = Path('.sessions/storage_state.json')

        browser = await p.chromium.launch(headless=False)

        if session_file.exists():
            context = await browser.new_context(storage_state=str(session_file))
        else:
            context = await browser.new_context()

        page = await context.new_page()

        print(f"正在打开粉丝数据页面: {Config.FOLLOWERS_DATA_URL}")
        await page.goto(Config.FOLLOWERS_DATA_URL, wait_until='domcontentloaded')
        await asyncio.sleep(3)

        # 选择30天
        print("选择近30天...")
        try:
            label = await page.wait_for_selector('label.select-item-default:has-text("近30天")', timeout=5000)
            await label.click()
            await asyncio.sleep(2)
        except:
            pass

        # 截图
        screenshot_path = "data/temp/fans_detail_page.png"
        Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"页面截图已保存: {screenshot_path}")

        # 查找所有数字
        print("\n正在查找页面上的所有数据...")
        js_code = """
        () => {
            const results = [];

            // 查找所有显示数字的文本
            const allElements = document.querySelectorAll('*');
            allElements.forEach(el => {
                const text = el.textContent || '';
                const trimmed = text.trim();

                // 查找包含"新增"、"掉丝"、"流失"等关键词的元素
                if (trimmed.includes('新增') || trimmed.includes('掉丝') ||
                    trimmed.includes('流失') || trimmed.includes('净增')) {
                    if (trimmed.length < 100) {  // 只取较短的文本
                        results.push({
                            tag: el.tagName,
                            text: trimmed.substring(0, 80),
                            class: el.className,
                            id: el.id
                        });
                    }
                }
            });

            return results;
        }
        """

        elements = await page.evaluate(js_code)

        print(f"\n找到 {len(elements)} 个包含粉丝数据的元素：")
        for i, el in enumerate(elements[:30]):  # 只显示前30个
            print(f"\n[{i}] {el['tag']}")
            print(f"  文本: {el['text']}")
            print(f"  class: {el['class']}")
            if el['id']:
                print(f"  id: {el['id']}")

        # 查找表格
        print("\n\n正在查找表格...")
        tables = await page.query_selector_all('table')
        print(f"找到 {len(tables)} 个表格")

        for i, table in enumerate(tables):
            rows = await table.query_selector_all('tr')
            print(f"\n表格 {i+1}: {len(rows)} 行")

            if len(rows) > 0 and len(rows) < 50:  # 只显示较小的表格
                for j, row in enumerate(rows[:5]):  # 只显示前5行
                    cells = await row.query_selector_all('td, th')
                    if cells:
                        row_data = []
                        for cell in cells:
                            text = await cell.inner_text()
                            row_data.append(text.strip()[:20])
                        print(f"  行 {j+1}: {' | '.join(row_data)}")

        print("\n浏览器将保持打开30秒，请查看页面...")
        print("观察新增和掉丝数据在哪里显示")
        try:
            await asyncio.sleep(30)
        except KeyboardInterrupt:
            print("\n正在关闭浏览器...")

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
