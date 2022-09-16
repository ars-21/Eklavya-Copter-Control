#! /usr/bin/env python3
# Giving default PID values incase no input from user

"""
        #> - means that the particular value needs to be changed while tuning

        d(X)  =  Derivative
        dd(X) =  Double Derivative
        _mat  =  Matrix
"""
from turtle import tilt
from moment_force_allocation import *
from cmath import cos, sin, sqrt
from math import atan2
import time
import numpy as np 
import rospy
from std_msgs.msg import Float64, Float64MultiArray
from mav_msgs.msg import Actuators


kp = 20

ki = 0

kd = 10

g = 9.81 # gravitational acceleration

kap = 8.06428e-05 #0.00099 #> constant for the matrix

Mu = 7.2e-06 #3.4e-6 #> constant for the matrix

t1 = 0.866025403784 #> sqrt(3)/2

len = 0.3 #> assuming that length is 0.3m 

xz = 0.5  


def PID_alt(roll, pitch, yaw, x, y, target, altitude, flag, roll_desired, pitch_desired, yaw_desired, k_pose, velocity, kap, Mu, kq, kr):
    #global variables are declared to avoid their values resetting to 0
    global prev_alt_err,iMem_alt,dMem_alt,pMem_alt,prevTime, ddMem_alt, prevdMem_alt
    global prevErr_roll, prevErr_pitch, prevErr_yaw, pMem_roll, pMem_yaw, pMem_pitch, iMem_roll, iMem_pitch, iMem_yaw, dMem_roll, dMem_pitch, dMem_yaw, setpoint_roll,setpoint_pitch, sample_time,current_time
    global target_x,target_y,req_alt
    global prop_pos_mat, diff_pose_mat, i_pose_mat, kp, ki, kd, omega

    #Assigning target, altitude
    setpoint_roll = 0  #this should change according to the desired r,p,y
    setpoint_pitch = 0  #this should change according to the desired r,p,y
    
    #setting targets
    kp = k_pose[0]
    ki = k_pose[1]
    kd = k_pose[2]
    omega = np.array([[velocity[0]],[velocity[1]],[velocity[2]]])
    target_x = target[0]
    target_y = target[1]
    req_alt = target[2]
    # setting time for the differential terms and for later applications too
    sample_time = 0.005
    current_time = time.time()

    #Controller for x and y. Sets setpoint pitch and roll as output depending upon the corrections given by PID
    position_controller(target_x, target_y, x, y, flag)

    err_pitch = pitch - pitch_desired #Changed this from setpoint roll to roll desired

    err_roll = roll - roll_desired #Changed this from setpoint pitch to pitch desired

    err_yaw = 0 - yaw #for our application we don't want the hexacopter to yaw like at all

    curr_alt_err = req_alt - altitude
    #this is limiting case where we have reached the desired location in x and y
    # if(-2.5 <=setpoint_pitch <=2.5 and -2.5<= setpoint_roll <= 2.5): 
    #     err_roll = setpoint_roll
    #     err_pitch = setpoint_pitch

    # Publishing error values to be plotted in rqt
    alt_err_pub = rospy.Publisher("/alt_err", Float64, queue_size=10)
    alt_err_pub.publish(curr_alt_err)
    roll_err_pub = rospy.Publisher("/roll_err", Float64, queue_size=10)
    roll_err_pub.publish(err_roll)
    pitch_err_pub = rospy.Publisher("/pitch_err", Float64, queue_size=10)
    pitch_err_pub.publish(err_pitch)
    yaw_err_pub = rospy.Publisher("/yaw_err", Float64, queue_size=10)
    yaw_err_pub.publish(err_yaw)



    mass_total = 4.04 #Kg this I got from the urdf file

    weight = 4.04*g

    hover_speed  = 678 #just taking an assumption later will correct it based on the experimanetal data

    # Flag for checking for the first time the function is called so that values can initilized
    # because if we don't check so then, we will encounter the error that we had no prevtime only
    if flag == 0:
        prevTime = 0
        prevErr_roll = 0
        prevErr_pitch = 0
        prevErr_yaw = 0
        pMem_roll = 0
        pMem_pitch = 0
        pMem_yaw = 0
        iMem_roll = 0
        iMem_pitch = 0
        iMem_yaw = 0
        dMem_roll = 0
        dMem_pitch = 0
        dMem_yaw = 0    
        prev_alt_err = 0
        iMem_alt = 0
        dMem_alt = 0
        prevdMem_alt = 0
        ddMem_alt = 0

    #defining time for the differential terms
    dTime = current_time - prevTime

    #defining all the differential terms

    dErr_alt = curr_alt_err - prev_alt_err


