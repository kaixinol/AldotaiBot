import loguru

from util.jsonTool import create_json, read_json

setting = read_json("./config.json5")
loguru.logger.info("config.json read")


def save_config():
    create_json("config.json5", setting)
