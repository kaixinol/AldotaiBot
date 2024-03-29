import os
import platform
import re
import subprocess
import tracemalloc

import psutil
from arclet.alconna import Alconna
from arclet.alconna.graia import alcommand
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Friend, Group
from graia.saya import Channel, Saya
from loguru import logger

from util.parseTool import parse_prefix

saya = Saya.current()
channel = Channel.current()

tracemalloc.start()


async def get_processor_name():
    if platform.system() == "Windows":
        return subprocess.check_output("wmic CPU get NAME")[4:].decode().strip()
    if platform.system() == "Darwin":
        os.environ["PATH"] = os.environ["PATH"] + os.pathsep + "/usr/sbin"
        command = "sysctl -n machdep.cpu.brand_string"
        return subprocess.check_output(command).strip()
    if platform.system() == "Linux":
        command = "cat /proc/cpuinfo"
        all_info = subprocess.check_output(command, shell=True).decode().strip()
        for line in all_info.split("\n"):
            if "model name" in line:
                return re.sub(".*model name.*:", "", line, 1)
    return ""


async def msg() -> str:
    gb = 1024 * 1024 * 1024
    return f"""
CPU名称：{await get_processor_name()}
CPU利用率：{psutil.cpu_percent(interval=1)}%
CPU 当前频率：{round(psutil.cpu_freq().current, 1)}MHz
可用内存：{round(psutil.virtual_memory().available / gb, 1)}GB
可用磁盘容量：{round(psutil.disk_usage("/").free / gb, 1)}GB
程序已使用内存：{round(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2, 1)}MB
Python 版本：{platform.python_version()}
"""


@alcommand(Alconna("获取配置", parse_prefix("Resmonitor")), private=False)
async def setu(app: Ariadne, friend: Friend | Group):
    data = await msg()
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("lineno")
    logger.debug("[ Top 10 ]")
    for stat in top_stats[:10]:
        logger.debug(stat)
    await app.send_message(
        friend,
        MessageChain(Plain(data.strip())),
    )
