# -*- coding: utf-8 -*-
"""
@ Author     : zhufeng
@ Time       : 2024年01月23日
@ File       : log.py
@ Description: 日志模块
"""
import sys
from datetime import datetime
from loguru import logger
from pathlib import Path

# 确保日志目录存在
log_directory = "logs"
log_date = datetime.now().strftime("%Y-%m-%d")
filename = f'{Path(__file__).stem}-{log_date}.log'
Path(log_directory).mkdir(parents=True, exist_ok=True)
# 日志格式
custom_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " \
                "<level>{level: <8}</level> | " \
                "<level>{thread.name: <10}</level> | " \
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - " \
                "<level>{message}</level>"
# 移除默认的控制台输出
logger.remove()
# 添加文件输出 sink
logger.add(
    # 日志文件路径 文件类对象、字符串、pathlib.Path、可调用对象、协程函数或logging.Handler）- 负责接收格式化的日志消息并将其传播到适当终点的对象。
    sink=(Path(log_directory) / filename),
    # 是否应将待记录的消息先通过一个多进程安全队列，然后再传递到sink。在通过多个进程记录到文件时，这很有用。这还具有使日志调用非阻塞的优点。
    enqueue=True,
    # 从中将日志消息发送到sink的最低严重级别。
    level="INFO",
    # 自动轮转过大的文件
    rotation="15 MB",
    # 一段时间后进行清理
    retention="2 days",
    encoding="utf-8",
    # 是否应扩展异常跟踪格式，以显示生成错误的完整堆栈跟踪，在DEBUG等级下，通常不建议打开backtrace, 可以减少生产环境下的性能开销
    backtrace=True,
    # 是否应显示异常跟踪的变量值，以便于调试。在生产环境中应将其设置为False，以避免泄漏敏感数据。
    diagnose=True,
    compression="zip",
    # format：(str或可调用对象，可选) - 用于在发送到sink之前格式化日志消息的模板。
    format=custom_format,
    # serialize：（bool，可选）- 是否在发送到sink之前首先将日志消息及其记录转换为JSON字符串。
    serialize=False
)
# 添加控制台输出 sink，如果想改变默认的控制台输出格式，添加新的 sink
logger.add(
    sink=sys.stderr,  # 使用标准错误输出(stderr)为例，您也可以选择标准输出(sys.stdout)
    format=custom_format,  # 可以单独为控制台输出设置自定义样式
    level="DEBUG"
)

