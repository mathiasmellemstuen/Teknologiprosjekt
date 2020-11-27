import json

FILE = "config.json"

config = {}

def int_please_object_hook(obj):
    rv = {}
    for k, v in obj.items():
        if isinstance(v, str):
            try:
                rv[k] = int(v)
            except ValueError:
                rv[k] = v
        else:
            rv[k] = v
    return rv

def save(data):
    global config
    config = json.loads(json.dump(data), object_hook=int_please_object_hook)
    with open(FILE,"w") as f:
        json.dump(data, f)

def load():
    global config
    print("Loadig config file.") 
    with open(FILE,"r") as f:
        config = json.load(f, object_hook=int_please_object_hook)

def get():
    global config
    return config
