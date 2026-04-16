"""
需求：订阅里程计消息，当机器狗位移超出指定阈值，输出机器狗当前位置坐标
实现流程：
1订阅里程计消息
2在订阅的回调函数中，计算当前机器狗与上一个记录的坐标之间的距离
                如果距离大于阈值就输出坐标，并更新记录点。

                第一个记录点如何生成？
                当第一次订阅到里程计消息时，就为记录点赋值

"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import math


class Go2State(Node):
    def __init__(self):
        super().__init__("go2_state")
        # 第一次获取里程计消息的标记
        self.is_first = True
        # 记录点的坐标变量
        self.last_x = 0.0
        self.last_y = 0.0
        # 阈值设置为参数
        self.declare_parameter("distance_threshold", 0.1)

        self.odom_sub = self.create_subscription(
            Odometry, "odom", self.odom_callback, 10
        )

    def odom_callback(self, odom: Odometry):
        # 获取当前坐标
        # 获取x,y但在实际过程时需要三维
        x = odom.pose.pose.position.x
        y = odom.pose.pose.position.y

        # 设置第一个记录点
        if self.is_first:
            self.last_x = x
            self.last_y = y
            self.is_first = False
            self.get_logger().info(f"初始坐标：x={x:.2f}, y={y:.2f}")
            return

        # 计算是否超出距离
        dis_x = x - self.last_x
        dis_y = y - self.last_y
        distance = math.sqrt(dis_x**2 + dis_y**2)
        # 判断
        if distance >= self.get_parameter("distance_threshold").value:
            # 输出坐标点
            self.get_logger().info(f"当前坐标：x={x:.2f}, y={y:.2f}")
            # 更新记录点
            self.last_x = x
            self.last_y = y


def main():
    rclpy.init()
    rclpy.spin(Go2State())
    rclpy.shutdown()


if __name__ == "__main__":
    main()
