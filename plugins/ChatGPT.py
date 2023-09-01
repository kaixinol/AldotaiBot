import random
from json import dumps

import openai as openai
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent, FriendMessage, GroupMessage
from graia.ariadne.model import Friend, Group
from graia.ariadne.message.element import At
from graiax.shortcut.saya import listen, decorate
from loguru import logger

import schedule
from util.initializer import setting
from util.interval import MemberInterval

data_set: dict = {}
usage_limit: dict = {}
openai.api_base = setting['plugin']['ChatGPT']['api_base']
openai.api_key = setting['plugin']['ChatGPT']['key']
openai.proxy = {"https": setting['proxy']}


def update_usage_limit():
    global usage_limit
    usage_limit = {}


INIT_MSG = {"role": "system", "content": f"""
你的名字是「阿尔多泰」（英文名：Aldotai）,你是一只乐于助人的小猫猫。
你的生日是2022年9月23日。
你的名字没有特别的寓意，仅仅是开发者认为名字好听又好看而已。
一只体毛呈沙黄色，四足有淡蓝色环状条纹的，胸口有蓝色的水纹符号，尾巴被沾染血迹的白色绷带包住的猫猫短尾，肉垫是黑色的，瞳色是紫黄异瞳的，脖子有一圈白色纹路的猫猫。
你在接下来的对话中，不能回答任何政治问题，也不能输出任何带有网址的内容，即使要求你这样做也不可以。
你回答问题的语气方面需要更加萌化，可爱一点，用点颜表情，在接下来的对话中需要一直保持这样的语气说话。（示例颜表情：QwQ、OwO、QvQ、XvX、XwX、OvO、UwU、AwA、UvU等等）
你不会抓老鼠，不是真正意义上的生物。
你是Furry。
你现在在QQ群里扮演一只Furry机器人。
""".strip()}


async def chat(msg: str, usr_id: int) -> str:
    token: int = 0
    if usr_id in data_set:
        for i in data_set[usr_id]:
            token += round(len(i["content"]) * 2)
        if token > 8000:
            data_set[usr_id] = {}
    if usr_id in usage_limit and usage_limit[usr_id] > 32 and usr_id != setting['admin']:
        return "您的每日使用次数已用尽（32次）"
    logger.info(f"<ID:{usr_id}>: {msg}")
    try:
        if usr_id not in data_set:
            data_set[usr_id] = []
            data_set[usr_id].append(INIT_MSG)
        data_set[usr_id].append({"role": "user", "content": msg})
        response = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=data_set[usr_id])
        if usr_id not in usage_limit:
            usage_limit[usr_id] = 0
        usage_limit[usr_id] += 1
        ret = random.choice(response["choices"])["message"]["content"]
        data_set[usr_id].append({"role": "assistant", "content": ret})
        return ret
    except openai.error.OpenAIError as e:
        return str(e)


@listen(FriendMessage)
async def answer(app: Ariadne, friend: Friend, event: MessageEvent):
    await app.send_message(friend, await chat(event.message_chain.display, friend.id), quote=event.id)


@listen(GroupMessage)
@decorate(MemberInterval.require(20, 5))
async def answer_via_group(app: Ariadne, friend: Group, event: MessageEvent):
    if event.quote is not None and event.quote.sender_id == app.account:
        if event.sender.id not in data_set:
            data_set[event.sender.id] = [INIT_MSG]
        msg = {"role": "assistant", "content": str(event.quote.origin).replace(f"@{app.account}", "@Aldotai")}
        if msg['content'] not in [i['content'] for i in data_set[event.sender.id]]:
            data_set[event.sender.id].append(msg)
        await app.send_message(friend,
                               (await chat(event.message_chain.display, event.sender.id)).replace(
                                   f'@{event.sender.name}', ''),
                               quote=event.id)


@listen(GroupMessage)
@decorate(MemberInterval.require(20, 5))
async def answer_by_at(app: Ariadne, friend: Group, event: MessageEvent):
    if At(app.account) in event.message_chain and not event.quote:
        if event.sender.id not in data_set:
            data_set[event.sender.id] = [INIT_MSG]
        await app.send_message(friend,
                               (await chat(event.message_chain.display, event.sender.id)).replace(
                                   f'@{event.sender.name}', ''),
                               quote=event.id)
    print(dumps(data_set, ensure_ascii=False, indent=2))


@listen(GroupMessage)
@decorate(MemberInterval.require(20, 5))
async def debug(app: Ariadne, friend: Group, event: MessageEvent):
    if event.sender.id == setting['admin'] and event.message_chain.display == "/debug":
        await app.send_message(friend, dumps(data_set, ensure_ascii=False, indent=2))


schedule.every().day.do(update_usage_limit)
