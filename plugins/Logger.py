from graia.ariadne.app import Ariadne
from graia.ariadne.event.mirai import (
    BotGroupPermissionChangeEvent,
    BotLeaveEventActive,
    BotLeaveEventKick,
    BotMuteEvent,
)
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger as l
from graia.ariadne.util.saya import listen
from graia.broadcast.builtin.event import ExceptionThrowed

channel = Channel.current()


@listen(BotLeaveEventKick)
async def kick_group(event: BotLeaveEventKick):
    """
    被踢出群
    """
    l.info(f"收到被踢出群聊事件\n群号：{event.group.id}\n群名：{event.group.name}"),


@listen(BotLeaveEventActive)
async def leave_group(event: BotLeaveEventActive):
    """
    主动退群
    """

    l.info(f"收到主动退出群聊事件\n群号：{event.group.id}\n群名：{event.group.name}")


@listen(BotGroupPermissionChangeEvent)
async def permission_change(event: BotGroupPermissionChangeEvent):
    """
    群内权限变动
    """
    l.info(
        f"收到权限变动事件\n群号：{event.group.id}\n群名：{event.group.name}\n权限变更为：{event.current}"
    )


@channel.use(ListenerSchema(listening_events=[BotMuteEvent]))
async def main(app: Ariadne, group: Group, mute: BotMuteEvent):
    l.info(
        f"""
收到禁言事件，已退出该群
群号：{group.id}
群名：{group.name}
操作者：{mute.operator.name} | {mute.operator.id}
"""
    )
    await app.quit_group(group.id)


@listen(ExceptionThrowed)
async def except_handle(event: ExceptionThrowed):
    if isinstance(event.event, ExceptionThrowed):
        return
    l.error(
        f"""\
# 异常事件：
{str(event.event.__repr__())}
# 异常类型：
`{type(event.exception)}`
# 异常内容：
{str(event.exception)}
"""
    )
