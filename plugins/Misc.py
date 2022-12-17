from random import randint, choice

from graia.ariadne.app import Ariadne
from graia.saya import Channel
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema

from util.initializer import setting
from util.spider import Session

channel = Channel.current()
data = setting["plugin"]["Misc"]
spider = Session("Misc")


@channel.use(SchedulerSchema(timers.every_custom_hours(12)))
async def auto_get_cookie(app: Ariadne):
    if (
        await spider.get_json(
            "https://cloud.foxtail.cn/api/account/state",
            cookie=setting["plugin"]["ShouYunJi"]["cookie"],
        )
    )["code"] != "11100":
        setting["plugin"]["ShouYunJi"]["cookie"] = await spider.get_cookie(
            "https://cloud.foxtail.cn/api/account/login",
            kw={
                "account": data["account"],
                "password": data["password"],
                "model": "1",
                "token": data["token"],
            },
        )


@channel.use(SchedulerSchema(timers.every_custom_hours(randint(1, 4))))
async def rd_msg(app: Ariadne):
    rand_group = await app.get_group_list()
    send_group = choice(rand_group)
    send_msg = data["message"]
    await app.send_group_message(send_group, choice(send_msg))
