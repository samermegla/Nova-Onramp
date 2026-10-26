"""Small helpers shared by the control nodes.

Keeping these in one place means the chase node and the mouse node use
identical steering maths, which makes their behaviour easier to compare
when one of them misbehaves.
"""

import math

# turtlesim's canvas is a square this many world units on a side.
# (The window is 500x500 pixels by default, and 500 / 45.0 pixels-per-unit
# gives 11.0888..., which is where this number comes from.)
CANVAS = 11.08888

# Keep goal points this far inside the walls so a turtle slides along an
# edge instead of grinding into it and spamming collision warnings.
WALL_MARGIN = 1.0


def normalize_angle(angle):
    """Wrap any angle into the range [-pi, pi].

    Without this, the difference between a heading of +3.0 rad and
    -3.0 rad looks like 6.0 rad (most of a full turn) when it is really
    only about 0.28 rad the other way. The turtle would spin the long way
    around every time it crossed that boundary.
    """
    return math.atan2(math.sin(angle), math.cos(angle))


def clamp(value, low, high):
    """Constrain a value to a range."""
    return max(low, min(high, value))


def steer(pose, goal_x, goal_y, linear_gain=1.5, angular_gain=4.0,
          max_linear=3.0, max_angular=4.0, cone=math.pi / 3):
    """Proportional controller: return (linear, angular) to reach a goal.

    The idea is simple: measure how wrong we are, and respond in
    proportion to that error.

      * Angular: how far off is our heading from pointing at the goal?
        Turn at a rate proportional to that angle error.
      * Linear: how far away is the goal? Drive at a speed proportional
        to that distance, capped so we do not rocket across the canvas.

    The `cone` guard stops us driving forward while badly misaimed. If
    the goal is behind us, driving forward first would carve a wide arc;
    turning in place until roughly aimed, then driving, looks much more
    deliberate.

    Both outputs are capped. Uncapped, a goal directly behind produces
    `angular_gain * pi` rad/s, which makes the turtle spin so fast it
    is hard to see what it is doing.
    """
    dx = goal_x - pose.x
    dy = goal_y - pose.y
    distance = math.hypot(dx, dy)

    heading_error = normalize_angle(math.atan2(dy, dx) - pose.theta)

    angular = clamp(angular_gain * heading_error, -max_angular, max_angular)
    linear = 0.0
    if abs(heading_error) < cone:
        linear = min(linear_gain * distance, max_linear)

    return linear, angular