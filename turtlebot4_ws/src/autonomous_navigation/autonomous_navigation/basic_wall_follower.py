#!/usr/bin/env python3

import rclpy

from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TwistStamped

import math
from rclpy.qos import qos_profile_sensor_data


class SimpleMazeNavigator(Node):
    def __init__(self):
        super().__init__("simple_maze_navigator")

        self.scan_sub = self.create_subscription(
            LaserScan,
            "/tb4/scan",
            self.scan_callback,
            qos_profile_sensor_data
        )

        self.cmd_pub = self.create_publisher(
            TwistStamped,
            "/tb4/cmd_vel",
            10
        )

        self.latest_scan = None

        self.forward_speed = 3.0
        self.turn_speed = 1.5
        self.wall_threshold = 0.4

        self.difference_threshold = 0.2

        self.timer = self.create_timer(0.05, self.control_loop)

        self.get_logger().info("Barebones maze navigator started.")
        self.get_logger().info("Subscribing to /tb4/scan")
        self.get_logger().info("Publishing to /tb4/cmd_vel")

        self.min_distance_left = None

        self.state = 'FORWARD'
        self.prev_state = None

        self.turn_start_time = None
        self.turn_duration = None

        self.forward_distance = None
        self.left_distance = None
        self.prev_left_distance = None
    
    def _get_angle_idx(self, angle, angle_min, angle_increment):
        return round((angle + abs(angle_min)) / angle_increment)

    def scan_callback(self, msg):
        self.latest_scan = msg

        forward_idx = self._get_angle_idx(0, msg.angle_min, msg.angle_increment)
        left_idx = self._get_angle_idx(math.pi / 2, msg.angle_min, msg.angle_increment)

        self.prev_left_distance = self.left_distance
        self.forward_distance = msg.ranges[forward_idx]
        self.left_distance = msg.ranges[left_idx]

        start = self._get_angle_idx(math.pi / 3, msg.angle_min, msg.angle_increment)
        end = self._get_angle_idx((2 * math.pi) / 3, msg.angle_min, msg.angle_increment)

        curr = None
        for i in range(start, end):
            distance = msg.ranges[i]
            if curr is None or distance < curr:
                curr = distance
        self.min_distance_left = curr

    def control_loop(self):
        if self.latest_scan is None:
            self.stop()
            self.get_logger().info("Waiting for scan message...")
            return

        self.get_logger().info(f"{self.state}")

        if self.state == 'DONE':
            pass
    
        if self.state == 'FORWARD':
            self.get_logger().info(f"Forward Distance: {self.forward_distance}")
            self.get_logger().info(f"Left Distance: {self.left_distance} versus {self.prev_left_distance}")

            if self.forward_distance == 0:
                self.get_logger().info(f"DONE")
                self.state = 'DONE'
            elif not self.prev_left_distance is None and (self.left_distance - self.prev_left_distance >= self.difference_threshold or self.left_distance == 0):
                self.state = 'LOOK_FOR_OPENING'
            elif self.forward_distance < self.wall_threshold:
                self.stop()
                self.start_turn(90, 'FORWARD', 'RIGHT')
            else:
                self.move_forward()
        
        if self.state == 'LOOK_FOR_OPENING':
            self.get_logger().info(f"Min Left Distance: {self.min_distance_left}, wall distance {self.wall_threshold}")
            # if self.min_distance_left >= self.wall_threshold:
            #     self.stop()
            #     self.start_turn(90, 'FORWARD', 'LEFT')
            if self.forward_distance < self.wall_threshold:
                self.stop()
                self.start_turn(90, 'FORWARD', 'LEFT')
            else:
                self.move_forward()

        if self.state == 'RIGHT':
            elapsed = (self.get_clock().now() - self.turn_start_time).nanoseconds / 1e9

            if elapsed < self.turn_duration:
                self.turn_right()
            else:
                self.stop()
                self.state = self.prev_state
                self.prev_state = None
        
        if self.state == 'LEFT':
            elapsed = (self.get_clock().now() - self.turn_start_time).nanoseconds / 1e9

            if elapsed < self.turn_duration:
                self.turn_left()
            else:
                self.stop()
                self.state = self.prev_state
                self.prev_state = None

    def move_forward(self):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"

        msg.twist.linear.x = self.forward_speed
        msg.twist.angular.z = 0.0

        self.cmd_pub.publish(msg)
    
    def turn_left(self):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"

        msg.twist.linear.x = 0.0
        msg.twist.angular.z = self.turn_speed

        self.cmd_pub.publish(msg)
    
    def turn_right(self):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"
        msg.twist.linear.x = 0.0
        msg.twist.angular.z = -1 * self.turn_speed
        self.cmd_pub.publish(msg)
    
    def start_turn(self, angle_degrees, prev_state, direction):
        self.get_logger().info(f"Starting turn: {angle_degrees} {direction}, returning to {prev_state}")
        self.prev_state = prev_state
        self.turn_start_time = self.get_clock().now()
        self.turn_duration = math.radians(abs(angle_degrees)) / self.turn_speed
        self.state = direction
        self.get_logger().info(f"Turn started")

    def stop(self):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"

        msg.twist.linear.x = 0.0
        msg.twist.angular.z = 0.0

        self.cmd_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = SimpleMazeNavigator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Keyboard interrupt received. Stopping robot.")
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()