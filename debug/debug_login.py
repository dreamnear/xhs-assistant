"""
调试脚本 - 查看粉丝数据页面
"""
import asyncio
import sys
sys.path.insert(0, '.')

from playwright.async_api import async_playwright
from config import Config


async def main():
    print("正在启动浏览器...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 尝试加载已保存的会话
        from pathlib import Path
        session_file = Path('.sessions/storage_state.json')
        if session_file.exists():
            print("加载已保存的会话...")
            context = await browser.new_context(storage_state=str(session_file))
            page = await context.new_page()

        print(f"正在打开粉丝数据页面: {Config.FOLLOWERS_DATA_URL}")
        await page.goto(Config.FOLLOWERS_DATA_URL, wait_until='domcontentloaded')

        print("等待页面加载...")
        await asyncio.sleep(3)

        # 截图保存
        screenshot_path = "data/temp/followers_page.png"
        Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"页面截图已保存: {screenshot_path}")

        # 查找日期选择相关的元素
        print("\n正在查找日期选择器...")

        # 查找所有按钮
        buttons = await page.query_selector_all('button')
        print(f"找到 {len(buttons)} 个button标签")
        for i, btn in enumerate(buttons[:20]):
            try:
                text = await btn.inner_text()
                class_name = await btn.get_attribute('class')
                if text and ('天' in text or '日' in text or '7' in text or '30' in text or '90' in text):
                    print(f"  [{i}] 文本: {text.strip()} | class: {class_name}")
            except:
                pass

        # 查找可能的日期选项
        date_selectors = [
            '[class*="date"]',
            '[class*="range"]',
            '[class*="tab"]',
            '.select',
            'select',
        ]

        for selector in date_selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"\n找到 {len(elements)} 个匹配 '{selector}' 的元素")
                for i, el in enumerate(elements[:5]):
                    try:
                        text = await el.inner_text()
                        print(f"  [{i}] 文本: {text.strip()[:50]}")
                    except:
                        pass

        print("\n浏览器将保持打开60秒，请查看页面...")
        print("观察页面上的日期选择器在哪里，如何选择30天的数据")
        print("然后按Ctrl+C关闭...")

        try:
            await asyncio.sleep(60)
        except KeyboardInterrupt:
            print("\n正在关闭浏览器...")

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
