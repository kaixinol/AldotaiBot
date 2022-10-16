from graia.ariadne.event.message import GroupMessage, FriendMessage
def parseMsgType(config:dict)->list:
    ret=[]
    if 'Group' in config['process']:
        ret.append(GroupMessage)
    if 'Friend' in config['process']:
        ret.append(FriendMessage)
    return ret
def parsePrefix(config: dict)->list|None:
    if 'prefix' not in config:
        return None
    else:
        return config['prefix']
