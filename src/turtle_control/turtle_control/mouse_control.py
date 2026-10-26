"""Drive turtle1 toward the mouse pointer.

turtlesim does not publish anything about the mouse, so this node reads
the pointer position straight from the X server, converts it from screen
pixels into turtlesim world coordinates, and steers turtle1 at it.

Three conversions matter:

  1. The pointer has to be measured relative to the turtlesim window,
     not the whole screen. Querying the pointer through that window
     gives exactly that.
  2. X11 measures y downward from the top of a window. turtlesim measures
     y upward from the bottom of the canvas. One of them has to flip.
  3. Pixels are not world units. Dividing by the window size gives a
     0..1 fraction, which scales to the 11.0888-unit canvas.
"""

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from Xlib import display

from turtle_control.turtle_math import CANVAS, steer

# turtlesim sets its window title to "TurtleSim". We search for this
# rather than hardcoding a window id, because the id changes every run.
WINDOW_TITLE = 'TurtleSim'

# Stop nudging once we are this close, otherwise the turtle jitters
# around the cursor forever instead of settling.
ARRIVAL_RADIUS = 0.15


def find_window(window, title):
    """Depth-first search of the X window tree for a matching title.

    X11 organises windows as a tree rooted at the screen. The window a
    toolkit like Qt actually draws into is often nested a few levels
    down inside frames the window manager added, so we cannot just look
    at the root's direct children.
    """
    try:
        name = window.get_wm_name()
    except Exception:
        # Some windows have no name or vanish mid-query. Not fatal.
        name = None

    if name and title in name:
        return window

    try:
        children = window.query_tree().children
    except Exception:
        return None

    for child in children:
        match = find_window(child, title)
        if match is not None:
            return match
    return None


class MouseControl(Node):

    def __init__(self):
        super().__init__('mouse_control')

        self.declare_parameter('turtle', 'turtle1')
        self.declare_parameter('rate_hz', 20.0)

        turtle = self.get_parameter('turtle').value
        rate = self.get_parameter('rate_hz').value

        self.publisher = self.create_publisher(
            Twist, f'/{turtle}/cmd_vel', 10)
        self.create_subscription(
            Pose, f'/{turtle}/pose', self.on_pose, 10)

        self.pose = None

        self.display = display.Display()
        self.root = self.display.screen().root
        self.window = None
        self.warned_missing_window = False

        self.create_timer(1.0 / rate, self.tick)

        self.get_logger().info(
            f'Steering {turtle} toward the mouse pointer.')

    def on_pose(self, msg):
        self.pose = msg

    def mouse_target(self):
        """Pointer position in turtlesim world coordinates, or None.

        Returns None when the turtlesim window cannot be found or when
        the pointer is outside the canvas. Callers should treat None as
        "no target right now" and stop the turtle rather than guessing.
        """
        if self.window is None:
            self.window = find_window(self.root, WINDOW_TITLE)
            if self.window is None:
                if not self.warned_missing_window:
                    self.get_logger().warn(
                        f'No window titled "{WINDOW_TITLE}" found yet; '
                        'waiting for turtlesim to appear.')
                    self.warned_missing_window = True
                return None
            self.get_logger().info('Found the turtlesim window.')
            self.warned_missing_window = False

        try:
            geometry = self.window.get_geometry()
            # Querying the pointer through the turtlesim window (rather
            # than the root) gives win_x/win_y already relative to that
            # window's top-left corner, so there is no offset maths to
            # get wrong.
            pointer = self.window.query_pointer()
        except Exception:
            # The window was probably closed. Forget it and look again
            # on the next tick rather than dying.
            self.window = None
            return None

        px = pointer.win_x
        py = pointer.win_y

        if not (0 <= px <= geometry.width and 0 <= py <= geometry.height):
            return None  # pointer is off the canvas

        x = (px / geometry.width) * CANVAS
        # The 1.0 - ... is the y-axis flip described in the module docstring.
        y = (1.0 - py / geometry.height) * CANVAS
        return x, y

    def tick(self):
        if self.pose is None:
            return  # haven't heard where the turtle is yet

        command = Twist()
        target = self.mouse_target()

        if target is not None:
            distance = math.hypot(target[0] - self.pose.x,
                                  target[1] - self.pose.y)
            if distance > ARRIVAL_RADIUS:
                linear, angular = steer(
                    self.pose, target[0], target[1],
                    linear_gain=2.0, angular_gain=5.0,
                    cone=math.pi / 4)
                command.linear.x = linear
                command.angular.z = angular

        # Publishing an all-zero Twist when there is no target is
        # deliberate: turtlesim keeps applying the last command it
        # received, so staying silent would leave the turtle driving.
        self.publisher.publish(command)


def main(args=None):
    rclpy.init(args=args)
    node = MouseControl()
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