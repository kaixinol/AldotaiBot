from graia.ariadne.event.message import FriendMessage, GroupMessage

from util.initializer import setting


def parse_msg_type(config_name: str) -> list:
    config = setting["plugin"][config_name]
    ret = []
    if "Group" in config["process"]:
        ret.append(GroupMessage)
    if "Friend" in config["process"]:
        ret.append(FriendMessage)
    return ret


def parse_prefix(config_name: str) -> list | None:
    config = setting["plugin"][config_name]
    return None if "prefix" not in config else config["prefix"]
