from graia.ariadne.message.parser.base import MatchRegex, RegexGroup
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Friend, Group
from graia.ariadne.util.saya import decorate, dispatch, listen
from util.interval import GroupInterval
from util.parseTool import get_id
from util.initializer import keyword
from graia.ariadne.event.message import MessageEvent, GroupMessage, FriendMessage


@listen(GroupMessage, FriendMessage)
@dispatch(
    MatchRegex(
        regex=r"(?<![a-z|.])(?P<owo>([t-z]|0|[m-q]|a)(v|w|a|u|x)([t-z]|0|[m-q]|a))(?![a-z|.])"
    )
)
@decorate(GroupInterval.require(18, 4, send_alert=False))
async def owo(
    app: Ariadne,
    friend: Friend | Group,
    event: MessageEvent,
    count: MessageChain = RegexGroup("owo"),
):
    msg = count.display
    if abs(ord(msg[0]) - ord(msg[2])) in [0, 1] and get_id(event.sender) not in keyword:
        await app.send_message(friend, count)
