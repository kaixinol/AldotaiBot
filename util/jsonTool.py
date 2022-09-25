import json
def ReadJson(n: str)->dict | str:
    try:
        with open(n, "r") as load_f:
            load_dict = json.load(load_f)
        return load_dict
    except Exception as e: 
        return str(e)


def CreateJson(n: str, data: dict):
    try:
        with open(n, "w") as f:
            json.dump(data, f)
        return True
    except:
        return False