
from util.initializer import setting


def parse_prefix(config_name: str) -> list | None:
    config = setting["plugin"][config_name]
    return None if "prefix" not in config else config["prefix"]


def get_id(obj):
    return obj.group.id if hasattr(obj, "group") else obj.id
