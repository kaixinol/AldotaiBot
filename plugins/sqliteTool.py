import sqlite3
global dbLink
dbLink = {}


def Execute(name: str, s: str) -> dict | str:
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
        print(sentence)
        Execute(db, sentence)
        return True
    except:
        return False


def UpdateTable(db: str, name: str, struct: dict) -> bool:
    cmd = f"DELETE FROM {name} WHERE {struct['select'][0]} = {struct['select'][1]};"
    print(cmd)
    Execute(db, cmd)
    InsertTable(db, name, struct['data'])


def CreateTable(db: str, name: str, struct: dict) -> bool:
    def qParser(n): return {'str': ' TEXT NOT NULL',
                            'int': ' INT NOT NULL'}[n]
    cmd = f"CREATE TABLE IF NOT EXISTS {name}("+','.join([i+qParser(struct[i])
                                                          for i in struct.keys()])+');'
    print(cmd)
    Execute(db, cmd)


def SearchData(db: str, table: str, column: list | str = '*') -> list | dict:

    if type(column) == list:
        cmd = f"SELECT {', '.join(column)} FROM {table};"
    elif type(column) == str:
        cmd = f"SELECT {column} FROM {table};"
    print(cmd)
    return parseDataToDict(Execute(db, cmd), column)


def parseDataToDict(data: list, key: list | str) -> dict:
    ret = {}
    if not type(key) == str:
        for i in data:
            for num in range(len(key)):
                ret[key[num]] = [] if key[num] not in ret else ret[key[num]]
                ret[key[num]].append(i[num])
    else:
        return [i for i in list(data)]
    return ret


if __name__ == "__main__":
    Connect('1.db')
    CreateTable('1.db', 'furry', {'QQ': 'int', '圈名': 'str'})
    InsertTable('1.db', 'furry', {'QQ': 114514, '圈名': 'dfghcfh'})
    InsertTable('1.db', 'furry', {'QQ': 114, '圈名': 'dcfh'})
    UpdateTable('1.db', 'furry', struct={'select': [
        'QQ', 114514], 'data': {'QQ': 114514, '圈名': 'ffg'}})
    print(SearchData('1.db', "furry", ["qq", "圈名"]))
