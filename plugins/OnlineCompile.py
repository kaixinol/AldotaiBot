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
    ForwardNode
)
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya import Channel
from graia.ariadne.model import Group, Friend
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.app import Ariadne
from graia.saya import Saya, Channel
from graia.saya.event import SayaModuleInstalled
from parseTool import *
from initializer import *
from logTool import *
import pydoodle
import datetime
saya = Saya.current()

channel = Channel.current()


async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")


@channel.use(ListenerSchema(listening_events=parseMsgType(ReadConfig('resmonitor'))))
async def setu(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    message = event.message_chain
    from arclet.alconna import Alconna
    dic = Alconna("在线编译{lang}", headers=parsePrefix(
        'OnlineCompile')).parse(message[Plain][0].text.splitlines()[0]).header
    if not dic:
        return
    infos = ""
    try:
        buffer = message[Plain][0].text.find('\n')
        text = message[Plain][0].text
        info(text)
        raw_info = Compile(text[buffer:], dic['lang'],
                           ReadConfig('OnlineCompile'))

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
                    Forward([ForwardNode(event.sender, datetime.datetime(2022, 1, 14, 5, 14, 1), MessageChain(infos), '阿尔多泰Aldotai')])),
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
