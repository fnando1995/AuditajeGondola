import glob
import pandas as pd
import os
import json

jsonspath = glob.glob("datasets\evaluacion\positional_information\\tickets\*.json")
new_dir="datasets\evaluacion\positional_information\\final\\"
clustersdf = pd.read_csv("datasets\evaluacion\\annotations\\clusters\\raw.csv",dtype={"imagen":str,"ticketnumber":str,"id":str})
clustersdf['ticket_filename']=clustersdf.apply(lambda x:'%s_%s' % (x['imagen'],x['ticketnumber']),axis=1)
googletextsdir = "datasets\evaluacion\\annotations\google\\"
classes={"0":"price","1":"code","2":"description"}

counter=0
for jsonpath in jsonspath:
    with open(jsonpath) as f:
        data = json.load(f)
    for iticket,ticket in data["tickets"].items():
        ticket_filename=data["filename"]+f"_{iticket}"
        cluster = clustersdf[clustersdf["ticket_filename"]==ticket_filename].reset_index()
        cluster = None if len(cluster)==0 else cluster["id"][0]
        ticket["cluster"]=cluster
        ticket["read_text"]={"price":None,"description":None,"code":None}
        if os.path.exists(googletextsdir+ticket_filename+"_0.json"):
            with open(googletextsdir+ticket_filename+"_0.json") as f:
                jdata = json.load(f)
                ticket["read_text"]["price"]=jdata
        if os.path.exists(googletextsdir+ticket_filename+"_1.json"):
            with open(googletextsdir+ticket_filename+"_1.json") as f:
                jdata = json.load(f)
                ticket["read_text"]["description"]=jdata
        if os.path.exists(googletextsdir+ticket_filename+"_2.json"):
            with open(googletextsdir+ticket_filename+"_2.json") as f:
                jdata = json.load(f)
                ticket["read_text"]["code"]=jdata
    with open(new_dir+data["filename"]+".json","w") as f:
        json.dump(data,f,indent=4,sort_keys=True)
