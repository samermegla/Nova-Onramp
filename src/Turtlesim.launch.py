from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node


SPAWN_X = 2.0
SPAWN_Y = 2.0
SPAWN_THETA = 0.0
SPAWN_NAME = 'turtle2'


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen',
        ),

        TimerAction(
            period=2.0,
            actions=[
                ExecuteProcess( #Terminal command to spawn a second turtle
                    cmd=[
                        'ros2', 'service', 'call',
                        '/spawn',
                        'turtlesim/srv/Spawn',
                        f"{{x: {SPAWN_X}, y: {SPAWN_Y}, "
                        f"theta: {SPAWN_THETA}, name: '{SPAWN_NAME}'}}",
                    ],
                    output='screen',
                ),
            ],
        ),
    ])

