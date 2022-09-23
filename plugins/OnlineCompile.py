from graia.ariadne.message.element import Plain
from pydoc import plain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya import Channel
from graia.ariadne.model import Group, Friend
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.app import Ariadne
from graia.saya import Saya, Channel
from graia.saya.event import SayaModuleInstalled
from parseTool import *
from initializer import *
import pydoodle
saya = Saya.current()

channel = Channel.current()


async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")


@channel.use(ListenerSchema(listening_events=parseMsgType(ReadConfig('resmonitor'))))
async def setu(app: Ariadne, friend: Friend | Group,  message: MessageChain):
    try:

        from arclet.alconna import Alconna
        dic = Alconna("在线编译{lang}", headers=parsePrefix(
            'OnlineCompile')).parse(message[Plain][0].text.splitlines()[0]).header
        if not dic:
            return
        buffer = message[Plain][0].text.find('\n')
        text = message[Plain][0].text
        raw_info = Compile(text[buffer:], dic['lang'],
                           ReadConfig('OnlineCompile'))

        info = ""
        for index in raw_info:
            info += index
        info = info[:256]
        if info.count("\n") > 8:
            info = "请勿滥用本bot恶意刷屏"
    except Exception as e:
        info = str(e)
    finally:
        await app.send_message(
            friend,
            MessageChain(
                Plain(info)),
        )


def Compile(script: str, lang: str, config: dict):
    c = pydoodle.Compiler(clientId=config["id"], clientSecret=config["secret"])
    print(f"{script}|{lang}|{config}")
    result = c.execute(script, lang)
    return result.output
