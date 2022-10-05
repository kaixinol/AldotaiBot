import sqlite3
import base64
import emoji
from loguru import logger as l
global dbLink
dbLink = {}


def Decode(s: str):
    if '.' not in s:
        return base64.standard_b64decode(s.encode()).decode()
    else:
        return s


def Encode(s: str):
    return base64.standard_b64encode(s.encode()).decode()


def Execute(name: str, s: str) -> dict | str:
    l.info(f"[SQL]\t{s}")
    return dbLink[name].cursor().execute(s)


def Connect(s: str):
    if s not in dbLink:
        dbLink[s] = sqlite3.connect(s)


def Commit(s: str):
    dbLink[s].commit()


def CloseAll():
    for i in dbLink.keys():
        dbLink[i].commit()
        dbLink[i].close()
    dbLink = {}


def InsertTable(db: str, name: str, cmd: dict) -> bool:
    ls = [(k, v) for k, v in cmd.items() if v is not None]
    sentence = f'INSERT INTO  {name} (' + ','.join([i[0] for i in ls]) +\
        ') VALUES (' + ','.join(repr(i[1]) for i in ls) + ');'
    try:
        Execute(db, sentence)
        return True
    except:
        return False


def UpdateTable(db: str, name: str, struct: dict) -> bool:
    cmd = f"DELETE FROM {name} WHERE {struct['select'][0]} = {struct['select'][1]};"
    Execute(db, cmd)
    InsertTable(db, name, struct['data'])


def CreateTable(db: str, name: str, struct: dict) -> bool:
    def qParser(n): return {'str': ' TEXT NOT NULL',
                            'int': ' INT NOT NULL'}[n]
    cmd = f"CREATE TABLE IF NOT EXISTS {name}("+','.join([i+qParser(struct[i])
                                                          for i in struct.keys()])+');'
    Execute(db, cmd)


def SearchData(db: str, table: str, column: list | dict | str = '*') -> list | dict:
    if type(column) == list:
        cmd = f"SELECT {', '.join(column)} FROM {table};"
    elif type(column) == str:
        cmd = f"SELECT {column} FROM {table};"
    elif type(column) == dict:
        cmd = f"SELECT {'*' if 'select' not in column else column['select']} FROM {table} WHERE {list(column['data'].keys())[0]} LIKE '{list(column['data'].values())[0]}';"
        return TupleToList(Execute(db, cmd))
    return parseDataToDict(Execute(db, cmd), column)


def parseDataToDict(data: list, key: list | str) -> dict:
    ret = {}
    if not type(key) == str:
        for i in data:
            for num in range(len(key)):
                ret[key[num]] = [] if key[num] not in ret else ret[key[num]]
                ret[key[num]].append(emoji.emojize(
                    Decode(i[num])) if type(i[num]) == str else i[num])
        return ret
    else:
        return TupleToList(data)


def TupleToList(s: list):
    ret2 = []
    for i in s:
        if type(i) == tuple:
            for ii in i:
                ret2.append(emoji.emojize(
                    Decode(ii)) if type(ii) == str else ii)
    return ret2


if __name__ == "__main__":
    Connect('1.db')
    CreateTable('1.db', 'furry', {'QQ': 'int', '圈名': 'str'})
    InsertTable('1.db', 'furry', {'QQ': 114514,
                '圈名': Encode(emoji.demojize('我测你们🐴'))})
    InsertTable('1.db', 'furry', {'QQ': 114, '圈名': Encode('dcfh')})
    UpdateTable('1.db', 'furry', struct={'select': [
        'QQ', 114514], 'data': {'QQ': 114514, '圈名': Encode('阿斯奇琳')}})
    InsertTable('1.db', 'furry', {'QQ': 114514, '圈名': Encode('我草.jpg')})
    l.debug(SearchData('1.db', "furry", ['qq', '圈名']))
    l.debug(SearchData('1.db', "furry", {
        'select': '圈名', 'data': {'qq': 114514}}))
