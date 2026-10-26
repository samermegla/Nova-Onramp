"""Container 2: the chase behaviour and the mode switcher.

Neither node touches the display. They find turtlesim purely over the
network by subscribing to its topics, which is the whole point of
running them in a separate container.

No TimerActions here. Unlike the first launch file, nothing in this one
needs to wait for a service to exist or a window to be drawn - both
nodes simply subscribe and start listening. If turtlesim is not up yet
they sit quietly until it is.
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        # Makes turtle2 follow or flee turtle1, depending on the
        # current mode it hears on /chase_mode.
        Node(
            package='turtle_control',
            executable='chaser',
            name='chaser',
            output='screen',
        ),

        # Publishes the custom ChaseMode message, flipping every 10s.
        Node(
            package='turtle_control',
            executable='mode_switcher',
            name='mode_switcher',
            output='screen',
        ),
    ])