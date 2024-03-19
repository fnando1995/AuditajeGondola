import glob
import pandas as pd
import os
import json

jsonspath = glob.glob("datasets\evaluacion\positional_information\\final\*.json")
last = "datasets\evaluacion\positional_information\\1_last.json"
D={}
for jsonpath in jsonspath:
    filename = jsonpath.split(os.sep)[-1][:-5]
    with open(jsonpath) as f:
        d=json.load(f)
    D[filename]=d
with open(last,"w") as f:
    json.dump(D,f,indent=4,sort_keys=True)