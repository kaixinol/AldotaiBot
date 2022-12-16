from re import MULTILINE, IGNORECASE

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent, GroupMessage, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.base import MatchRegex, RegexGroup
from graia.ariadne.model import Friend, Group
from graia.ariadne.util.saya import decorate, dispatch, listen

from util.initializer import keyword
from util.interval import MemberInterval
from util.parseTool import get_id


@listen(GroupMessage, FriendMessage)
@dispatch(
    MatchRegex(
        regex=r"(.*)(?<![a-z|.])(?P<owo>([t-z]|0|[m-q]|a)(v|w|a|u|x)([t-z]|0|[m-q]|a))(?![a-z|.])(.*)",
        flags=MULTILINE | IGNORECASE,
    )
)
@decorate(MemberInterval.require(10, 3, send_alert=True, alert_time_interval=30))
async def owo(
    app: Ariadne,
    friend: Friend | Group,
    event: MessageEvent,
    count: MessageChain = RegexGroup("owo"),
):
    msg = count.display
    if abs(ord(msg[0]) - ord(msg[2])) in [0, 1] and get_id(event.sender) not in keyword:
        await app.send_message(friend, count)
