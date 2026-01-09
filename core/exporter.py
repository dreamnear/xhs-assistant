"""
Excel导出工具
提供通用的Excel数据导出功能
"""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class ExcelExporter:
    """Excel导出器"""

    def __init__(self):
        self.output_dir = Config.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        data: List[Dict[str, Any]],
        filename: str,
        sheet_name: str = 'Sheet1'
    ) -> str:
        """
        导出数据到Excel

        Args:
            data: 要导出的数据列表（字典列表）
            filename: 文件名（不需要扩展名）
            sheet_name: 工作表名称

        Returns:
            str: 导出文件的完整路径
        """
        if not data:
            raise ValueError("没有数据可导出")

        try:
            logger.info(f"准备导出 {len(data)} 条记录...")

            # 转换为DataFrame
            df = pd.DataFrame(data)

            # 添加导出时间戳
            df['导出时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 生成文件名
            if not filename.endswith('.xlsx'):
                filename = f"{filename}.xlsx"

            output_path = self.output_dir / filename

            # 导出到Excel
            logger.info(f"正在写入Excel文件: {output_path}")
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                # 设置列宽
                worksheet = writer.sheets[sheet_name]
                self._auto_adjust_column_width(worksheet, df)

            logger.info(f"数据导出成功: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"导出Excel失败: {e}", exc_info=True)
            raise

    def export_multiple_sheets(
        self,
        data_dict: Dict[str, List[Dict[str, Any]]],
        filename: str
    ) -> str:
        """
        导出多个工作表到同一个Excel文件

        Args:
            data_dict: 字典，键为工作表名，值为数据列表
            filename: 文件名（不需要扩展名）

        Returns:
            str: 导出文件的完整路径
        """
        if not data_dict:
            raise ValueError("没有数据可导出")

        try:
            logger.info(f"准备导出 {len(data_dict)} 个工作表...")

            # 生成文件名
            if not filename.endswith('.xlsx'):
                filename = f"{filename}.xlsx"

            output_path = self.output_dir / filename

            # 导出到Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, data in data_dict.items():
                    if data:
                        df = pd.DataFrame(data)
                        df['导出时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

                        # 设置列宽
                        worksheet = writer.sheets[sheet_name]
                        self._auto_adjust_column_width(worksheet, df)

            logger.info(f"多工作表数据导出成功: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"导出多工作表Excel失败: {e}", exc_info=True)
            raise

    def _auto_adjust_column_width(self, worksheet, df: pd.DataFrame):
        """
        自动调整Excel列宽

        Args:
            worksheet: openpyxl工作表对象
            df: DataFrame对象
        """
        try:
            import openpyxl
            from openpyxl.utils import get_column_letter

            # 遍历所有列
            for idx, col in enumerate(df.columns, 1):
                # 获取列名长度
                max_length = len(str(col)) + 2

                # 获取该列所有值的最大长度
                for value in df[col]:
                    value_length = len(str(value))
                    if value_length > max_length:
                        max_length = value_length

                # 设置列宽（限制最大宽度）
                column_width = min(max_length, 50)
                worksheet.column_dimensions[get_column_letter(idx)].width = column_width

        except Exception as e:
            logger.warning(f"自动调整列宽失败: {e}")

    def validate_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        验证并清洗数据

        Args:
            data: 原始数据

        Returns:
            清洗后的数据
        """
        validated_data = []

        for item in data:
            try:
                # 移除None值，替换为空字符串
                cleaned_item = {
                    k: (v if v is not None else '')
                    for k, v in item.items()
                }
                validated_data.append(cleaned_item)
            except Exception as e:
                logger.warning(f"数据验证失败，跳过该条记录: {e}")
                continue

        logger.info(f"数据验证完成，有效记录: {len(validated_data)}/{len(data)}")
        return validated_data


class CSVExporter:
    """CSV导出器（备选方案）"""

    def __init__(self):
        self.output_dir = Config.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        data: List[Dict[str, Any]],
        filename: str
    ) -> str:
        """
        导出数据到CSV

        Args:
            data: 要导出的数据列表
            filename: 文件名（不需要扩展名）

        Returns:
            str: 导出文件的完整路径
        """
        if not data:
            raise ValueError("没有数据可导出")

        try:
            logger.info(f"准备导出 {len(data)} 条记录到CSV...")

            # 转换为DataFrame
            df = pd.DataFrame(data)

            # 添加导出时间戳
            df['导出时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 生成文件名
            if not filename.endswith('.csv'):
                filename = f"{filename}.csv"

            output_path = self.output_dir / filename

            # 导出到CSV
            df.to_csv(output_path, index=False, encoding=Config.CSV_ENCODING)

            logger.info(f"CSV数据导出成功: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"导出CSV失败: {e}", exc_info=True)
            raise
