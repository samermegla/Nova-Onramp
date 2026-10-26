"""Make turtle2 chase or flee turtle1, depending on the current mode.

This node listens to three things:

  * /turtle1/pose   - where the target is
  * /turtle2/pose   - where we are
  * /chase_mode     - our custom message saying chase or run away

and publishes velocity commands to /turtle2/cmd_vel.

Both behaviours have a "good enough" band so the turtle settles instead
of oscillating: when chasing it stops once close, when fleeing it stops
once far. Crossing back out of that band starts it moving again, which
is exactly what the task asks for.
"""

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from turtle_msgs.msg import ChaseMode

from turtle_control.turtle_math import CANVAS, WALL_MARGIN, clamp, steer

# Close enough that we stop chasing.
CHASE_STOP_DISTANCE = 1.0
# Far enough that we stop fleeing.
FLEE_SAFE_DISTANCE = 4.0
# How far ahead to aim when running away.
FLEE_LOOKAHEAD = 3.0


class Chaser(Node):

    def __init__(self):
        super().__init__('chaser')

        self.declare_parameter('target', 'turtle1')
        self.declare_parameter('self_name', 'turtle2')
        self.declare_parameter('rate_hz', 20.0)

        target = self.get_parameter('target').value
        me = self.get_parameter('self_name').value
        rate = self.get_parameter('rate_hz').value

        self.target_pose = None
        self.my_pose = None
        # Default to chasing so we do something sensible before the
        # first mode message arrives.
        self.chase = True
        self.last_logged_mode = None

        self.create_subscription(
            Pose, f'/{target}/pose', self.on_target_pose, 10)
        self.create_subscription(
            Pose, f'/{me}/pose', self.on_my_pose, 10)
        self.create_subscription(
            ChaseMode, '/chase_mode', self.on_mode, 10)

        self.publisher = self.create_publisher(
            Twist, f'/{me}/cmd_vel', 10)

        self.create_timer(1.0 / rate, self.tick)

        self.get_logger().info(f'{me} is watching {target}.')

    def on_target_pose(self, msg):
        self.target_pose = msg

    def on_my_pose(self, msg):
        self.my_pose = msg

    def on_mode(self, msg):
        self.chase = msg.chase
        if self.chase != self.last_logged_mode:
            self.get_logger().info(
                'Mode: CHASE' if self.chase else 'Mode: RUN AWAY')
            self.last_logged_mode = self.chase

    def pick_goal(self, distance):
        """Where we want to be, or None if we are happy where we are."""
        if self.chase:
            if distance <= CHASE_STOP_DISTANCE:
                return None  # close enough, hold position
            return self.target_pose.x, self.target_pose.y

        # Running away.
        if distance >= FLEE_SAFE_DISTANCE:
            return None  # far enough, hold position

        # Aim at a point directly opposite the target, but clamp it
        # inside the canvas. Without the clamp the turtle drives into a
        # wall and sits there pressed against it while turtlesim logs a
        # collision warning every tick.
        away = math.atan2(self.my_pose.y - self.target_pose.y,
                          self.my_pose.x - self.target_pose.x)
        goal_x = self.my_pose.x + FLEE_LOOKAHEAD * math.cos(away)
        goal_y = self.my_pose.y + FLEE_LOOKAHEAD * math.sin(away)
        return (clamp(goal_x, WALL_MARGIN, CANVAS - WALL_MARGIN),
                clamp(goal_y, WALL_MARGIN, CANVAS - WALL_MARGIN))

    def tick(self):
        if self.my_pose is None or self.target_pose is None:
            return  # not enough information yet

        distance = math.hypot(self.target_pose.x - self.my_pose.x,
                              self.target_pose.y - self.my_pose.y)

        command = Twist()
        goal = self.pick_goal(distance)

        if goal is not None:
            linear, angular = steer(self.my_pose, goal[0], goal[1])
            command.linear.x = linear
            command.angular.z = angular

        self.publisher.publish(command)


def main(args=None):
    rclpy.init(args=args)
    node = Chaser()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()