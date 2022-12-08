from arclet.alconna import Alconna
import datetime
import sys

import pydoodle
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Forward, ForwardNode, Plain, Source
from graia.ariadne.model import Friend, Group
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger as l

from util.initializer import setting
from util.parseTool import *

sys.path.append("../")
saya = Saya.current()

channel = Channel.current()
alcn = Alconna("在线编译{lang}", parse_prefix("OnlineCompile"))
data = setting["plugin"]["OnlineCompile"]


@channel.use(ListenerSchema(listening_events=parse_msg_type("OnlineCompile")))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if not message[Plain]:
        return
    dic = alcn.parse(message[Plain][0].text.splitlines()[0]).header
    if not dic:
        return
    if type(friend) == Group:
        await app.send_message(
            friend, MessageChain(Plain("加好友后才能使用本功能")), quote=event.id
        )
        return
    info = ""
    try:
        buffer = message[Plain][0].text.find("\n")
        text = message[Plain][0].text
        l.info(text)
        raw_info = compile_code(text[buffer:], dic["lang"], data)

        for index in raw_info:
            info += index
        info = info[:512]
        if not info:
            info = "[空]"
    except Exception as e:
        info = str(e)
    finally:
        if info.count("\n") > 8 or len(info) > 256:
            await app.send_message(
                friend,
                MessageChain(
                    Forward(
                        [
                            ForwardNode(
                                event.sender,
                                datetime.datetime(2022, 1, 14, 5, 14, 1),
                                MessageChain(info),
                                "阿尔多泰Aldotai",
                            )
                        ]
                    )
                ),
            )
        else:
            await app.send_message(
                friend,
                MessageChain(info),
            )


def compile_code(script: str, lang: str, config: dict):
    c = pydoodle.Compiler(clientId=config["id"], clientSecret=config["secret"])
    result = c.execute(script, lang)
    return result.output
