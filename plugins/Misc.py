from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from util.sqliteTool import sqlLink
from graia.ariadne.app import Ariadne
from graia.saya import Channel
from loguru import logger as l
from graia.ariadne.util.saya import decorate, dispatch, listen
from graia.ariadne.event.mirai import NudgeEvent
from graia.ariadne.model import Friend, Group
from graia.ariadne.message.chain import MessageChain, Plain
from random import randint
from util.initializer import ReadConfig


channel = Channel.current()


@channel.use(SchedulerSchema(timers.every_custom_minutes(30)))
async def every_minute_speaking(app: Ariadne):
    l.info('COMMIT')
    sqlLink.CommitAll()


@channel.use(SchedulerSchema(timers.every_custom_hours(randint(1, 4))))
async def TRCX(app: Ariadne):
    rand_group = (await app.get_group_list())
    send_group = rand_group[randint(0, len(rand_group)-1)]
    send_msg = ReadConfig('Misc')['message']
    await app.send_group_message(send_group, send_msg[randint(0, len(send_msg)-1)])
