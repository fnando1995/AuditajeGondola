import glob
import pandas as pd
import os
import json
import shutil

filepath="datasets\evaluacion\\annotations\clusters\\raw.csv"
dir_="datasets\evaluacion\drawings\clusters\\"
ticketsdir="datasets\evaluacion\\rgb_images\\tickets\\"
df = pd.read_csv(filepath,dtype={"id":str,"cluster":str})
for row in df.iterrows():
    row=row[1]
    hall=row.imagen[0]
    hall_dir=dir_+f"{hall}\\"
    if not os.path.exists(hall_dir):
        os.mkdir(hall_dir)
    cluster_dir=hall_dir+f"{row.id}\\"
    if not os.path.exists(cluster_dir):
        os.mkdir(cluster_dir)
    fn=f"{row.imagen}_{row.ticketnumber}.jpg"
    fp=ticketsdir+fn
    shutil.copy(fp,cluster_dir+fn)