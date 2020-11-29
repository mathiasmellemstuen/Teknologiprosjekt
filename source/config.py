import json

FILE = "config.json"

def objectHook(obj):
    rv = {}
    
    if obj is None: 
        print("Error: The value is None. Returning empty dict.")
        return rv

    for k, v in obj.items():
        if v is None:
            print("Error: The value in the key is None. Changing it to 0")
            rv[k] = 0
        elif isinstance(v, str):
            if "." in v:
                try: 
                    rv[k] = float(v)
                except ValueError: 
                    rv[k] = v
            else:
                try:
                    rv[k] = int(v)
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
        return json.load(f, object_hook=objectHook)

