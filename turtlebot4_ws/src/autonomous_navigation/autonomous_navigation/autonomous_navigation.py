import math
import time

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TwistStamped

class MazeNavigator(Node):
    def __init__(self):
        super().__init__('autonomous_navigation')

        self.forward_speed = 0.15
        self.turn_speed = 0.5
        self.stop_distance = 0.2

        self.latest_scan = None

    def scan_callback(self, msg):
        self.latest_scan = msg
    
    