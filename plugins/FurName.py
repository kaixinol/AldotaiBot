from arclet.alconna import Alconna
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import (
    Plain,
)
from graia.ariadne.model import Friend, Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from arclet.alconna import Alconna
from arclet.alconna.graia import alcommand
from arclet.alconna import Alconna, Args, Arparma

from util.parseTool import *
from util.sqliteTool import get_name, add_name

alcn = {
    "设置圈名{name}": Alconna("设置圈名{name}", parse_prefix("FurName")),
    "我是谁": Alconna("我是谁"),
}
channel = Channel.current()


@alcommand(Alconna("设置圈名{name}", parse_prefix("FurName")), private=False)
async def set_name(app: Ariadne, group: Group, result: Arparma, event: MessageEvent):
    ret_data = add_name(result.header["name"], event.sender.id)
    if not ret_data:
        await app.send_message(
            group,
            MessageChain(Plain("更新圈名成功！(＞x＜) ")),
        )
        return
    elif ret_data[0] == "TOO_LONG":
        await app.send_message(group, MessageChain(Plain("你的名字太长了，阿尔多泰记不住！")))
    elif ret_data[0] == "HAS_SAME_NAME":
        await app.send_message(group, MessageChain(Plain(f"你的名字与{ret_data[1]}重名")))


@alcommand(Alconna("我是谁"), private=True)
async def set_name(app: Ariadne, group: Group, event: MessageEvent):
    name = get_name(event.sender.id)
    if not name:
        await app.send_message(group, MessageChain(Plain("你是……咦，我不知道你是谁")))
    else:
        await app.send_message(
            group,
            MessageChain(Plain(f"你是{name}!")),
        )
        return


@alcommand(Alconna("我是{name}"), private=True)
async def set_name(app: Ariadne, group: Group, result: Arparma):
    await app.send_message(group, MessageChain(Plain(f"你是{result.header['name']}!")))
