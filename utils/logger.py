"""
日志工具模块
提供统一的日志记录功能，支持文件和控制台输出，以及GUI回调
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable

from config import Config


class ColorFormatter(logging.Formatter):
    """彩色日志格式化器"""

    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'

    def format(self, record):
        # 添加颜色
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


class GUILogger(logging.Handler):
    """GUI日志处理器，将日志发送到GUI显示"""

    def __init__(self):
        super().__init__()
        self.callbacks = []

    def add_callback(self, callback: Callable[[str], None]):
        """
        添加日志回调函数

        Args:
            callback: 接收日志消息的回调函数
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[[str], None]):
        """
        移除日志回调函数

        Args:
            callback: 要移除的回调函数
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def emit(self, record):
        """
        发送日志到所有回调函数
        """
        try:
            msg = self.format(record)
            # 移除ANSI颜色代码（GUI不需要）
            msg = msg.replace('\033[36m', '').replace('\033[32m', '') \
                      .replace('\033[33m', '').replace('\033[31m', '') \
                      .replace('\033[35m', '').replace('\033[0m', '')

            # 调用所有回调函数
            for callback in self.callbacks:
                try:
                    callback(msg)
                except Exception:
                    pass
        except Exception:
            self.handleError(record)


class Logger:
    """日志管理器"""

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        获取或创建日志记录器

        Args:
            name: 日志记录器名称，通常使用 __name__

        Returns:
            logging.Logger实例
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        logger.handlers.clear()  # 清除已有的handlers

        # 文件处理器
        if Config.LOG_TO_FILE:
            log_file = Config.LOG_DIR / f"xhs_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColorFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # GUI处理器
        gui_handler = GUILogger()
        gui_handler.setLevel(logging.INFO)
        gui_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        gui_handler.setFormatter(gui_formatter)
        logger.addHandler(gui_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def add_gui_callback(cls, callback: Callable[[str], None]):
        """
        为所有已存在的日志记录器添加GUI回调

        Args:
            callback: 接收日志消息的回调函数
        """
        gui_handler = GUILogger()
        gui_handler.add_callback(callback)

        for logger in cls._loggers.values():
            # 检查是否已经有GUILogger处理器
            has_gui = False
            for handler in logger.handlers:
                if isinstance(handler, GUILogger):
                    handler.add_callback(callback)
                    has_gui = True
                    break

            if not has_gui:
                gui_handler_copy = GUILogger()
                gui_handler_copy.add_callback(callback)
                gui_handler_copy.setFormatter(gui_formatter)
                gui_handler_copy.setLevel(logging.INFO)
                logger.addHandler(gui_handler_copy)


def get_logger(name: str) -> logging.Logger:
    """
    便捷函数：获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger实例
    """
    return Logger.get_logger(name)
