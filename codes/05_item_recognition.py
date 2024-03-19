#!/usr/bin/python3
import os,time,json,glob,io,os
from datetime import datetime as dt, timedelta as td
import concurrent
from google.cloud import vision
google_dir = "datasets\evaluacion\\annotations\google\\"


class ItemRecognitionTextManager():
    def __init__(self):
        self.creds_file = "code\\05_gcp_token.json" # create a token in google vision apo
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.creds_file
        self.client = vision.ImageAnnotatorClient()
        self.dir_ = "datasets\evaluacion\\annotations\google\\"
        
    def forward_document(self,filepath,tries=1):
        with io.open(filepath, 'rb') as image_file: 
            content = image_file.read()
        filename = filepath.split(os.sep)[-1][:-4]
        image           = vision.Image(content=content)
        flag            = True
        error_tries     = 0
       
        while flag:
            try:
                response    = self.client.document_text_detection(image=image).full_text_annotation
                if str(response)=="":
                    texto=""
                    confianza=0.0
                else:
                    texto = response.text.replace("\n"," ")
                    confianza = float(response.pages[0].confidence)
                d={"text":texto,"confidence":confianza}
                with open(self.dir_+filename+".json","w") as f:
                    json.dump(d,f,indent=4,sort_keys=True)
            except Exception as e:
                print(f"Error with {filepath} {e} ")
                error_tries+=1
            else:
                flag = False
            finally:
                if error_tries==tries:
                    flag = False
                    print(f"[Item Recognizer] error en imagen {filepath} supero el limite de intentos.\n")


             
recog = ItemRecognitionTextManager()

for filepath  in glob.glob("datasets\evaluacion\\rgb_images\items\\*.jpg"):
    recog.forward_document(filepath)