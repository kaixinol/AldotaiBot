from random import randint, choice

from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from loguru import logger

from util.initializer import setting
from util.sqliteTool import session

channel = Channel.current()
data = setting["plugin"]["Misc"]


@channel.use(SchedulerSchema(timers.every_custom_minutes(30)))
async def every_minute_speaking():
    logger.info("COMMIT")
    session.commit()


@channel.use(SchedulerSchema(timers.every_custom_hours(randint(1, 4))))
async def rd_msg(app: Ariadne):
    rand_group = await app.get_group_list()
    send_group = choice(rand_group)
    send_msg = data["message"]
    await app.send_group_message(send_group, choice(send_msg))
