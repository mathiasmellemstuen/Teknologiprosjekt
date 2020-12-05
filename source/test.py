import Benchmarking as b

import json

b.start()

with open("config.json","r") as f: 
    json.load(f)

b.stop()
b.printExecutionTime()
