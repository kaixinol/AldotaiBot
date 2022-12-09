import base64
import sqlite3

import loguru

pool = {}


class SqlLink:
    def __init__(self, path: str, b64: bool = False):
        self.b64 = b64
        if path not in pool:
            loguru.logger.info("新连接一个数据库")
            self.link = sqlite3.connect(path)
            pool[path] = self.link
        else:
            self.link = pool[path]

    def exec_sql(self, s: str) -> sqlite3.Cursor:
        loguru.logger.info(f"[SQL]\t{s}")
        return self.link.cursor().execute(s)

    @staticmethod
    def commit_all():
        for i in pool:
            pool[i].commit()

    def search_data(
        self, table: str, column: list | dict | str = "*", require: type = list
    ):
        cmd = None
        if type(column) == list:
            cmd = f"SELECT {', '.join(column)} FROM {table};"
        elif type(column) == str:
            cmd = f"SELECT {column} FROM {table};"
        elif type(column) == dict:
            cmd = f"SELECT {'*' if 'select' not in column else column['select']} FROM {table} WHERE {list(column['data'].keys())[0]} LIKE '{list(column['data'].values())[0]}'; "
        if require == list:
            return (
                self.__decode_b64(self.exec_sql(cmd))
                if self.b64
                else self.exec_sql(cmd)
            )
        else:
            return self.parse_data_to_dict(
                self.__decode_b64(self.exec_sql(cmd))
                if self.b64
                else self.exec_sql(cmd),
                column,
            )

    def insert_table(self, name: str, cmd: dict):
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

        self.exec_sql(sentence)

    def create_table(self, name: str, struct: dict):
        def parser(n):
            return {str: " TEXT", int: " INT NOT NULL"}[n]

        cmd = (
            f"CREATE TABLE IF NOT EXISTS {name}("
            + ",".join([i + parser(struct[i]) for i in struct])
        ) + ");"

        self.exec_sql(cmd)

    @staticmethod
    def __decode(s: str):
        return base64.standard_b64decode(s.encode()).decode()

    @staticmethod
    def __encode(s: str):
        return base64.standard_b64encode(s.encode()).decode()

    def __decode_b64(self, data: sqlite3.Cursor):
        rzt = []
        for i in data:
            rzt_b = [self.__decode(ii) if type(ii) == str else ii for ii in i]
            rzt.append(rzt_b)
        return rzt

    @staticmethod
    def to_pure_list(ll: list | sqlite3.Cursor):
        ret = []
        for ii in ll:
            ret.extend(iter(ii))
        return ret

    @staticmethod
    def parse_data_to_dict(data: list, key: list | str) -> dict | list:
        if type(key) == str:
            return data
        ret = {}
        for i in data:
            for num in range(len(key)):
                ret[key[num]] = [] if key[num] not in ret else ret[key[num]]
                ret[key[num]].append(i[num])
        return ret

    def update_table(self, name: str, struct: dict):
        cmd = f"DELETE FROM {name} WHERE {struct['select'][0]} = {struct['select'][1]};"
        self.exec_sql(cmd)
        self.insert_table(name, struct["data"])


if __name__ == "__main__":
    loguru.logger.warning("Created a database whose strings are all base64 encoded")
    x = SqlLink("test1.db", b64=True)
    x.create_table("furry", {"QQ": int, "圈名": str, "其他": str})
    x.insert_table("furry", {"QQ": 114514, "圈名": "测试圈名"})
    x.insert_table("furry", {"QQ": 114, "圈名": "dcfh"})
    loguru.logger.debug(x.search_data("furry", ["QQ", "圈名", "其他"], require=dict))
    loguru.logger.debug(
        x.to_pure_list(x.search_data("furry", {"select": "圈名", "data": {"qq": 114514}}))
    )
    loguru.logger.warning("Created a database whose strings are all plaintext")
    x = SqlLink("test2.db")
    x.create_table("furry", {"QQ": int, "圈名": str, "其他": str})
    x.insert_table("furry", {"QQ": 114514, "圈名": "测试圈名"})
    x.update_table(
        "furry", {"select": ["QQ", 114514], "data": {"QQ": 114514, "圈名": "阿斯奇琳"}}
    )
    x.insert_table("furry", {"QQ": 114514, "圈名": "测试圈名"})
    loguru.logger.debug(x.search_data("furry", ["QQ", "圈名"], require=dict))
    loguru.logger.debug(
        x.to_pure_list(x.search_data("furry", {"select": "圈名", "data": {"qq": 114514}}))
    )
    SqlLink.commit_all()
    x.link.close()
