'''
# System --> Windows & Python3.10.0
# File ----> log_colour.py
# Author --> Illusionna
# Create --> 2024/11/28 15:00:02
'''
# -*- Encoding: UTF-8 -*-


import os
import logging

os.makedirs('cache', exist_ok=True)

# 定义日志颜色字典。
COLOR_ASCII = {
    'DEBUG': '\033[94m',
    'INFO': '\033[92m',
    'WARNING': '\033[95m',
    'ERROR': '\033[93m',
    'CRITICAL': '\033[91m'
}

COLOR_RESET = '\033[0m'


class ColorFormatter(logging.Formatter):
    """普通子类：定义日志颜色格式。

    Args:
        logging (_type_): 继承 `"logging.Formatter"` 标准库父类。
    """

    def format(self, record: logging.LogRecord) -> str:
        """公有成员函数：格式配置。

        Args:
            record (logging.LogRecord): 日志记录。

        Returns:
            str: 返回带颜色的字符串。
        """
        log_color = COLOR_ASCII.get(record.levelname, '')
        formatted_message = super().format(record)
        return f'{log_color}{formatted_message}{COLOR_RESET}'


def create_logging(log_path: str) -> logging.Logger:
    """普通函数：创建一个日志对象。

    Args:
        log_path (str): 日志保存路径。

    Returns:
        logging.Logger: 返回日志对象。
    """
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)

        colored_formatter = ColorFormatter(
            fmt = '%(asctime)s:%(msecs)03d - %(levelname)s - %(message)s',
            datefmt = '%Y-%m-%d %H:%M:%S'
        )

        plain_formatter = logging.Formatter(
            fmt = '%(asctime)s:%(msecs)03d - %(levelname)s - %(message)s',
            datefmt = '%Y-%m-%d %H:%M:%S'
        )

        stream_handler.setFormatter(colored_formatter)
        file_handler.setFormatter(plain_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger