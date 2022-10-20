from graia.ariadne.event.message import GroupMessage, FriendMessage
from util.initializer import ReadConfig


def parseMsgType(config: str) -> list:
    config = ReadConfig(config)
    ret = []
    if 'Group' in config['process']:
        ret.append(GroupMessage)
    if 'Friend' in config['process']:
        ret.append(FriendMessage)
    return ret


def parsePrefix(config: str) -> list | None:
    config = ReadConfig(config)
    if 'prefix' not in config:
        return None
    else:
        return config['prefix']
