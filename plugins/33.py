from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Friend, Group
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya.event import SayaModuleInstalled
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema

channel = Channel.current()


@channel.use(SchedulerSchema(timers.every_minute()))
async def every_minute_speaking(app: Ariadne):
    pass
