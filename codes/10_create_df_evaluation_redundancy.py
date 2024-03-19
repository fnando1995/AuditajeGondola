import glob
import pandas as pd
import os
import json
df=pd.DataFrame([],columns=["name","x","y","z","price","price_conf","description","description_conf","code","code_conf","original_cluster"])
last = "datasets\evaluacion\positional_information\\1_last.json"
datapath = "datasets\evaluacion\positional_information\\2_filtered.csv"


with open(last) as f:
    dflast = json.load(f)
lista_rechazados=[]
counter=0
price_conf_thres = 0.90
description_conf_thres = 0.75
code_conf_thres = 0.90
for key in dflast.keys():
    for ticketid,ticketval in dflast[key]["tickets"].items():
        name = f"{key}_{ticketid}"
        counter+=1
        if ticketval["read_text"]["price"] is None:
            lista_rechazados.append(name)
            continue
        if ticketval["read_text"]["price"]["text"]=="":
            lista_rechazados.append(name)
            continue
        if ticketval["read_text"]["price"]["confidence"]<price_conf_thres:
            lista_rechazados.append(name)
            continue
        # ninguno de los dos es distinto a None
        if not(ticketval["read_text"]["description"] is not None or ticketval["read_text"]["code"] is not None):
            lista_rechazados.append(name)
            continue
        # lecturas ordenadas siempre que existan y superen los threshold de confianza
        reads=[ticketval["read_text"]["price"]["text"],ticketval["read_text"]["price"]["confidence"]]
        if ticketval["read_text"]["description"] is not None:
            if ticketval["read_text"]["description"]["confidence"]>=description_conf_thres:
                reads.extend([ticketval["read_text"]["description"]["text"],ticketval["read_text"]["description"]["confidence"]])
            else:
                reads.extend([None,None])
        else:
            reads.extend([None,None])

        if ticketval["read_text"]["code"] is not None:
            if ticketval["read_text"]["code"]["confidence"]>=code_conf_thres:
                reads.extend([ticketval["read_text"]["code"]["text"],ticketval["read_text"]["code"]["confidence"]])
            else:
                reads.extend([None,None])
        else:
            reads.extend([None,None])
        row = [name]+ticketval["map_position"]["trans"]+reads+[ticketval["cluster"]]
        df.loc[len(df)]=row
df.to_csv(datapath,sep=",",index=False)
