#!/usr/bin/env python3
import rospy
import tf
import math
import numpy                as np
import matplotlib.pyplot    as plt
from tf.transformations     import euler_from_quaternion, quaternion_from_euler, rotation_matrix
from sensor_msgs.msg        import Image, CameraInfo
import json


datos = "datasets/evaluacion/positional_information/tickets/1_8_mid.json"
with open(datos) as f:
    data = json.load(f)


def publish_tf(event):
    for tickIdx, tickData in data["tickets"].items():
        x,y,z=tickData["map_position"]["trans"]
        tf_broadcaster.sendTransform((x,y,z),
                                    tickData["map_position"]["rot"],
                                    rospy.Time.now(),
                                    '/%s'%str(tickIdx),
                                    '/map')


if __name__ == "__main__":

    rospy.init_node("goals_schedule_show")

    tf_broadcaster  = tf.TransformBroadcaster()

    rospy.Timer(rospy.Duration(0.01), publish_tf)

    try:
        rospy.spin() 
    except KeyboardInterrupt:
        rospy.signal_shutdown("End")