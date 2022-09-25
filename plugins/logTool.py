from loguru import *
import datetime
import os

if not os.path.exists(f"./log/{datetime.date.today()}.log"):
    logger.add(
        f"./log/{datetime.date.today()}.log", retention="10 days", rotation="00:00", level="DEBUG", filter=lambda record: record["extra"]["name"] == "botlog" if 'name' in record['extra'] else False)
    logger_a = logger.bind(name="botlog")
else:
    logger_a = logger.bind(name="botlog")


#logger.add("{time: YYYY-MM-DD}.log", rotation="00:00", encoding="utf-8", filter=lambda rec: "graia" not in rec["name"])

# 如果 init 改成这样，当插件和主程序同时调用此模组时，会导致多个log文件建立（重复init？）
'''
logger.add("./log/{time}.log", level="DEBUG", filter=lambda record: record["extra"]["name"] == "botlog" if 'name' in record['extra'] else False)
logger_a = logger.bind(name="botlog")
'''


def c(s: str):
    return s if len(s) == 0 else f'[{s}]\t'


def debug(s: str, type: str = ''):
    logger.debug(f'{c(type)}{s}')


def info(s: str, type: str = ''):
    logger.info(f'{c(type)}{s}')


def err(s: str, type: str = ''):
    logger.error(f'{c(type)}{s}')
