import re
import sys

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent, GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Friend, Group, MemberPerm
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from plugins.FurName import get_name
from arclet.alconna import Alconna
from util.initializer import setting
from util.parseTool import parse_msg_type, parse_prefix
from util.initializer import setting
from arclet.alconna import Alconna
from graia.ariadne.util.saya import listen
from loguru import logger as l

sys.path.append("../")

channel = Channel.current()

data = setting["plugin"]["KeywordAnswer"]
alcn = {
    i[0]: Alconna(i[0].replace("Alconna:", ""))
    for i in data["react"]
    if i[0].startswith("Alconna:")
}


@channel.use(ListenerSchema(listening_events=parse_msg_type("KeywordAnswer")))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain

    def get_qq_name(obj):
        return obj.nickname if hasattr(obj, "nickname") else obj.name

    def get_id(obj):
        return obj.group.id if hasattr(obj, "group") else None

    if (
        not message[Plain]
        or ignore(message.display, data["ignore"])
        or event.sender.id == app.account
        or "Aldotai" in get_qq_name(event.sender)
        or get_id(event.sender) in data["ignore_group"]
    ):
        return
    ret = ""
    for ii in data["react"]:
        if ii[0].startswith("Alconna:") and not ignore(
            message.display, data["alconna"]
        ):
            ret = alcn[ii[0]].parse(message.display)
            if ret.matched:
                await app.send_message(
                    friend,
                    MessageChain(Plain(replace_msg(ii[1], ret.header))),
                )
        if ii[0].find(":") == -1 and eval(ii[0], globals(), locals()):
            msg = eval(ii[1], globals(), locals())
            await app.send_message(
                friend,
                MessageChain(Plain(msg)),
            )
        if ii[0].startswith("Exec:"):
            exec(ii[0].replace("Exec:", ""), globals(), globals())
            if f(message.display.lower()):
                msg = eval(ii[1], globals(), locals())
                await app.send_message(
                    friend,
                    MessageChain(Plain(msg)),
                )


def ignore(s: str, db: list):
    for ii in db:
        if (
            "Reg:" in ii
            and re.search(ii.replace("Reg:", ""), s).span() != (0, 0)
            or s.find(ii) == 0
        ):
            l.debug(
                "Reg:{}\t{},Find:{}".format(
                    "Reg:" in ii
                    and re.search(ii.replace("Reg:", ""), s).span() != (0, 0),
                    ii.replace("Reg:", ""),
                    s.find(ii),
                )
            )
            return True
    return False


def replace_msg(s: str, d: dict):
    for ii in d:
        s = s.replace("{" + ii + "}", d[ii])
    return s


alcn2 = Alconna("关键字开关", parse_prefix("KeywordAnswer"))


@listen(GroupMessage)
async def configure(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    global data
    message = event.message_chain
    if not message[Plain]:
        return
    if alcn2.parse(message[Plain]).matched:
        if (
            event.sender.permission != MemberPerm.Member
            or event.sender.id in setting["admins"]
        ):
            if event.sender.group.id in data["ignore_group"]:
                setting["plugin"]["KeywordAnswer"]["ignore_group"].pop(
                    setting["plugin"]["KeywordAnswer"]["ignore_group"].index(
                        event.sender.group.id
                    )
                )
                send = "已开启关键字回复"
            else:
                setting["plugin"]["KeywordAnswer"]["ignore_group"].append(
                    event.sender.group.id
                )
                send = "已关闭关键字回复"
            data = setting["plugin"]["KeywordAnswer"]
        else:
            send = "你非管理员"
        await app.send_message(
            friend,
            MessageChain(Plain(send)),
        )
