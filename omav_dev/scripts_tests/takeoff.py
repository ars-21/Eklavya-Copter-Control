#!/usr/bin/env python3
# This console is only for debugging

import rospy
from mav_msgs.msg import Actuators
from nav_msgs.msg import Odometry 
from std_msgs.msg import Float64
altitude = 0
s = 7
s1 = 0
def calPos(msg):
    global x,y,altitude
    x = round(msg.pose.pose.position.x,3)
    y = round(msg.pose.pose.position.y,3)
    altitude = (round(msg.pose.pose.position.z,3))- 0.17498
def takeoff():
    alt_pub  = rospy.Publisher('alt_pub', Float64, queue_size=100)
    pub = rospy.Publisher('/omav/command/motor_speed', Actuators,queue_size=100)
    rospy.init_node('takeoff_node',anonymous=True)
    speed =  Actuators()
    rate = rospy.Rate(1)
    speed.angular_velocities.append(100*s)
    speed.angular_velocities.append(100*s)
    speed.angular_velocities.append(100*s)
    speed.angular_velocities.append(100*s)
    speed.angular_velocities.append(100*s)
    speed.angular_velocities.append(100*s)
    speed.angular_velocities.append(100*s)
    speed.angular_velocities.append(100*s)
    speed.angular_velocities.append(100*s)
    speed.angular_velocities.append(100*s)
    speed.angular_velocities.append(100*s)
    speed.angular_velocities.append(100*s)

    speed.angular_velocities.append(1*s1)
    speed.angular_velocities.append(1*s1)
    speed.angular_velocities.append(1*s1)
    speed.angular_velocities.append(1*s1)
    speed.angular_velocities.append(1*s1)
    speed.angular_velocities.append(1*s1)
    
    i = 0
    while not rospy.is_shutdown():
        if i == 1:
            speed.angular_velocities[0] = 100*s
            speed.angular_velocities[1] = 100*s
            speed.angular_velocities[2] = 100*s
            speed.angular_velocities[3] = 100*s
            speed.angular_velocities[4] = 100*s
            speed.angular_velocities[5] = 100*s
            speed.angular_velocities[6] = 100*s
            speed.angular_velocities[7] = 100*s
            speed.angular_velocities[8] = 100*s
            speed.angular_velocities[9] = 100*s
            speed.angular_velocities[10] = 100*s
            speed.angular_velocities[11] = 100*s
            speed.angular_velocities[12] = 0
            speed.angular_velocities[13] = 0
            speed.angular_velocities[14] = 0
            speed.angular_velocities[15] = 0
            speed.angular_velocities[16] = 0
            speed.angular_velocities[17] = 0
        rospy.Subscriber("/omav/ground_truth/odometry", Odometry, calPos)

        alt_pub.publish(altitude)

        rospy.loginfo(speed)
        pub.publish(speed)
        i+= 1
        rate.sleep()    

if __name__=='__main__':
    try:
        takeoff()
    except rospy.exceptions.ROSInternalException:
        pass