# ================== Starting calculations for the error terms =================== #


    if ( dTime >= sample_time ):

        # Proportional Terms
        
        pMem_alt = curr_alt_err
        
        # Integral Terms

        iMem_alt += curr_alt_err*dTime


        # Derivative Terms
        
        dMem_alt = dErr_alt / dTime

        #limit integrand values
        if(iMem_alt > 400): iMem_alt = 400
        if(iMem_alt <-400): iMem_alt = -400

    #Updating previous error terms

    prev_alt_err = curr_alt_err
    prevdMem_alt = dMem_alt

    # Final output correction terms after combining PID
    # output_alt = pMem_alt + iMem_alt + kd_thrust*dMem_alt

    # Now, For tuning purposes we will be limiting output altitude
    
    # output_alt = 1 if output_alt > 1 else output_alt


    prop_pos_mat = np.array([[pMem_x],[pMem_y],[pMem_alt]]) #position error matrix
    # print(prop_pos_mat)
    diff_pose_mat = np.array([[dMem_x],[dMem_y],[dMem_alt]])
    # print(diff_pose_mat)
    i_pose_mat = np.array([[iMem_x],[iMem_y],[iMem_alt]])
    # print(i_pose_mat)
    tilt_ang, ang_vel_rot = control_allocation( roll, pitch, yaw, hover_speed, mass_total, weight, flag, roll_desired, pitch_desired, yaw_desired, kq, kr, Mu, kap)

    t = 0
    if ( t == 0 ):
        speed.angular_velocities.append(ang_vel_rot[4])
        speed.angular_velocities.append(ang_vel_rot[1])
        speed.angular_velocities.append(ang_vel_rot[0])
        speed.angular_velocities.append(ang_vel_rot[3])
        speed.angular_velocities.append(ang_vel_rot[5])
        speed.angular_velocities.append(ang_vel_rot[2])
        speed.angular_velocities.append(ang_vel_rot[4])
        speed.angular_velocities.append(ang_vel_rot[1])
        speed.angular_velocities.append(ang_vel_rot[0])
        speed.angular_velocities.append(ang_vel_rot[3])
        speed.angular_velocities.append(ang_vel_rot[5])
        speed.angular_velocities.append(ang_vel_rot[2])
        speed.angular_velocities.append(tilt_ang[4])
        speed.angular_velocities.append(tilt_ang[1]-math.pi/2)
        speed.angular_velocities.append(tilt_ang[0])
        speed.angular_velocities.append(tilt_ang[3]-math.pi/2)
        speed.angular_velocities.append(tilt_ang[5]-math.pi/2)
        speed.angular_velocities.append(tilt_ang[2])
        # print("Once")
        t += 1

    speed.angular_velocities[0] = ang_vel_rot[4]
    speed.angular_velocities[1] = ang_vel_rot[1]
    speed.angular_velocities[2] = ang_vel_rot[0]
    speed.angular_velocities[3] = ang_vel_rot[3]
    speed.angular_velocities[4] = ang_vel_rot[5]
    speed.angular_velocities[5] = ang_vel_rot[2]
    speed.angular_velocities[6] = ang_vel_rot[4]
    speed.angular_velocities[7] = ang_vel_rot[1]
    speed.angular_velocities[8] = ang_vel_rot[0]
    speed.angular_velocities[9] = ang_vel_rot[3]
    speed.angular_velocities[10] = ang_vel_rot[5]
    speed.angular_velocities[11] = ang_vel_rot[2]
    speed.angular_velocities[12] = tilt_ang[4]
    speed.angular_velocities[13] = (tilt_ang[1])
    speed.angular_velocities[14] = tilt_ang[0]
    speed.angular_velocities[15] = (tilt_ang[3])
    speed.angular_velocities[16] = (tilt_ang[5])
    speed.angular_velocities[17] = tilt_ang[2]

    # Limiting the speeds to the permissible limits
    if (speed.angular_velocities[0] > 1700): speed.angular_velocities[0] = 1700
    if (speed.angular_velocities[1] > 1700): speed.angular_velocities[1] = 1700
    if (speed.angular_velocities[2] > 1700): speed.angular_velocities[2] = 1700
    if (speed.angular_velocities[3] > 1700): speed.angular_velocities[3] = 1700
    if (speed.angular_velocities[4] > 1700): speed.angular_velocities[4] = 1700
    if (speed.angular_velocities[5] > 1700): speed.angular_velocities[5] = 1700
    if (speed.angular_velocities[6] > 1700): speed.angular_velocities[6] = 1700
    if (speed.angular_velocities[7] > 1700): speed.angular_velocities[7] = 1700
    if (speed.angular_velocities[8] > 1700): speed.angular_velocities[8] = 1700
    if (speed.angular_velocities[9] > 1700): speed.angular_velocities[9] = 1700
    if (speed.angular_velocities[10] > 1700): speed.angular_velocities[10] = 1700
    if (speed.angular_velocities[11] > 1700): speed.angular_velocities[11] = 1700

    print(speed.angular_velocities)
    return(speed)

