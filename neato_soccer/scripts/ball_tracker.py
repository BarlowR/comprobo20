#!/usr/bin/env python3

""" This is a script that walks through some of the basics of working with
    images with opencv in ROS. """

import rospy
from sensor_msgs.msg import Image
from copy import deepcopy
from cv_bridge import CvBridge
import cv2
import numpy as np
from geometry_msgs.msg import Twist, Vector3

class BallTracker(object):
    """ The BallTracker is a Python object that encompasses a ROS node 
        that can process images from the camera and search for a ball within.
        The node will issue motor commands to move forward while keeping
        the ball in the center of the camera's field of view. """

    def __init__(self, image_topic):
        """ Initialize the ball tracker """
        rospy.init_node('ball_tracker')
        self.cv_image = None                        # the latest image from the camera
        self.bridge = CvBridge()                    # used to convert ROS messages to OpenCV

        self.center_x = None

        rospy.Subscriber(image_topic, Image, self.process_image)
        self.pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        cv2.namedWindow('video_window')
        cv2.namedWindow('threshold_window')

    def process_image(self, msg):
        """ Process image messages from ROS and stash them in an attribute
            called cv_image for subsequent processing """
        self.cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        self.binary_image = cv2.inRange(self.cv_image, (0,0,60), (50,50,255))
        moments = cv2.moments(self.binary_image)
        if moments['m00'] != 0:
            self.center_x, self.center_y = moments['m10']/moments['m00'], moments['m01']/moments['m00']
        else: self.center = None

    def run(self):
        """ The main run loop, in this node it doesn't do anything """
        r = rospy.Rate(5)
        while not rospy.is_shutdown():
            if not self.cv_image is None:
                print(self.cv_image.shape)
                cv2.imshow('video_window', self.cv_image)
                cv2.imshow('threshold_window', self.binary_image)
                cv2.waitKey(5)

                n_white_pix = np.sum(self.binary_image == 255)
                print (n_white_pix)

                twist = Twist()
                if n_white_pix < 20: 
                    twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0;
                    twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0.5

                elif self.center_x is not None:
                    twist.linear.x = 1; twist.linear.y = 0; twist.linear.z = 0;
                    twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0.005 * (300-self.center_x)
                    

                
                
                self.pub.publish(twist)
            # start out not issuing any motor commands
            r.sleep()

if __name__ == '__main__':
    node = BallTracker("/camera/image_raw")
    node.run()
