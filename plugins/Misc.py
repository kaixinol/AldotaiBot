from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from util.sqliteTool import SqlLink
from graia.ariadne.app import Ariadne
from graia.saya import Channel
from loguru import logger

from random import randint
from util.initializer import setting

channel = Channel.current()
data = setting["plugin"]["Misc"]


@channel.use(SchedulerSchema(timers.every_custom_minutes(30)))
async def every_minute_speaking():
    logger.info("COMMIT")
    SqlLink.commit_all()


@channel.use(SchedulerSchema(timers.every_custom_hours(randint(1, 4))))
async def rd_msg(app: Ariadne):
    rand_group = await app.get_group_list()
    send_group = rand_group[randint(0, len(rand_group) - 1)]
    send_msg = data["message"]
    await app.send_group_message(send_group, send_msg[randint(0, len(send_msg) - 1)])
