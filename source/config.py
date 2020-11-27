import json

FILE = "config.json"

class CurrentConfig:
    config = {}
    
    @staticmethod
    def get():
        return CurrentConfig.config

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
    CurrentConfig.config = json.loads(json.dumps(data), object_hook=int_please_object_hook)

    with open(FILE,"w") as f:
        json.dump(data, f)

def load():
    print("Loadig config file.") 
    with open(FILE,"r") as f:
        CurrentConfig.config = json.load(f, object_hook=int_please_object_hook)

