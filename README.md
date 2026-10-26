# Nova-Onramp

A ROS2 playground built around `turtlesim`.

- **turtle1** follows your mouse cursor.
- **turtle2** alternates every 10 seconds between chasing and fleeing turtle1.

## Packages

- `turtle_control` — mouse-following node, chase node, mode switcher, and launch files.
- `turtle_msgs` — custom `ChaseMode` message used to signal chase/flee.

## Running it

```bash
# build
colcon build --symlink-install
source install/setup.bash

# terminal 1: turtlesim + turtle2 spawn + mouse control
ros2 launch turtle_control Turtlesim.launch.py

# terminal 2: chase behavior + mode switching
ros2 launch turtle_control Chase.launch.py
```

## Demo

<video src="https://raw.githubusercontent.com/samermegla/Nova-Onramp/main/media/turtle-demo.mp4" controls width="600"></video>
