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
from util.sqliteTool import SqlLink
from arclet.alconna import Alconna
import loguru

x = SqlLink("./db/furryData.db", b64=True)
x.create_table("name", {"qq": int, "name": str})

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
        if len(ret.header["name"]) < 12:
            await app.send_message(
                friend,
                MessageChain(Plain(add_name(ret.header["name"], event.sender.id))),
            )
            return
        else:
            await app.send_message(friend, MessageChain(Plain("你的名字太长了，阿尔多泰记不住！")))

    ret = alcn["我是谁"].parse(message[Plain])
    if ret.matched:
        name = get_name(event.sender.id)
        if name == "[未设置圈名]":
            await app.send_message(friend, MessageChain(Plain("你是……咦，我不知道你是谁")))
        else:
            await app.send_message(
                friend,
                MessageChain(Plain(f"你是{name}!")),
            )

        return


def add_name(n: str, qq: int) -> str:
    ret = x.search_data("name", ["qq", "name"])
    ret_dict = x.parse_data_to_dict(ret, ["qq", "name"])
    for i in ret:
        if i == [qq, n]:
            return f"你的圈名已经是{n}了"
        if (
            i[0] == qq
            and safe_index(ret_dict, "qq", qq) == safe_index(ret_dict, "name", n) != -1
        ):
            x.update_table(
                "name", {"select": ["qq", qq], "data": {"qq": qq, "name": n}}
            )
            return f"你的圈名现在是{n}了"
        if i[1] == n and safe_index(ret_dict, "qq", qq) != safe_index(
            ret_dict, "name", n
        ):
            same_name = ret_dict["qq"][ret_dict["name"].index(n)]
            return f"你的圈名与{same_name}重名"
    x.update_table("name", {"select": ["qq", qq], "data": {"qq": qq, "name": n}})
    return f"你的圈名现在是{n}了"


def safe_index(ll: dict, key: str, wt) -> int:
    if key not in ll:
        return -1
    return -1 if wt not in ll[key] else ll[key].index(wt)


def get_name(qq: int) -> str:
    ret = x.search_data("name", {"select": "name", "data": {"qq": qq}})
    return x.to_pure_list(ret)[len(ret) - 1] if len(ret) >= 1 else "[未设置圈名]"


if __name__ == "__main__":
    x = SqlLink("./db/furryData.db", b64=True)
    loguru.logger.debug(add_name("阿尔多泰", 114514))
    loguru.logger.debug(x.search_data("name", ["qq", "name"], require=list))
    loguru.logger.debug(add_name("阿尔多泰", 114))
    loguru.logger.debug(x.search_data("name", ["qq", "name"], require=dict))
    loguru.logger.debug(add_name("阿斯奇琳", 114))
    loguru.logger.debug(x.search_data("name", ["qq", "name"], require=dict))
    loguru.logger.debug(add_name("测你的码", 114))
    loguru.logger.debug(x.search_data("name", ["qq", "name"], require=dict))
    loguru.logger.debug(get_name(114))
    loguru.logger.debug(get_name(115))
