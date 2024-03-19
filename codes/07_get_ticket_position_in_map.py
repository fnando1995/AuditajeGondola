
import glob
import json
from statistics import median,mean
import numpy as np
import math

import tf
from tf.transformations import quaternion_from_euler,translation_from_matrix,quaternion_from_matrix

import rospy

rospy.init_node('test_node')

def yolobbox2bbox(x,y,w,h):
    x1, y1 = x-w/2, y-h/2
    x2, y2 = x+w/2, y+h/2
    return x1, y1, x2, y2

def ids_to_astra(x1,y1,x2,y2,x,y,array):
    distance_limit_near = 600    # robot captura a una distancia cercana a los 80 cm de la gondola.
    distance_limit_far  = 900    # ticket se encuentra en bandeja por lo que debe estar lo mas cerca a esa distancia
    astra_height = 640
    astra_width = 480
    factor      = 7.675 # factor relacion imagen rgb-3d.
    traslado_x  = 49.89 # Traslado en anchura.
    traslado_y  = -9.42 # Traslado en altura.    
    x1 = int((x1/factor)+traslado_x) #int por ser pixel.
    y1 = int((y1/factor)+traslado_y)
    x2 = int((x2/factor)+traslado_x)
    y2 = int((y2/factor)+traslado_y)
    x1 = x1 if x1>=0 else 0
    y1 = y1 if y1>=0 else 0
    x2 = x2 if x2<astra_width else astra_width-1 # index
    y2 = y2 if y2<astra_height else astra_height-1 # index
    # Del arreglo de distancias se coge todas aquellas que esten en el rango
    # definido posible para los tickets
    z_s = [distance for distance in list(array[x1:x2,y1:y2].reshape(-1)) if distance>distance_limit_near and distance<distance_limit_far]
    x = int((x/factor)+traslado_x)
    y = int((y/factor)+traslado_y)
    z = int(median(z_s)) if len(z_s)>0 else -1 # valor medio como representacion final, sino -1 para descartar
    return [x1,y1,x2,y2,x,y,z]

def median_distance_for_all_tickets(dictionary):
    vs=[]
    for idx,value in dictionary.items():
        v=value["astra"][-1]
        if v!=-1:
            vs.append(v)
    if len(vs)>0:
        meanz = mean(vs)
    else:
        meanz = 800

    for idx in dictionary.keys():
        dictionary[idx]["astra"][-1]=meanz
    
    return dictionary

def rgb_pixel_to_3d_coordinate(x,y,z,camera_info):
    """
    de pizel RGB hacia la referencia de la camara 
    usando los valores intrinsecos de la propia
    camara 3D obtenidos durante la calibracion
    de la misma.
    """
    u = y
    v = x
    cx = camera_info.K[2]
    cy = camera_info.K[5]
    fx = camera_info.K[0]
    fy = camera_info.K[4]
    x_ = ((640.0-float(u-10)) - cx)/fx #no confundir x con y con u y v... solucionar luego!
    y_ = (float(v) - cy)/fy
    z = float(z)/1000
    x = x_ * z
    y = y_ * z
    return [x, y , z]


posinfo = "datasets/evaluacion/positional_information/raw/*.json"
annottickets = "datasets/evaluacion/annotations/tickets/*.txt"
depthimages = "datasets/evaluacion/depth_images/npy/*.npy"
cameras_info_filepath = "datasets/cameras_positional_info_20221124.npy"
hi = 4912
wi = 3684
cameras_info    = np.load(cameras_info_filepath,allow_pickle=True)[0]
camera_info_top = cameras_info["camera_info_top"]
camera_info_mid = cameras_info["camera_info_mid"]
camera_info_bot = cameras_info["camera_info_bot"]
M_robot_top     = cameras_info["M_robot_top"]
M_robot_mid     = cameras_info["M_robot_mid"] 
M_robot_bot     = cameras_info["M_robot_bot"]
position_listener = tf.TransformListener()



for annot,pos_info,depthimg in zip(sorted(glob.glob(annottickets)),sorted(glob.glob(posinfo)),sorted(glob.glob(depthimages)) ):
    with open(annot) as f: tickets_annots = [ [ float(i) for i in line.split(" ")[1:]] for line in f.readlines()]
    with open(pos_info) as f: position_info = json.load(f)
    position_info["tickets"]={}
    depth = np.load(depthimg,allow_pickle=True)
    # trasladar a sistema relativo de mapa.
    collector       = position_info["host"]
    x_goal          = position_info["map_pos"]["x"]
    y_goal          = position_info["map_pos"]["y"]
    yaw_goal        = position_info["map_pos"]["yaw"]
    # matriz para proyectar a referencia del mapa
    M_map           = position_listener.fromTranslationRotation([x_goal, y_goal, 0.0],quaternion_from_euler(0.0,0.0,yaw_goal))
    # Seleccionar la informacion de la camara del collector 
    if collector=="bot":
        M_robot_tmp = M_robot_bot
        camera_info_tmp = camera_info_bot
    elif collector=="mid":
        M_robot_tmp = M_robot_mid
        camera_info_tmp = camera_info_mid
    elif collector=="top":
        M_robot_tmp = M_robot_top
        camera_info_tmp = camera_info_top
    else:
        print(f"Collector equivocado: {collector}")
    for idx,line in enumerate(tickets_annots):
        x,y,w,h = line
        x = x*wi
        y = y*hi
        w = w*wi
        h = h*hi
        x1,y1,x2,y2 = yolobbox2bbox(x,y,w,h)
        position_info["tickets"][idx]={"rgbuhd":[int(i) for i in [x1,y1,x2,y2,x,y]],
                                        "astra":ids_to_astra(x1,y1,x2,y2,x,y,depth)}

    position_info["tickets"] = median_distance_for_all_tickets(position_info["tickets"])

    for idx,line in enumerate(tickets_annots):    
        x_depth = position_info["tickets"][idx]["astra"][-3]
        y_depth = position_info["tickets"][idx]["astra"][-2]
        z_depth = position_info["tickets"][idx]["astra"][-1]
        ticket_traslation   = rgb_pixel_to_3d_coordinate(x_depth,y_depth,z_depth,camera_info_tmp) # [lista]
        ticket_rotation     = quaternion_from_euler(0.0, math.pi, math.pi)      # ticket rotado en 90* en y,z 
        M_ticket            = position_listener.fromTranslationRotation(ticket_traslation,ticket_rotation)
        M                   = np.dot(np.dot(M_map,M_robot_tmp),M_ticket)
        ticket_map_trans    = list(translation_from_matrix(M)) # x,y,z
        ticket_map_rot      = list(quaternion_from_matrix(M))  # roll,pich,yaw (en quaternials)
        position_info["tickets"][idx]["map_position"]  ={"trans":ticket_map_trans,"rot":ticket_map_rot}    
    
    
    with open(pos_info.replace("/raw/","/tickets/"),"w") as f:
        json.dump(position_info,f,indent=4,sort_keys=True)











