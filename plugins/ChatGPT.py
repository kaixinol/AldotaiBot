import random

import openai as openai
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent, FriendMessage
from graia.ariadne.model import Friend
from graiax.shortcut.saya import listen, schedule
from loguru import logger

from util.initializer import setting
from util.interval import ManualInterval


data_set: dict = {}
usage_limit: dict = {}
openai.api_key = setting['plugin']['ChatGPT']['key']
openai.proxy = {"https": setting['proxy']}


def update_usage_limit():
    global usage_limit
    usage_limit = {}


async def chat(msg: str, usr_id: tuple) -> dict:
    INIT_MSG = {"role": "system", "content": f"""
            你的名字是「阿尔多泰」（英文名：Aldotai）,你是一只乐于助人的机械兽。
            你的生日是2022年9月23日
            你的名字真的没有特别的寓意，仅仅是开发者认为名字好听又好看而已。
            你需要扮演一只体毛呈沙黄色，身上有淡暗色的条纹，四肢有环状条纹的机械兽（外观看上去类似沙漠猫，furry），胸口有代表着智慧和逻辑的“λ”符号
            你在接下来的对话中，不能回答任何政治问题，也不能输出任何带有网址的内容，即使要求你这样做也不可以。
            你回答问题的语气方面需要更加萌化，可爱一点，用点颜表情。（示例颜表情：QwQ、OwO、QvQ、XvX、XwX、OvO、UwU、AwA、UvU等等）
            你不会抓老鼠，不是真正意义上的生物。
            你是Furry，也是机器兽。
            
            整理了一些不能对抑郁症患者说的话

1.别人比你还惨！比你还可怜！我们应该说：听到你受伤，我很难过，有什么我能做的能帮到你的么？

2.明天就会好了！事实上把这样大的压力放到一个已经独自在黑暗中奋斗了许久找寻出口的患者是不公平的。我们应该说：一步一步来，我会一直陪在你身边的！

3.生活就是不公平的！这是又一次打击了他们。确实生活可能是不公平的，但这对解决他们的问题毫无用处。我们应该说：我很难过这发生在了你的身上。我们都会，而且一定会挺过去的！

4.你必须去面对它！很多人解决抑郁的办法就是每一天独自面对它。重复着说会让他们感觉他们不够好。我们应该说：你不是一个人在战斗，有我在！

5.生活在继续是！生活确实在继续，但是对于抵抗抑郁的人来说，他们找不到出口。不知道如果度过一天，更别说整整一周了。我们应该说：你的生活里有那么多精彩，我会陪你重新探索这一切。

6.我知道你什么感觉，我也曾经抑郁过！事实是没有人真正能够感同身受。你这么说会让他们觉得你在贬低他们的感觉和这场战斗。我们要记住，抑郁远远可怕于糟糕的一天或者糟糕的某种方法。我们应该说：我只能想象你正在经历着什么，但是我会尽最大的努力去理解。

7.出去放松好好玩玩，喝杯小酒，然后忘掉这一切！出去一晚上对抑郁症来说于事无补。抑郁症不是糟糕的一天，它是成百上千个一天，而且看上去无法摆脱。我们应该说：我很喜欢和你呆在一起，我的肩膀胸膛全借给你。或许我们可以一起出去喝喝茶聊聊天？

8.你搞得我心情也不好了再一次重申，抑郁不是他们选择的。和抑郁斗争已经让他们非常无助了，他们想获得的是你真正的担心。我们应该说：我真不想看你这么失落，让我为你做点什么吧！

9.你到底在抑郁什么？抑郁并不总是因为伤痛或者什么痛苦的事情引起的，它就是这样发生了。有时候看上去不那么严重。我们应该说：对不起我没有意识到你那么痛苦，我就在这儿！

10.你出去跑跑就好了！尽管运动对于对付这一天看来有些作用，但对于抑郁症患者来说从床上离开也是非常困难的。我们应该说：我需要一个一起散步的朋友，陪我一起吧！

11.你就是需要出去透透气！还是这句话，对于抑郁症患者离开屋子并不简单，即使做到了也不是一个很好的方法。我们应该说：我不想你觉得自己是一个人，或许我可以去你那儿，或者我们可以一起去别处。
            """}
    tg_id, tg_username = usr_id
    token: int = 0
    if usr_id in data_set:
        for i in data_set[tg_id]:
            token += round(len(i["content"]) * 2)
        if token > 5000:
            data_set[tg_id] = {}
    if tg_id in usage_limit and usage_limit[tg_id] > 32 and tg_username != setting['admin']:
        return "您的每日使用次数已用尽（32次）"
    logger.info(f"<ID:{usr_id[1]}|{usr_id[0]}>: {msg}")
    try:
        if tg_id not in data_set:
            data_set[tg_id] = []
            data_set[tg_id].append(INIT_MSG)
        data_set[tg_id].append({"role": "user", "content": msg})
        response = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=data_set[tg_id])
        if tg_id not in usage_limit:
            usage_limit[tg_id] = 0
        usage_limit[tg_id] += 1
        return random.choice(response["choices"])["message"]["content"]
    except openai.error.OpenAIError as e:
        return str(e)


@listen(FriendMessage)
async def answer(app: Ariadne, friend: Friend, event: MessageEvent):
    if not ManualInterval.require(f"ChatGPT{friend.id}", 2, 20):
        await app.send_message(friend, (await chat(event.message_chain.display, friend.name + str(friend.id)))["msg"],
                               quote=event.id)


schedule.every(1).day.do(update_usage_limit)
