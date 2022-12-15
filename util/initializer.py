from loguru import logger

from util.jsonTool import read_json

setting = read_json("./config.json5")
keyword = setting["keyword_ignore"]
logger.info("config.json read")
