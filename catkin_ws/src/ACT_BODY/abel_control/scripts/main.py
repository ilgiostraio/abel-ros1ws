#!/usr/bin/env python3

# from curses import flash
# from os import truncate
import rospy

from abel_control.MoveAbelArms import MoveAbelArms
from abel_control.MoveAbelNeck import MoveAbelNeck

from sensor_msgs.msg import JointState
from std_msgs.msg import  Float64MultiArray, String, Int64
from trajectory_msgs.msg import JointTrajectoryPoint
import threading
from queue import Queue
import time


arms    = MoveAbelArms()
neck    = MoveAbelNeck()
onlyArms = True
onlyNeck = True


def arms_gestures_scheduler(queue):
	rospy.loginfo("scheduler thread starting")
	while True:
		next_gesture = queue.get()
		rospy.loginfo("I found something in queue")
		arms.run_gesture(next_gesture, 3)
		time.sleep(5)

def lookat_callback(data):
	rospy.loginfo(rospy.get_caller_id() + " I'm looking at:  %s", data.data)
	if (abs(data.data[0])<=1) and (abs(data.data[1])<=1):
		x = data.data[0]
		y = data.data[1]
		if len(data.data)==3:
			d = data.data[2]
			neck.look_xy(x, y, d)
		else:
			neck.look_xy(x, y)
	else:
		rospy.WARN("Insert values between -1 and 1")

def gesture_arms_callback(data):
	
	checkchar = "\\"
	
	if checkchar in data.data:
		data.data = data.data.replace('\\', '')
		data.data = data.data.replace('\"', '')

	arms.gesture_arms_list()
	rospy.loginfo(rospy.get_caller_id() + " I heard %s and I put it in the queue", data.data)

	arms_gestures_scheduler_queue.put(data.data)


	#class_method = getattr(gesture, data.data)
	#class_method(5)

def gesture_neck_callback(data):
		
	checkchar = "\\"
	
	if checkchar in data.data:
		data.data = data.data.replace('\\', '')
		data.data = data.data.replace('\"', '')

		neck.gesture_neck_list()
		rospy.loginfo(rospy.get_caller_id() + " I heard %s", data.data)

		neck.run_posture(data.data, 1)

	else:
		neck.gesture_neck_list()
		rospy.loginfo(rospy.get_caller_id() + " I heard %s", data.data)

	neck.run_posture(data.data, 5)

	#class_method = getattr(neck, data.data)
	#class_method(5)

def capture_arms_callback(data):
	rospy.loginfo(rospy.get_caller_id() + " I heard %s", data.data)
	if data == 0:
		rospy.loginfo("Send 1 if you want to start arms gesture acquisition...")
	else:
		arms.capture_position(data.data, 10)
                
def capture_neck_callback(data):
	if data == 0:
		rospy.loginfo("Send 1 if you want to start neck gesture acquisition...")
	else:
		neck.capture_position(10)
                
                

def moveit_callback(data):
        pos = data.position
        #rospy.loginfo(pos)
        #new_position = JointTrajectoryPoint()

        new_position = [pos[0], pos[1], pos[2], pos[3], pos[4], 
                           pos[5], pos[6], pos[7], pos[8], pos[9] ]

        new_position.time_from_start = rospy.Duration(2)

        arms.move_joints(new_position)

def close():

	if onlyArms:
		arms.shutdown()
	elif onlyNeck:
		neck.shutdown()
	else:
		neck.shutdown()
		rospy.sleep(10)
		arms.shutdown()
	
	rospy.loginfo("Bye! Bye!")


if __name__ == '__main__':


	rospy.init_node('abel_control', log_level=rospy.DEBUG)
	rate = rospy.Rate(10)
	
	lookat_subscriber = rospy.Subscriber("/abel_control/neck/lookat", Float64MultiArray, lookat_callback )

	gesture_arms_subscriber = rospy.Subscriber("/abel_control/arms/gesture", String, gesture_arms_callback )
	gesture_neck_subscriber = rospy.Subscriber("/abel_control/neck/gesture", String, gesture_neck_callback )

	capture_arms_subscriber = rospy.Subscriber("/abel_control/arms/capture", Int64, capture_arms_callback )
	capture_neck_subscriber = rospy.Subscriber("/abel_control/neck/capture", Int64, capture_neck_callback )

	## INIT THREAD QUEUE 
	arms_gestures_scheduler_queue = Queue()
	arms_gestures_scheduler_thread = threading.Thread(target=arms_gestures_scheduler, args=(arms_gestures_scheduler_queue, ))
	arms_gestures_scheduler_thread.start()

	## -- MOVEIT TEST FOR JOINTS VALUES -- ##
	moveit_subscriber = rospy.Subscriber("/joint_states", JointState, moveit_callback, queue_size=100 )
	
	rospy.loginfo("*** AbelMove Initialization ***")
	
	if not onlyArms and not onlyNeck:
		raise Exception("I know python!")
	
	if onlyArms:
		arms.initialize()
	
	if onlyNeck:
		neck.initialize()

	#arms.run_gesture("neutral",5)
	
	#neck.run_posture("neutral",5)
	#rospy.sleep(10)
	#close()
	rospy.loginfo("**** Abel is ready! ****")

	rospy.on_shutdown(close)

	rospy.spin()
	

		

		



#     gesture.hand(5)
#     rospy.sleep(3)
#     neck.down(5)
#     rospy.sleep(3)

#     gesture.hello(5)
#     rospy.sleep(3)    
#     neck.up(5)
#     rospy.sleep(3)

    
#     neck.rotate_left(5)
#     rospy.sleep(3)

#     gesture.neutral(5)
#     rospy.sleep(3)
#     neck.neutral(5)
#     rospy.sleep(3)

    ## -- TEST LOOK_XY -- ##
    #neck.lookat_sequence_test()


    ## -- MOVEMENT SEQUENCE -- ##
    #gesture.sequence_test(5)
    #neck.sequence_test(5)
    #rospy.sleep(5)


    ## -- ESPLORAZIONE MOTORI COLLO -- ##
    #neck.explore()

    ##TEST CAPTURE POSITION##
    #arms.capture_position_arms(5)
    #neck.capture_position_neck(10)

    ##TEST ESPLORAZIONE MOTORE SPALLA SX##
    #arms.explore_vel()