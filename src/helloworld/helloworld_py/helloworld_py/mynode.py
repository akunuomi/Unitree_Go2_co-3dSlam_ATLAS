import rclpy
from rclpy.node import Node


class HelloWorldPy(Node):
    def __init__(self):
        super().__init__("helloworld_py")


def main():
    rclpy.init()
    rclpy.spin(HelloWorldPy())
    rclpy.shutdown()


if __name__ == "__main__":
    main()
