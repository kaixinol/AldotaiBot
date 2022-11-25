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
from graia.saya.event import SayaModuleInstalled
from loguru import logger as l
from graia.ariadne.util.saya import decorate, dispatch, listen


from util.initializer import *
from util.parseTool import *

sys.path.append("../")
saya = Saya.current()

channel = Channel.current()
alcn = Alconna("在线编译{lang}", headers=parsePrefix("OnlineCompile"))


@channel.use(ListenerSchema(listening_events=parseMsgType("OnlineCompile")))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if len(message[Plain]) == 0:
        return
    dic = alcn.parse(message[Plain][0].text.splitlines()[0]).header
    if not dic:
        return
    if type(friend) == Group:
        await app.send_message(
            friend, MessageChain(Plain("加好友后才能使用本功能")), quote=message[Source][0]
        )
        return
    infos = ""
    try:
        buffer = message[Plain][0].text.find("\n")
        text = message[Plain][0].text
        l.info(text)
        raw_info = Compile(text[buffer:], dic["lang"], ReadConfig("OnlineCompile"))

        for index in raw_info:
            infos += index
        infos = infos[:512]
    except Exception as e:
        infos = str(e)
    finally:
        if infos.count("\n") > 8 or len(infos) > 256:
            await app.send_message(
                friend,
                MessageChain(
                    Forward(
                        [
                            ForwardNode(
                                event.sender,
                                datetime.datetime(2022, 1, 14, 5, 14, 1),
                                MessageChain(infos),
                                "阿尔多泰Aldotai",
                            )
                        ]
                    )
                ),
            )
        else:
            await app.send_message(
                friend,
                MessageChain(infos),
            )


def Compile(script: str, lang: str, config: dict):
    c = pydoodle.Compiler(clientId=config["id"], clientSecret=config["secret"])
    result = c.execute(script, lang)
    return result.output
