from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from util.sqliteTool import sqlLink
from graia.ariadne.app import Ariadne
from graia.saya import Channel
from loguru import logger as l

channel = Channel.current()


@channel.use(SchedulerSchema(timers.every_custom_minutes(3)))
async def every_minute_speaking(app: Ariadne):
    l.info('COMMIT')
    sqlLink.CommitAll()
