"""
统一导出模块
处理多种数据的统一导出流程
"""
import asyncio
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime

from config import Config
from core.browser import browser_manager
from core.exporter import ExcelExporter
from modules.notes_exporter import NotesExporter
from modules.followers_scraper import FollowersScraper
from utils.logger import get_logger

logger = get_logger(__name__)


class UnifiedExporter:
    """统一导出器"""

    def __init__(self):
        self.notes_exporter = NotesExporter()
        self.followers_scraper = FollowersScraper()
        self.excel_exporter = ExcelExporter()

    async def export_all(
        self,
        export_config: Dict[str, Any],
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> str:
        """
        统一导出所有勾选的数据

        Args:
            export_config: 导出配置
                {
                    'export_notes': bool,
                    'notes_date_range': str,  # 'all' or 'custom'
                    'notes_start_date': str or None,
                    'notes_end_date': str or None,
                    'export_followers': bool,
                    'followers_days': int
                }
            progress_callback: 进度回调函数

        Returns:
            str: 导出文件的路径
        """

        def update_progress(msg: str, progress: int = 0):
            """更新进度"""
            logger.info(msg)
            if progress_callback:
                progress_callback(msg, progress)

        try:
            update_progress("开始导出数据...", 0)

            # 收集所有数据
            all_data = {}
            total_steps = 0
            current_step = 0

            # 计算总步骤数
            if export_config['export_notes']:
                total_steps += 1
            if export_config['export_followers']:
                total_steps += 1

            # 1. 导出笔记数据
            if export_config['export_notes']:
                current_step += 1
                progress = int((current_step - 1) / total_steps * 80) + 10
                update_progress(f"[{current_step}/{total_steps}] 正在导出笔记数据...", progress)

                try:
                    notes_data = await self._export_notes(
                        export_config['notes_date_range'],
                        export_config['notes_start_date'],
                        export_config['notes_end_date'],
                        update_progress
                    )

                    if notes_data:
                        all_data['笔记数据'] = notes_data
                        update_progress(f"✓ 笔记数据导出成功，共 {len(notes_data)} 条记录", progress + 5)
                    else:
                        update_progress(f"⚠ 笔记数据为空", progress + 5)
                except Exception as e:
                    update_progress(f"⚠ 笔记数据导出失败: {str(e)}", progress + 5)
                    logger.warning(f"笔记数据导出失败（不影响其他数据）: {e}")

            # 2. 抓取粉丝数据
            if export_config['export_followers']:
                current_step += 1
                progress = int((current_step - 1) / total_steps * 80) + 10
                update_progress(f"[{current_step}/{total_steps}] 正在抓取粉丝数据...", progress)

                try:
                    followers_data = await self._export_followers(
                        export_config['followers_days'],
                        update_progress
                    )

                    if followers_data:
                        all_data['粉丝数据'] = followers_data
                        update_progress(f"✓ 粉丝数据抓取成功，共 {len(followers_data)} 条记录", progress + 5)
                    else:
                        update_progress(f"⚠ 粉丝数据为空", progress + 5)
                except Exception as e:
                    update_progress(f"⚠ 粉丝数据抓取失败: {str(e)}", progress + 5)
                    logger.warning(f"粉丝数据抓取失败（不影响其他数据）: {e}")

            # 3. 导出完成，不再生成汇总Excel文件
            if not all_data:
                raise Exception("没有获取到任何数据")

            # 收集已生成的文件路径
            output_files = []
            if '笔记数据' in all_data:
                # 笔记数据已经是单独的Excel文件
                notes_files = list(Path('data/output').glob('notes_data_*.xlsx'))
                if notes_files:
                    latest_notes = max(notes_files, key=lambda p: p.stat().st_mtime)
                    output_files.append(('笔记数据', str(latest_notes)))

            if '粉丝数据' in all_data:
                # 粉丝数据已经是单独的CSV文件
                followers_files = list(Path('data/output').glob('followers_data_*.csv'))
                if followers_files:
                    latest_followers = max(followers_files, key=lambda p: p.stat().st_mtime)
                    output_files.append(('粉丝数据', str(latest_followers)))

            update_progress("✓ 所有数据导出完成！", 100)

            # 返回文件路径信息
            file_info = "\n".join([f"{name}: {path}" for name, path in output_files])
            logger.info(f"导出文件:\n{file_info}")

            return file_info

        except Exception as e:
            update_progress(f"导出失败: {str(e)}", 0)
            logger.error(f"统一导出失败: {e}", exc_info=True)
            raise

    async def _export_notes(
        self,
        date_range: str,
        start_date: Optional[str],
        end_date: Optional[str],
        progress_callback: Callable[[str, int], None]
    ) -> List[Dict[str, Any]]:
        """导出笔记数据"""
        try:
            # 解析日期参数
            if date_range == 'all':
                start_date = None
                end_date = None

            # 导出笔记数据
            temp_path = await self.notes_exporter.export_notes_data(
                start_date=start_date,
                end_date=end_date,
                progress_callback=progress_callback
            )

            # 读取导出的数据
            import pandas as pd
            df = pd.read_excel(temp_path)
            data = df.to_dict('records')

            # 保留Excel文件，不删除
            # Path(temp_path).unlink()

            logger.info(f"笔记数据已导出: {temp_path}")

            return data

        except Exception as e:
            logger.error(f"导出笔记数据失败: {e}")
            raise

    async def _export_followers(
        self,
        days: int,
        progress_callback: Callable[[str, int], None]
    ) -> List[Dict[str, Any]]:
        """抓取粉丝数据"""
        try:
            # 抓取粉丝数据
            csv_path = await self.followers_scraper.scrape_followers_data(
                days=days,
                progress_callback=progress_callback
            )

            # 读取导出的CSV数据（UTF-8 BOM）
            import pandas as pd
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            data = df.to_dict('records')

            # 保留CSV文件，不删除
            # Path(csv_path).unlink()

            logger.info(f"已读取粉丝数据: {len(data)} 条记录")

            return data

        except Exception as e:
            logger.error(f"抓取粉丝数据失败: {e}")
            raise

    def _generate_summary_excel(self, all_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        生成汇总Excel文件

        Args:
            all_data: {sheet_name: data}

        Returns:
            str: 输出文件路径
        """
        try:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"xiaohongshu_data_{timestamp}.xlsx"
            output_path = Config.OUTPUT_DIR / filename

            logger.info(f"正在生成汇总Excel文件: {output_path}")

            # 使用 ExcelExporter 导出多个sheet
            import pandas as pd

            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, data in all_data.items():
                    df = pd.DataFrame(data)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    logger.info(f"  添加sheet: {sheet_name}, {len(data)} 行")

            logger.info(f"汇总Excel文件生成成功: {output_path}")

            return str(output_path)

        except Exception as e:
            logger.error(f"生成汇总Excel失败: {e}")
            raise
