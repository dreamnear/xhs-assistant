"""
笔记数据导出模块
从小红书创作者平台导出笔记数据
"""
import asyncio
import pandas as pd
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any
from playwright.async_api import Page, Download

from config import Config
from core.browser import browser_manager
from core.exporter import ExcelExporter
from utils.logger import get_logger

logger = get_logger(__name__)


class NotesExporter:
    """笔记数据导出器"""

    def __init__(self):
        self.page: Optional[Page] = None
        self.exporter = ExcelExporter()

    async def export_notes_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> str:
        """
        导出笔记数据

        Args:
            start_date: 开始日期 (格式: YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYY-MM-DD)
            progress_callback: 进度回调函数 callback(message, progress_percent)

        Returns:
            str: 导出文件的路径
        """

        def update_progress(msg: str, progress: int = 0):
            """更新进度"""
            logger.info(msg)
            if progress_callback:
                progress_callback(msg, progress)

        try:
            update_progress("开始导出笔记数据...", 0)

            # 获取页面
            if not self.page:
                self.page = await browser_manager.new_page()

            # 导航到笔记数据页面
            update_progress("正在导航到笔记数据页面...", 10)
            logger.info("开始导航到笔记数据页面")
            try:
                await self.page.goto(
                    Config.NOTES_DATA_URL,
                    wait_until='domcontentloaded',
                    timeout=60000  # 增加到60秒
                )
                logger.info("页面导航完成，等待动态内容加载")
                await asyncio.sleep(3)  # 等待页面动态内容加载
                logger.info("动态内容加载完成")
            except Exception as e:
                logger.error(f"导航失败: {e}")
                raise Exception(f"导航到笔记数据页面失败: {str(e)}")

            # 如果指定了日期范围，选择日期
            if start_date or end_date:
                update_progress("正在选择日期范围...", 20)
                await self._select_date_range(start_date, end_date)
                await asyncio.sleep(1)

            # 查找并点击导出按钮
            update_progress("正在查找导出按钮...", 30)

            # 尝试多种可能的导出按钮选择器
            export_selectors = [
                'button:has-text("导出")',
                'button:has-text("下载")',
                '.export-btn',
                '.download-btn',
                '[class*="export"]',
                '[class*="download"]'
            ]

            export_btn = None
            for selector in export_selectors:
                try:
                    export_btn = await self.page.wait_for_selector(selector, timeout=2000)
                    if export_btn:
                        logger.info(f"找到导出按钮: {selector}")
                        break
                except:
                    continue

            if not export_btn:
                raise Exception("未找到导出按钮，请检查页面结构")

            # 设置下载处理
            update_progress("准备下载数据...", 40)

            download_path = Config.TEMP_DIR / 'notes_data_temp.xlsx'

            async with self.page.expect_download() as download_info:
                await export_btn.click()
                download = await download_info.value

            update_progress("正在下载文件...", 60)

            # 保存下载的文件
            await download.save_as(download_path)
            logger.info(f"文件已下载到: {download_path}")

            update_progress("正在处理数据...", 70)

            # 读取并处理数据
            data = await self._process_downloaded_file(download_path)

            # 导出为Excel
            update_progress("正在生成Excel文件...", 80)

            filename = Config.get_output_filename('notes_data')
            output_path = self.exporter.export(data, filename, sheet_name='笔记数据')

            # 清理临时文件
            if download_path.exists():
                download_path.unlink()

            update_progress(f"笔记数据导出完成！文件保存在: {output_path}", 100)

            return output_path

        except Exception as e:
            update_progress(f"导出失败: {str(e)}", 0)
            logger.error(f"导出笔记数据失败: {e}", exc_info=True)
            raise

    async def _select_date_range(self, start_date: Optional[str], end_date: Optional[str]):
        """
        选择日期范围

        Args:
            start_date: 开始日期
            end_date: 结束日期
        """
        try:
            # 查找日期选择器
            date_picker_selectors = [
                '.date-picker',
                '.date-range-picker',
                '[class*="date"]',
                '[placeholder*="日期"]'
            ]

            date_picker = None
            for selector in date_picker_selectors:
                try:
                    date_picker = self.page.wait_for_selector(selector, timeout=2000)
                    if date_picker:
                        break
                except:
                    continue

            if date_picker:
                # 点击日期选择器
                await date_picker.click()
                await asyncio.sleep(0.5)

                # 这里需要根据实际的日期选择器结构来实现
                # 暂时跳过具体实现，因为页面结构可能不同
                logger.warning("日期选择功能尚未完全实现，请手动选择日期")

        except Exception as e:
            logger.warning(f"选择日期范围失败: {e}")

    async def _process_downloaded_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        处理下载的文件

        Args:
            file_path: 下载的文件路径

        Returns:
            处理后的数据列表
        """
        try:
            # 根据文件扩展名读取文件
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path, encoding=Config.CSV_ENCODING)
            elif file_path.suffix in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_path.suffix}")

            logger.info(f"读取到 {len(df)} 条记录")
            logger.debug(f"列名: {df.columns.tolist()}")

            # 转换为字典列表
            data = df.to_dict('records')

            # 数据清洗和验证
            validated_data = self.exporter.validate_data(data)

            return validated_data

        except Exception as e:
            logger.error(f"处理文件失败: {e}", exc_info=True)
            raise

    async def get_notes_summary(self) -> Dict[str, Any]:
        """
        获取笔记数据概览（不导出，仅查看）

        Returns:
            笔记数据概览
        """
        try:
            if not self.page:
                self.page = await browser_manager.new_page()

            await self.page.goto(Config.NOTES_DATA_URL)
            await self.page.wait_for_load_state('networkidle')

            # 这里可以提取页面上的统计数据
            # 例如：总笔记数、总浏览量、总点赞数等

            summary = {
                'total_notes': 0,
                'total_views': 0,
                'total_likes': 0,
                'total_comments': 0
            }

            # TODO: 根据实际页面结构提取数据

            return summary

        except Exception as e:
            logger.error(f"获取笔记概览失败: {e}")
            raise

    async def close(self):
        """关闭页面"""
        if self.page:
            await self.page.close()
            self.page = None
