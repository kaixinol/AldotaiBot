import sys

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import (
    Plain,
)
from graia.ariadne.model import Friend, Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from util.parseTool import *
from util.sqliteTool import get_name, add_name
from arclet.alconna import Alconna

alcn = {
    "设置圈名{name}": Alconna("设置圈名{name}", parse_prefix("FurName")),
    "我是谁": Alconna("我是谁"),
}
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=parse_msg_type("FurName")))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if not message[Plain]:
        return
    ret = alcn["设置圈名{name}"].parse(message[Plain])
    if ret.matched:
        ret_data = add_name(ret.header["name"], event.sender.id)
        if not ret_data:
            await app.send_message(
                friend,
                MessageChain(Plain("更新圈名成功！(＞x＜) ")),
            )
            return
        elif ret_data[0] == "TOO_LONG":
            await app.send_message(friend, MessageChain(Plain("你的名字太长了，阿尔多泰记不住！")))
        elif ret_data[0] == "HAS_SAME_NAME":
            await app.send_message(friend, MessageChain(Plain(f"你的名字与{ret_data[1]}")))

    ret = alcn["我是谁"].parse(message[Plain])
    if ret.matched:
        name = get_name(event.sender.id)
        if not name:
            await app.send_message(friend, MessageChain(Plain("你是……咦，我不知道你是谁")))
        else:
            await app.send_message(
                friend,
                MessageChain(Plain(f"你是{name}!")),
            )

        return
