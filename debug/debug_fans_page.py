"""
调试脚本 - 详细查找粉丝数据页面的日期选择器
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
        browser = await p.chromium.launch(headless=False)
        session_file = Path('.sessions/storage_state.json')
        context = await browser.new_context(storage_state=str(session_file))
        page = await context.new_page()

        print(f"正在打开粉丝数据页面: {Config.FOLLOWERS_DATA_URL}")
        await page.goto(Config.FOLLOWERS_DATA_URL, wait_until='domcontentloaded')
        await asyncio.sleep(3)

        # 使用JavaScript查找所有可能包含日期选项的元素
        print("\n正在使用JavaScript查找日期选择器...")

        js_code = """
        () => {
            const results = [];

            // 查找所有文本包含"7天"、"30天"、"90天"的元素
            const allElements = document.querySelectorAll('*');
            allElements.forEach(el => {
                const text = el.textContent || '';
                const trimmed = text.trim();

                if (trimmed.includes('7天') || trimmed.includes('30天') || trimmed.includes('90天') ||
                    trimmed.includes('近7') || trimmed.includes('近30') || trimmed.includes('近90')) {
                    results.push({
                        tag: el.tagName,
                        text: trimmed.substring(0, 50),
                        class: el.className,
                        id: el.id,
                        html: el.outerHTML.substring(0, 200)
                    });
                }
            });

            return results;
        }
        """

        elements = await page.evaluate(js_code)

        print(f"\n找到 {len(elements)} 个包含日期选项的元素：")
        for i, el in enumerate(elements):
            print(f"\n[{i}] 标签: {el['tag']}")
            print(f"  文本: {el['text']}")
            print(f"  class: {el['class']}")
            print(f"  id: {el['id']}")
            print(f"  HTML: {el['html']}")

        print("\n浏览器将保持打开60秒，请查看页面...")
        try:
            await asyncio.sleep(60)
        except KeyboardInterrupt:
            print("\n正在关闭浏览器...")

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
