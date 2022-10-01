from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya import Channel
from graia.ariadne.model import Group, Friend
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.app import Ariadne
from graia.saya import Saya, Channel
from graia.saya.event import SayaModuleInstalled
channel = Channel.current()

@channel.use(SchedulerSchema(timers.every_minute()))
async def every_minute_speaking(app: Ariadne):
    pass
