import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, select, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from os import getcwd, mkdir
from os.path import exists
from json import dumps
from loguru import logger
import base64, sqlite3

if not exists("db"):
    mkdir("db")
engine = create_engine(f"sqlite:///./db/furryData.db", echo=True)
logger.info(f"{getcwd()}/db/furryDat.db")
Base = declarative_base()


class Fursona(Base):
    __tablename__ = "fursona"
    qq = Column(Integer, primary_key=True)
    imgJson = Column(String, nullable=False)
    desc = Column(String)


class Name(Base):
    __tablename__ = "name"
    qq = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
session.autocommit = True


def decode(s: str):
    return base64.standard_b64decode(s.encode()).decode()


def encode(s: str):
    return base64.standard_b64encode(s.encode()).decode()


def add_name(name: str, qq: int):
    if len(name) > 12:
        return ("TOO_LONG",)
    temp = (
        session.execute(f"SELECT qq FROM name WHERE name='{encode(name)}'")
        .mappings()
        .all()
    )
    temp1 = [i for i in temp]
    if not temp1 or temp1[0]["qq"] == qq:
        session.execute(f"DELETE FROM name WHERE qq={qq};")
        session.execute(f"INSERT INTO name (name,qq)  VALUES('{encode(name)}',{qq});")
        return None
    return "HAS_SAME_NAME", temp1[0]["qq"]


def add_fursona(img: list, qq: int):
    session.execute(f"DELETE FROM fursona WHERE qq = {qq};")
    session.execute(f"INSERT INTO fursona(imgJson, qq) VALUES ('{dumps(img)}', {qq});")


def add_desc(desc: str, qq: int):
    session.execute(
        f"UPDATE fursona SET desc = '{encode(desc)}' WHERE EXISTS (SELECT * FROM fursona WHERE qq={qq});"
    )


def get_name(qq: int):
    ret = list(session.execute(f"SELECT name FROM name WHERE qq={qq}"))
    if not ret:
        return None
    return decode(ret[0][0])


def get_fursona(name: int | str):
    if isinstance(name, str):
        ret = list(
            session.execute(
                f"SELECT * FROM fursona WHERE qq=(SELECT qq FROM name WHERE name='{encode(name)}');"
            )
        )
    else:
        ret = list(session.execute(f"SELECT * FROM fursona WHERE qq={name}"))
    if not ret:
        return None
    return ret[0]


def get_random_fursona():
    return list(session.execute(f"SELECT * FROM fursona order by RANDOM() LIMIT 1;"))


if __name__ == "__main__":
    # test
    print(get_random_fursona())
    print(add_name("简简单单测个试", 114514))
    print(f"QQ号114514的圈名为{get_name(114514)}")
    add_fursona(["img1.png", "img2.gif"], 114514)
    print(f"QQ号114的兽设资料为{get_fursona(114)}")
    print(f"简简单单测个试的兽设资料为{get_fursona('简简单单测个试')}")
    add_desc("测试", 114514)
    print(f"简简单单测个试的兽设资料为{get_fursona('简简单单测个试')}")
    print(add_name("简简单单测个试", 1919810))
    print(add_name("很" + "长" * 20 + "的名字", 1145141919810))
    add_fursona(["img1.png", "img2.gif"], 1919810)
    print(get_random_fursona())
