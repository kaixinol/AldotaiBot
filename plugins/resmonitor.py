import sys
import os
sys.path.append('../')
from util.parseTool import *
from util.initializer import *
from graia.ariadne.message.element import (
    Image,
    Plain,
    At,
    Quote,
    AtAll,
    Face,
    Poke,
    Forward,
    App,
    Json,
    Xml,
    MarketFace,
)
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya import Channel
from graia.ariadne.model import Group, Friend
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.app import Ariadne
from pyspectator.computer import Computer
from time import sleep
from pyspectator.convert import UnitByte
from collections.abc import MutableMapping
from graia.saya import Saya, Channel
from graia.saya.event import SayaModuleInstalled


saya = Saya.current()


class Format(object):

    @staticmethod
    def temperature(value):
        formatted_value = ''
        if isinstance(value, (int, float)):
            formatted_value = str(value) + '°C'
        return formatted_value

    @staticmethod
    def byte_value(value):
        formatted_value = ''
        if isinstance(value, (int, float)):
            value, unit = UnitByte.auto_convert(value)
            value = '{:.2f}'.format(value)
            unit = UnitByte.get_name_reduction(unit)
            formatted_value = value + unit
        return formatted_value

    @staticmethod
    def percent(value):
        formatted_value = ''
        if isinstance(value, (int, float)):
            formatted_value = str(value) + '%'
        return formatted_value


async def main(computer):
    data = ''
    data += ('Start monitoring system...')
    data += '\n'+('OS: ' + str(computer.os))
    data += '\n'+('Boot time: {}; Uptime: {}'.format(
        computer.boot_time, computer.uptime
    ))

    data += '\n'+('CPU name: ' + str(computer.processor.name))
    data += '\n'+('Amount of CPU cores: ' + str(computer.processor.count))
    data += '\n'+('CPU load: ' + Format.percent(computer.processor.load))
    data += '\n'+('Hostname: ' + str(computer.hostname))
    data += '\n'+('Network interface: ' + str(computer.network_interface.name))
    data += '\n'+('MAC: ' + str(computer.network_interface.hardware_address))
    data += '\n'+('IP: {}; Mask: {}; Gateway: {}'.format(
        computer.network_interface.ip_address,
        computer.network_interface.subnet_mask,
        computer.network_interface.default_route
    ))
    # Display virtual memory info
    data += '\n'+('Virtual memory: use {} from {}, {}'.format(
        Format.byte_value(computer.virtual_memory.available),
        Format.byte_value(computer.virtual_memory.total),
        Format.percent(computer.virtual_memory.used_percent)
    ))
    # Display nonvolatile memory info
    output_format1 = '{:_^16}{:_^16}{:_^16}{:_^16}{:_^16}'
    output_format2 = '{: ^16}{: ^16}{: ^16}{: ^16}{: ^16}'
    data += '\n'+(output_format1.format('Device',
                  'Total', 'Use', 'Type', 'Mount'))
    for dev in computer.nonvolatile_memory:
        output_text = output_format2.format(
            dev.device,
            Format.byte_value(dev.total),
            Format.percent(dev.used_percent),
            dev.fstype,
            dev.mountpoint
        )
        data += '\n'+(output_text)
    sleep(1)
    return data


channel = Channel.current()


async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")


@channel.use(ListenerSchema(listening_events=parseMsgType(ReadConfig('resmonitor'))))
async def setu(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    message = event.message_chain
    from arclet.alconna import Alconna
    if Alconna("获取配置", headers=parsePrefix('resmonitor')).parse(message[Plain]).matched:
        data = await main(Computer())
        await app.send_message(
            friend,
            MessageChain(Plain(data)),
        )
