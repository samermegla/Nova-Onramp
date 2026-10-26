import rclpy
from rclpy.node import Node

from turtle_msgs.msg import ChaseMode


class ModeSwitcher(Node):

    def __init__(self):
        super().__init__('mode_switcher')
        self.publisher_ = self.create_publisher(ChaseMode, 'chase_mode', 10)
        timer_period = 10.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.chase = True

    def timer_callback(self):
        self.chase = not self.chase
        msg = ChaseMode()
        msg.chase = self.chase
        self.publisher_.publish(msg)
        self.get_logger().info('CHASE' if self.chase else 'RUN AWAY')


def main(args=None):
    rclpy.init(args=args)

    mode_switcher = ModeSwitcher()

    rclpy.spin(mode_switcher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    mode_switcher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()