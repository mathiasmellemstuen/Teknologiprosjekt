import json

FILE = "config.json"

def int_please_object_hook(obj):
    rv = {}
    for k, v in obj.items():
        if isinstance(v, str):
            try:
                rv[k] = int(v)
            except ValueError:
                try: 
                    rv[k] = float(v)
                except ValueError:
                    rv[k] = v
        else:
            rv[k] = v
    return rv

def save(data):
    with open(FILE,"w") as f:
        json.dump(data, f)

def load(): 
    with open(FILE,"r") as f:
        return json.load(f, object_hook=int_please_object_hook)

