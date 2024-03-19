import cv2,os,time,glob,json
from math import ceil,floor
from datetime import datetime as dt, timedelta as td
import numpy as np
from PIL import Image


def yolobbox2bbox(x,y,w,h):
    x1, y1 = int(x-w/2), int(y-h/2)
    x1 = x1 if x1>0 else 0
    y1 = y1 if y1>0 else 0
    x2, y2 = int(x+w/2), int(y+h/2)
    return x1, y1, x2, y2

drawings_path       = "datasets\evaluacion\drawings\shelves_tickets\\"
shelves_images_path = sorted(glob.glob("datasets\evaluacion\\rgb_images\shelves\*.jpg"))
shelves_annots_path = sorted(glob.glob("datasets\evaluacion\\annotations\\tickets\*.txt"))
tickets_dir_path = "datasets\evaluacion\\rgb_images\\tickets\\"



for imagepath,textpath in zip(shelves_images_path,shelves_annots_path):
    filename = imagepath.split(os.sep)[-1][:-4]
    image    = cv2.cvtColor(np.array(Image.open(imagepath)), cv2.COLOR_RGB2BGR)
    hi,wi,_  = image.shape
    with open(textpath) as f:
        annotations = f.readlines()
    boxes = []
    for i,annot in enumerate(annotations):
        cls,x,y,w,h =annot.split(" ")
        x,y,w,h             = float(x),float(y),float(w),float(h)
        ximg,yimg,wimg,himg = int(x*wi),int(y*hi),int(w*wi),int(h*hi)
        x1,y1,x2,y2         = yolobbox2bbox(ximg,yimg,wimg,himg)
        print(x1,y1,x2,y2)
        ticket_roi          = image[y1:y2,x1:x2,:]
        boxes.append([x1,y1,x2,y2])
        cv2.imwrite(tickets_dir_path+filename+f"_{i}.jpg",ticket_roi)
    for x1,y1,x2,y2 in boxes:
        image               = cv2.rectangle(image, (x1,y1), (x2,y2), (0,0,255), thickness=10)
        image               = cv2.putText(image, str(i), (ximg,yimg), cv2.FONT_HERSHEY_SIMPLEX, 5, (0,0,255), 10, cv2.LINE_AA)
    cv2.imwrite(drawings_path+filename+".jpg",image)
    