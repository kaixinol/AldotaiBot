from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import (
    Plain,
)
from graia.ariadne.model import Group, Friend
from graia.saya import Channel
from arclet.alconna.graia import alcommand
from arclet.alconna import Alconna, Arparma

from util.parseTool import *
from util.sqliteTool import get_name, add_name
from util.initializer import setting, keyword
from util.parseTool import get_id

channel = Channel.current()
data = setting["plugin"]["FurName"]


@alcommand(Alconna("设置圈名{name}", parse_prefix("FurName")), private=False)
async def set_name(app: Ariadne, group: Group, result: Arparma, event: MessageEvent):
    ret_data = add_name(result.header["name"], event.sender.id)
    if not ret_data:
        await app.send_message(
            group,
            MessageChain(Plain("更新圈名成功！(＞x＜) ")),
        )
        return
    if ret_data[0] == "TOO_LONG":
        await app.send_message(group, MessageChain(Plain("你的名字太长了，阿尔多泰记不住！")))
    elif ret_data[0] == "HAS_SAME_NAME":
        await app.send_message(group, MessageChain(Plain(f"你的名字与{ret_data[1]}重名")))


@alcommand(Alconna("我是谁"), private=True)
async def set_name(app: Ariadne, group: Group | Friend, event: MessageEvent):
    name = get_name(event.sender.id)
    if not name:
        await app.send_message(group, MessageChain(Plain("你是……咦，我不知道你是谁")))
    elif get_id(event.sender) not in keyword:
        await app.send_message(
            group,
            MessageChain(Plain(f"你是{name}!")),
        )
        return


@alcommand(Alconna("我是{name}"), private=True)
async def repeat(
    app: Ariadne, group: Group | Friend, result: Arparma, event: MessageEvent
):
    if (
        not any([i in event.message_chain.display for i in data["alconna"]])
        and get_id(event.sender) not in keyword
    ):
        await app.send_message(
            group, MessageChain(Plain(f"你好{result.header['name']}!"))
        )