# ======================= Control Allocation Starts here ========================== #

"""
<-----------------------------------Matrices Used------------------------------------->

    1. Rotation matrix: 
            R(from ground to the body frame) = R(phi)^T*R(theta)^T*R(gamma)^T
    2. Static Allocation matrix:
            A = [constants](6x12)
    3. Hybrid matrix:
            x = [ xc1   xs1   xc2   xs2   xc3   xs3   xc4   xs4   xc5   xs5   xc6   xs6]^T
            Where, xci = cos(αi) and xsi = sin(αi) (Here, αi = Tilt angles of the ith rotor)   
    4. We also need a pseudo inverse for the static allocation matrix

"""

def control_allocation( roll, pitch, yaw, hover_speed, mass_total, weight, flag, roll_desired, pitch_desired, yaw_desired, kq, kr, Mu, kap):
    global F_des, M_des, prevoutRoll, prevoutPitch, prevoutYaw # F_des --> Force desired and M_des --> Desired moment
    global current_time,prevTime,dTime, Final_mat, speed, prevOmega
    theta = pitch * (math.pi / 180) #current pitch
    phi = roll * (math.pi / 180) #current Roll
    gamma = yaw * (math.pi / 180) #current yaw
    if (flag == 0):
        prevTime = 0
        prevoutRoll = 0
        prevoutPitch = 0
        prevoutYaw = 0
        prevOmega = np.zeros([3,1])

    dTime = current_time - prevTime
    sample_time = 0.005

#===============================Defining Matrices==================================>#
    F_des, A_pseudo_inv = force_desired(phi, theta, gamma, Mu, kap, len, t1, mass_total, prop_pos_mat, diff_pose_mat, i_pose_mat, kp, ki, kd)
    

