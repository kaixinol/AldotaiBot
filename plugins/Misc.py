from random import choice

from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from loguru import logger

from util.initializer import setting
from util.spider import Session

channel = Channel.current()
data = setting["plugin"]["Misc"]
spider = Session("Misc")


@channel.use(SchedulerSchema(timers.every_custom_hours(1)))
async def auto_get_cookie():
    if not setting["plugin"]["ShouYunJi"]["disabled"]:
        syj_data = setting["plugin"]["ShouYunJi"]
        if (
                await spider.get_json(
                    "https://cloud.foxtail.cn/api/account/state",
                    cookie=setting["plugin"]["ShouYunJi"]["cookie"],
                )
        )["code"] != "11100":
            logger.warning("Cookie已经丢失，正在尝试重新获取中……")
            setting["plugin"]["ShouYunJi"]["cookie"] = await spider.get_cookie(
                "https://cloud.foxtail.cn/api/account/login",
                kw={
                    "account": syj_data["account"],
                    "password": syj_data["password"],
                    "model": "1",
                    "token": syj_data["token"],
                },
            )
            logger.info(setting["plugin"]["ShouYunJi"]["cookie"])


@channel.use(SchedulerSchema(timers.every_custom_hours(12)))
async def rd_msg(app: Ariadne):
    rand_group = await app.get_group_list()
    send_group = choice(rand_group)
    send_msg = data["message"]
    await app.send_group_message(send_group, choice(send_msg))
