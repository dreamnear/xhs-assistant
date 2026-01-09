"""
测试修改后的导出功能
"""
import asyncio
import sys
sys.path.insert(0, '.')

from modules.unified_exporter import UnifiedExporter
from playwright.async_api import async_playwright
from config import Config
from pathlib import Path


async def main():
    print("=" * 60)
    print("测试：独立文件导出（无汇总Excel）")
    print("=" * 60)

    async with async_playwright() as p:
        session_file = Path('.sessions/storage_state.json')

        browser = await p.chromium.launch(headless=False)

        if session_file.exists():
            context = await browser.new_context(storage_state=str(session_file))
        else:
            context = await browser.new_context()

        page = await context.new_page()

        # 初始化导出器
        unified_exporter = UnifiedExporter()
        unified_exporter.followers_scraper.page = page

        # 测试配置（只导出粉丝数据，7天）
        export_config = {
            'export_notes': False,  # 不导出笔记，测试更快
            'notes_date_range': 'all',
            'notes_start_date': None,
            'notes_end_date': None,
            'export_followers': True,
            'followers_days': 7  # 默认7天
        }

        print("\n配置:")
        print(f"  导出笔记: {export_config['export_notes']}")
        print(f"  导出粉丝数据: {export_config['export_followers']}")
        print(f"  粉丝数据天数: {export_config['followers_days']}")

        def update_progress(msg, progress):
            print(f"[{progress}%] {msg}")

        try:
            print("\n开始导出...")
            result = await unified_exporter.export_all(export_config, update_progress)

            print(f"\n✅ 导出完成!")
            print(f"\n导出的文件:")
            print(result)

            # 检查文件是否存在
            print("\n检查文件:")
            output_dir = Path('data/output')

            followers_files = list(output_dir.glob('followers_data_*.csv'))
            if followers_files:
                latest = max(followers_files, key=lambda p: p.stat().st_mtime)
                print(f"✅ 粉丝数据CSV: {latest}")

                import pandas as pd
                df = pd.read_csv(latest, encoding='utf-8-sig')
                print(f"   行数: {len(df)}")
                print(f"   前3行:")
                print(df.head(3).to_string(index=False))

            # 检查是否生成了汇总Excel（不应该有）
            summary_files = list(output_dir.glob('xiaohongshu_data_*.xlsx'))
            if summary_files:
                print(f"\n⚠️  发现汇总Excel文件（应该没有）: {summary_files[-1]}")
            else:
                print(f"\n✅ 正确：没有生成汇总Excel文件")

            print("\n浏览器保持打开3秒...")
            await asyncio.sleep(3)

        except Exception as e:
            print(f"\n❌ 导出失败: {e}")
            import traceback
            traceback.print_exc()

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
