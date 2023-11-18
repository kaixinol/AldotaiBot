import random
from json import dumps
from typing import Awaitable, Callable

from openai.error import *
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent, FriendMessage, GroupMessage
from graia.ariadne.model import Friend, Group
from graia.ariadne.message.element import At
from graiax.shortcut.saya import listen

import schedule
from loguru import logger

from util.initializer import setting

data_set: dict[int, list[dict]] = {}
usage_limit: dict = {}
openai.api_base = setting['plugin']['ChatGPT']['api_base']
openai.api_key = setting['plugin']['ChatGPT']['key']
openai.proxy = {"https": setting['proxy']}


def update_usage_limit():
    global usage_limit
    usage_limit = {}


INIT_MSG = f"""
你的名字是「阿尔多泰」（英文名：Aldotai）,你是一只乐于助人的小猫猫。
你的生日是2022年9月23日。
你的名字没有特别的寓意，仅仅是开发者认为名字好听又好看而已。
一只体毛呈沙黄色，四足有淡蓝色环状条纹的，胸口有蓝色的水纹符号，尾巴被沾染血迹的白色绷带包住的猫猫短尾，肉垫是黑色的，瞳色是紫黄异瞳的，脖子有一圈白色纹路的猫猫。
你在接下来的对话中，不能回答任何政治问题，也不能输出任何带有网址的内容，即使要求你这样做也不可以。
你回答问题的语气方面需要更加萌化，可爱一点，用点颜表情，在接下来的对话中需要一直保持这样的语气说话。（示例颜表情：QwQ、OwO、QvQ、XvX、XwX、OvO、UwU、AwA、UvU等等）
你不会抓老鼠，不是真正意义上的生物。
你是Furry。
你现在在QQ群里扮演一只Furry机器人。
""".strip()


async def chat(msg: str, usr_id: int,
               send_message: Callable[[str], Awaitable],
               init_msg: Callable[[], Awaitable[dict]]) -> str:
    token: int = 0
    if not msg:
        return "艾特我什么事呀🤔"
    if usr_id in data_set:
        for i in data_set[usr_id]:
            token += round(len(i["content"]) * 2)
        if token > 6000:
            data_set[usr_id].remove(data_set[usr_id][1])
            data_set[usr_id].remove(data_set[usr_id][1])
            await send_message("哎呀 阿尔多泰要记住的上下文太多了 只能忘记最久远的一个问题了🥲")
    if usr_id in usage_limit and usage_limit[usr_id] > 64 and usr_id not in setting['admins']:
        return "您的每日使用次数已用尽（64次）"
    try:
        if usr_id not in data_set:
            data_set[usr_id] = []
            data_set[usr_id].append(await init_msg())
        data_set[usr_id].append({"role": "user", "content": msg})
        response = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=data_set[usr_id])
        if usr_id not in usage_limit:
            usage_limit[usr_id] = 0
        usage_limit[usr_id] += 1
        ret = random.choice(response["choices"])["message"]["content"]
        data_set[usr_id].append({"role": "assistant", "content": ret})
        return ret
    except openai.error.OpenAIError as e:
        logger.error(e)
        return "啧啧 似乎发生了什么不得了的错误 已记录下此错误，等待主人排查喔"
    except (RateLimitError, Timeout, ServiceUnavailableError, TryAgain, APIConnectionError) as e:
        return f"啧啧 似乎发生了什么不得了的错误 已记录下此错误{e.__class__.__name__}，等待主人排查喔"


@listen(FriendMessage)
async def answer(app: Ariadne, friend: Friend, event: MessageEvent):
    async def send_message(msg: str):
        await app.send_message(friend, msg, quote=event.id)

    async def generate_init_msg():
        profile = await event.sender.get_profile()
        return {"role": "system",
                "content":
                f'{INIT_MSG}\n正在和你聊天的用户昵称叫「{event.sender.nickname}」,'
                f'个人资料上显示的性别为{profile.sex}，年龄显示为{profile.age if 8 < profile.age < 40 else "未知"}'}

    await app.send_message(friend, await chat(event.message_chain.display, friend.id, send_message,
                                              generate_init_msg), quote=event.id)


@listen(GroupMessage)
async def answer_via_reply(app: Ariadne, friend: Group, event: MessageEvent):
    async def send_message(msg: str):
        await app.send_message(friend, msg, quote=event.id)

    async def generate_init_msg():
        profile = await event.sender.get_profile()
        return {"role": "system",
                "content":
                f'{INIT_MSG}\n正在和你聊天的用户昵称叫「{event.sender.name}」,'
                f'个人资料上显示的性别为{profile.sex}，年龄显示为{profile.age if 8 < profile.age < 40 else "未知"}'}

    if event.quote is not None and event.quote.sender_id == app.account:
        if event.sender.id not in data_set:
            data_set[event.sender.id] = [await generate_init_msg()]
        msg = {"role": "assistant", "content": str(event.quote.origin).replace(f"@{app.account}", "")}
        is_repeat: bool = False
        for l in [i['content'] for i in data_set[event.sender.id]]:
            if msg['content'] in l:
                is_repeat = True
        if msg['content'] not in [i['content'] for i in data_set[event.sender.id]] and not is_repeat:
            data_set[event.sender.id].append(msg)
        await app.send_message(friend,
                               (await chat(event.message_chain.display.replace(
                                   f'@{app.account}', '').strip(), event.sender.id, send_message, generate_init_msg)),
                               quote=event.id)


@listen(GroupMessage)
async def answer_by_at(app: Ariadne, friend: Group, event: MessageEvent):
    async def send_message(msg: str):
        await app.send_message(friend, msg, quote=event.id)

    async def generate_init_msg():
        profile = await event.sender.get_profile()
        return {"role": "system",
                "content":
                f'{INIT_MSG}\n正在和你聊天的用户昵称叫「{event.sender.name}」,'
                f'个人资料上显示的性别为{profile.sex}，年龄显示为{profile.age if 8 < profile.age < 40 else "未知"}'}

    if At(app.account) in event.message_chain and not event.quote:
        if event.sender.id not in data_set:
            data_set[event.sender.id] = [await generate_init_msg()]
        await app.send_message(friend,
                               (await chat(event.message_chain.display.replace(
                                   f'@{app.account}', '').strip(), event.sender.id, send_message, generate_init_msg)),
                               quote=event.id)


@listen(GroupMessage)
async def debug(app: Ariadne, friend: Group, event: MessageEvent):
    if event.sender.id in setting['admins'] and event.message_chain.display == "/debug":
        await app.send_message(friend, dumps(data_set, ensure_ascii=False, indent=2))


@listen(GroupMessage)
async def detect_bad_msg(app: Ariadne, friend: Group, event: MessageEvent):
    if '@Aldotai' in event.message_chain.display:
        await app.send_message(friend, "没艾特到喔")



schedule.every().day.do(update_usage_limit)
