import json

FILE = "config.json"

config = {}

def save(data):
    global config
    config = data
    with open(FILE,"w") as f:
        json.dump(data, f)

def load():
    global config
    print("Loadig config file.") 
    with open(FILE,"r") as f:
        config = json.load(f)

def get():
    global config
    return config