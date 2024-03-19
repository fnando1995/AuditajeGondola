import glob
import pandas as pd
import os
import json
df=pd.DataFrame([],columns=["name","x","y","z","price","price_conf","description","description_conf","code","code_conf","original_cluster"])
last = "datasets\evaluacion\positional_information\\1_last.json"
datapath = "datasets\evaluacion\positional_information\\2_nonfiltered.csv"


with open(last) as f:
    dflast = json.load(f)
for key in dflast.keys():
    for ticketid,ticketval in dflast[key]["tickets"].items():
        name = f"{key}_{ticketid}"
        reads=[]
        if ticketval["read_text"]["price"] is None:
            reads.extend([None,None])
        else:
            reads.extend([ticketval["read_text"]["price"]["text"],ticketval["read_text"]["price"]["confidence"]])
        if ticketval["read_text"]["description"] is None:
            reads.extend([None,None])
        else:
            reads.extend([ticketval["read_text"]["description"]["text"],ticketval["read_text"]["description"]["confidence"]])
        if ticketval["read_text"]["code"] is None:
            reads.extend([None,None])
        else:
            reads.extend([ticketval["read_text"]["code"]["text"],ticketval["read_text"]["code"]["confidence"]])
        row = [name]+ticketval["map_position"]["trans"]+reads+[ticketval["cluster"]]
        df.loc[len(df)]=row
df.to_csv(datapath,sep=",",index=False)
