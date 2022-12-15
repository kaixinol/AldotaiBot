from graia.ariadne.event.message import FriendMessage, GroupMessage

from util.initializer import setting


def parse_prefix(config_name: str) -> list | None:
    config = setting["plugin"][config_name]
    return None if "prefix" not in config else config["prefix"]
