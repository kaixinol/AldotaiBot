import re
import sys

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Friend, Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger as l
from plugins.FurName import getName
from util.initializer import *
from util.parseTool import parseMsgType, parsePrefix

sys.path.append("../")


channel = Channel.current()
from arclet.alconna import Alconna

data = ReadConfig("KeywordAnswer")
alcn = dict()
for i in data["react"]:
    if i[0].startswith("Alconna:"):
        alcn[i[0]] = Alconna(i[0].replace("Alconna:", ""))


@channel.use(ListenerSchema(listening_events=parseMsgType("KeywordAnswer")))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if (
        not message[Plain]
        or ignore(message.display, ReadConfig("KeywordAnswer")["ignore"])
        or event.sender == app.account
    ):
        return
    ret = ""

    for i in data["react"]:
        if i[0].startswith("Alconna:") and not ignore(
            message.display, ReadConfig("KeywordAnswer")["alconna"]
        ):
            Ret = alcn[i[0]].parse(message.display)
            if Ret.matched:
                await app.send_message(
                    friend,
                    MessageChain(Plain(replaceMsg(i[1], Ret.header))),
                )
        if not i[0].startswith("Alconna:") and eval(i[0], globals(), locals()):
            msg = eval(i[1], globals(), locals())
            await app.send_message(
                friend,
                MessageChain(Plain(msg)),
            )


def ignore(s: str, db: list):
    for i in db:
        if (
            "Reg:" in i
            and re.search(i.replace("Reg:", ""), s).span() != (0, 0)
            or s.find(i) == 0
        ):
            l.debug(
                "Reg:{}\t{},Find:{}".format(
                    "Reg:" in i
                    and re.search(i.replace("Reg:", ""), s).span() != (0, 0),
                    i.replace("Reg:", ""),
                    s.find(i),
                )
            )
            return True
    return False


def replaceMsg(s: str, d: dict):
    for i in d:
        s = s.replace("{" + i + "}", d[i])
    return s
