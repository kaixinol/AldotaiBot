import base64
import sqlite3

from loguru import logger as l

pool = {}


@l.catch
class sqlLink:
    def __init__(self, path: str, b64: bool = False):
        self.b64 = b64
        if path not in pool:
            self.link = sqlite3.connect(path)
            pool[path] = self.link
        else:
            self.link = pool[path]

    def Execute(self, s: str) -> sqlite3.Cursor:
        l.info(f"[SQL]\t{s}")
        return self.link.cursor().execute(s)

    def CommitAll():
        for i in pool:
            pool[i].commit()

    def Fetchone(self) -> tuple:
        return self.fetchone()

    def Fetchall(self) -> dict | list:
        return self.fetchall()

    def SearchData(
        self, table: str, column: list | dict | str = "*", require: type = list
    ):
        if type(column) == list:
            cmd = f"SELECT {', '.join(column)} FROM {table};"
        elif type(column) == str:
            cmd = f"SELECT {column} FROM {table};"
        elif type(column) == dict:
            cmd = f"SELECT {'*' if 'select' not in column else column['select']} FROM {table} WHERE {list(column['data'].keys())[0]} LIKE '{list(column['data'].values())[0]}';"
        if require == list:
            return (
                self.__decodeb64(self.Execute(cmd)) if self.b64 else self.Execute(cmd)
            )
        else:
            return self.parseDataToDict(
                self.__decodeb64(self.Execute(cmd)) if self.b64 else self.Execute(cmd),
                column,
            )

    def InsertTable(self, name: str, cmd: dict) -> bool:
        ls = [(k, v) for k, v in cmd.items() if v is not None]
        sentence = (
            (
                f"INSERT INTO  {name} ("
                + ",".join([i[0] for i in ls])
                + ") VALUES ("
                + ",".join(
                    (
                        repr(i[1])
                        if type(i[1]) != str
                        else "'" + self.__encode(i[1]) + "'"
                    )
                    for i in ls
                )
                + ");"
            )
            if self.b64
            else (
                f"INSERT INTO  {name} ("
                + ",".join([i[0] for i in ls])
                + ") VALUES ("
                + ",".join(repr(i[1]) for i in ls)
                + ");"
            )
        )

        self.Execute(sentence)

    def CreateTable(self, name: str, struct: dict) -> bool:
        def qParser(n):
            return {str: " TEXT", int: " INT NOT NULL"}[n]

        cmd = (
            f"CREATE TABLE IF NOT EXISTS {name}("
            + ",".join([i + qParser(struct[i]) for i in struct])
        ) + ");"

        self.Execute(cmd)

    @staticmethod
    def __decode(s: str):
        return base64.standard_b64decode(s.encode()).decode()

    @staticmethod
    def __encode(s: str):
        return base64.standard_b64encode(s.encode()).decode()

    def __decodeb64(self, data: list):
        rzt = []
        for i in data:
            rztB = [self.__decode(ii) if type(ii) == str else ii for ii in i]
            rzt.append(rztB)
        return rzt

    @staticmethod
    def ToPureList(l: list):
        ret = []
        for ii in l:
            ret.extend(iter(ii))
        return ret

    @staticmethod
    def parseDataToDict(data: list, key: list | str) -> dict:
        if type(key) == str:
            return data
        ret = {}
        for i in data:
            for num in range(len(key)):
                ret[key[num]] = [] if key[num] not in ret else ret[key[num]]
                ret[key[num]].append(i[num])
        return ret

    def UpdateTable(self, name: str, struct: dict) -> bool:
        cmd = f"DELETE FROM {name} WHERE {struct['select'][0]} = {struct['select'][1]};"
        self.Execute(cmd)
        self.InsertTable(name, struct["data"])


if __name__ == "__main__":
    l.warning("Created a database whose strings are all base64 encoded")
    x = sqlLink("test1.db", b64=True)
    x.CreateTable("furry", {"QQ": int, "圈名": str, "其他": str})
    x.InsertTable("furry", {"QQ": 114514, "圈名": "测试圈名"})
    x.InsertTable("furry", {"QQ": 114, "圈名": "dcfh"})
    l.debug(x.SearchData("furry", ["QQ", "圈名", "其他"], require=dict))
    l.debug(
        x.ToPureList(x.SearchData("furry", {"select": "圈名", "data": {"qq": 114514}}))
    )
    x.link.commit()
    x.link.close()
    l.warning("Created a database whose strings are all plaintext")
    x = sqlLink("test2.db")
    x.CreateTable("furry", {"QQ": int, "圈名": str, "其他": str})
    x.InsertTable("furry", {"QQ": 114514, "圈名": "测试圈名"})
    x.UpdateTable(
        "furry", {"select": ["QQ", 114514], "data": {"QQ": 114514, "圈名": "阿斯奇琳"}}
    )
    x.InsertTable("furry", {"QQ": 114514, "圈名": "测试圈名"})
    l.debug(x.SearchData("furry", ["QQ", "圈名"], require=dict))
    l.debug(
        x.ToPureList(x.SearchData("furry", {"select": "圈名", "data": {"qq": 114514}}))
    )
    x.link.commit()
    x.link.close()
