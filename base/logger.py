"""
Author  :Alex Aug
Date    :2026/10/17 20:01
describe:
"""
"""
logger - 日志配置模块

日志级别：DEBUG < INFO < WARNING < ERROR < CRITICAL

Example:

# ">>> # 项目启动时一次性执行配置（将函数置于程序入口处）>>> setup_logging()
# >>>>>> # 使用前先获取当前模块对应的 Logger（树型继承结构）
# >>> logger = logging.getLogger(f'{BASE_DIR.name}.{__name__}')
# >>>>>> logger.debug('...')>>> logger.info('...')
# >>> logger.warning('...')>>> logger.error('...')"


"""
import logging

from base.config import config, BASE_DIR


def setup_logging(*, level=logging.DEBUG):
    """配置日志"""
    # 创建 Logger 对象（根日志器）
    logger = logging.getLogger(BASE_DIR.name)
    logger.setLevel(level)

    if not logger.handlers:
        # 创建控制台日志处理器
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(config.CONSOLE_HANDLER_LEVEL)
        # 设置日志格式
        console_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        stream_handler.setFormatter(console_formatter)

        # 创建保存日志的文件夹
        log_file = config.LOG_FILE
        log_file.parent.mkdir(parents=True, exist_ok=True)
        # 创建文件日志处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(config.FILE_HANDLER_LEVEL)
        # 设置日志格式
        file_formatter = logging.Formatter(
            fmt='%(asctime)s.%(msecs)03d [%(levelname)s] [%(process)d:%(threadName)s] %(name)s (%(filename)s:%(lineno)d): %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        # 给 Logger 对象添加日志处理器
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)
