"""
测试修复后的统一导出功能
"""
import asyncio
import sys
sys.path.insert(0, '.')

from playwright.async_api import async_playwright
from modules.unified_exporter import UnifiedExporter
from modules.notes_exporter import NotesExporter
from modules.followers_scraper import FollowersScraper
from config import Config
from pathlib import Path


async def main():
    print("=" * 60)
    print("测试统一导出功能（CSV格式粉丝数据）")
    print("=" * 60)

    async with async_playwright() as p:
        session_file = Path('.sessions/storage_state.json')

        browser = await p.chromium.launch(headless=False)

        if session_file.exists():
            context = await browser.new_context(storage_state=str(session_file))
        else:
            context = await browser.new_context()

        page = await context.new_page()

        # 初始化统一导出器
        unified_exporter = UnifiedExporter()

        # 绑定页面到followers_scraper
        unified_exporter.followers_scraper.page = page

        # 测试配置
        export_config = {
            'export_notes': True,
            'notes_date_range': 'all',
            'notes_start_date': None,
            'notes_end_date': None,
            'export_followers': True,
            'followers_days': 7
        }

        print("\n配置:")
        print(f"  导出笔记: {export_config['export_notes']}")
        print(f"  导出粉丝数据: {export_config['export_followers']}")
        print(f"  粉丝数据天数: {export_config['followers_days']}")

        # 进度回调
        def update_progress(msg, progress):
            print(f"[{progress}%] {msg}")

        try:
            print("\n开始导出...")
            output_path = await unified_exporter.export_all(export_config, update_progress)

            print(f"\n✅ 导出成功!")
            print(f"   汇总文件: {output_path}")

            # 查看生成的文件
            import os
            output_dir = Path('data/output')
            files = list(output_dir.glob('followers_data_*.csv'))

            if files:
                latest_csv = max(files, key=os.path.getmtime)
                print(f"\n最新CSV文件: {latest_csv}")

                # 读取并显示前几行
                import pandas as pd
                df = pd.read_csv(latest_csv, encoding='utf-8-sig')
                print(f"\nCSV文件内容（前5行）:")
                print(df.head())

                if len(df) >= 5:
                    print("\n✅ SUCCESS - CSV格式导出成功！")
                    print("SUCCESS")
                else:
                    print(f"\n⚠️  只导出{len(df)}行数据")

            print("\n浏览器保持打开5秒...")
            await asyncio.sleep(5)

        except Exception as e:
            print(f"\n❌ 导出失败: {e}")
            import traceback
            traceback.print_exc()

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