#<--------------Intertia matrix for the Moment desired calc-------------------------->
    # angular velocities
    # 3x1
    
    I = np.array([[0.0075,0,0],[0,0.010939,0],[0,0,0.01369]]) 
    # The above matrix is already defined in the urdf
    
    M_des = moment_desired(roll_desired, pitch_desired, yaw_desired, roll, pitch, yaw , omega[0][0], omega[1][0], omega[2][0], I,kq,kr)

    # Final_mat = np.array([[F_des[0][0]],[F_des[1][0]],[F_des[2][0]],[M_des[0][0]],[M_des[1][0]],[M_des[2][0]]]) #6x1 matrix from Fdes and Mdes
    speed = Actuators()
    Final_mat = np.array([F_des[0][0].real,F_des[1][0].real,F_des[2][0].real,M_des[0][0].real,M_des[1][0].real,M_des[2][0].real]) #3x1 matrix when restrictions are applied
    # Now, here we consider xci = w^2*cos(αi) and xsi = w^2*sin(αi) 
    
    relation_matrix = np.round_(np.matmul( A_pseudo_inv , Final_mat ).real,decimals = 3)
    # print(relation_matrix)

    # Now, we are going to get the angles and the velocities for the rotors
    #Note: that we have not before just considered the real values from sins and cos it may cause some problem

    # Angular velocties deduction
    ang_vel= np.array([0.0,0.0,0.0,0.0,0.0,0.0])
    i = 0
    for i in range(6):
        ang_vel[i]= round(abs((1/sqrt(Mu))*(sqrt(sqrt(pow(relation_matrix[2*i],2) + pow(relation_matrix[2*i+1],2))).real)), 3) # ang_vel^2 = sqrt((Xci)^2+(Xsi)^2))


    # Tilt Angles deduction
    tilt_ang = np.array([0.0,0.0,0.0,0.0,0.0,0.0])
    i = 0
    for i in range(6):
        x1 = pow(sqrt(relation_matrix[2*i+1]).real,2)
        x2 = pow(sqrt(relation_matrix[2*i]).real,2)
        # print(x1) Uses this to get the real value from the matrix
        tilt_ang[i] = round(atan2(x1,x2),3) # atan2(sin/cos)

    #Now, we need to allocate the speed to each rotor
    ang_vel_rot = tuple(xz*ang_vel)
    # Uncomment for debugging only
    # print(ang_vel_rot,tilt_ang)
    tilt_ang = tuple(tilt_ang)
    return tilt_ang, ang_vel_rot

"""
    Note : CW -> Clockwise Rotation and CCW -> Anti Clockwise Rotation or Counter clockwise Rotation
            Here, We are considering CCW as +ve and CW as -ve
            Also, Here we are considering output error = current position - previous position
    So now we have got total errors for the x and y that we are off.
    So now what we do is to get at x and y is the following:

    1. To get to the x we need to pitch either CW or CCW
        * Now if the difference in current_error and previous_error in x is greater than a certain constant let's say 2 units, that means we have surpassed the point x
            So, Now we need to pitch in the opposite direction of the output error in x and also in the opposite direction of the velocity in x
        
    2. To get to the y we need to roll either CW or CCW
        * Now if the difference in current_error and previous_error in y is greater than a certain constant let's say 2 units, that means we have surpassed the point y
            So, Now we need to roll in the opposite direction of the output error in y and also in the opposite direction of the velociy in y

"""

#Controller which applies PID to errors in x and y(target values of vel being 0) and gives setpoint pitch and roll as output to correct the errors
def position_controller(target_x, target_y, x, y, flag):
    #global variables are declared to avoid their values resetting to 0
    global prevTime,dTime
    global prevErr_x,prevErr_y,pMem_x,pMem_y,iMem_x,iMem_y,dMem_x,dMem_y
    global err_x,err_y,dErr_x,dErr_y
    global prevdMem_x, prevdMem_y
    global setpoint_pitch, setpoint_roll
    
    if (flag == 0):
        prevTime = 0
        prevErr_x = 0
        prevErr_y = 0
        prevdMem_x = 0
        prevdMem_y = 0
        pMem_x = 0
        pMem_y = 0
        iMem_x = 0
        iMem_y = 0
        dMem_x = 0
        dMem_y = 0

    #setting dTime for derivative and integral terms
    dTime = current_time - float(prevTime)

    err_x = x - target_x
    err_y = y - target_y


    dErr_x = err_x - prevErr_x
    dErr_y = err_y - prevErr_y

    sample_time = 0.005

    if(dTime >= sample_time):
        
        # Proportional terms
        pMem_x = err_x
        pMem_y = err_y

        # Integral terms
        iMem_x += err_x*dTime
        iMem_y += err_y*dTime

        if(iMem_x>10): iMem_x = 10
        if(iMem_x<-10): iMem_x=-10

        #Derivative terms

        dMem_x = (dErr_x / dTime)
        dMem_y = (dErr_y / dTime)

    #updating previous terms
    prevErr_x = err_x
    prevErr_y = err_y