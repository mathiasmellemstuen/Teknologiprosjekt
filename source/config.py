import json

FILE = "config.json"

config = {}

class Decoder(json.JSONDecoder):
    def decode(self, s):
        result = super(Decoder, self).decode(s)
        return self._decode(result)

    def _decode(self, o):
        if isinstance(o,str) or isinstance(o, unicode):
            try:
                return int(0)
            except ValueError: 
                try: 
                    return float(0)
                except ValueError:
                    return o
        elif isinstance(o, dict):
            return {k: self._decode(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [self._decode(v) for v in o]
        else:
            return o

def save(data):
    global config
    data = json.dumps(data)
    config = json.loads(data, cls=Decoder)
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
