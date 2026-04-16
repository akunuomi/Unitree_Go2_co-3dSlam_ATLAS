"""
需求：处理客户端提交的数据（0或非0 ）
如果是0，调用停止巡航的接口
如果是非0，开始巡航，不过不论提交的什么数据都需要相应机器人的位置信息

流程：
1创建服务端
2回调函数处理请求，分情况处理（控制机器人的巡航）最后响应结果


"""

import rclpy
from rclpy.node import Node
from go2_tutorial_inter.srv import Cruising
from geometry_msgs.msg import Point
from nav_msgs.msg import Odometry
from unitree_api.msg import Request
from .sport_model import ROBOT_SPORT_API_IDS
import json
import time


class Go2CruingService(Node):
    def __init__(self):
        super().__init__("go2_cruising_service")
        # 创建服务端
        self.service = self.create_service(Cruising, "cruising", self.cruising_callback)
        # 创建一个空point
        self.point = Point()
        # 订阅里程计信息，获取机器人的位置信息
        self.odom_sub = self.create_subscription(
            Odometry, "odom", self.odom_callback, 10
        )
        # 设置巡航参数
        self.declare_parameter("x", 0.0)
        self.declare_parameter("y", 0.0)
        self.declare_parameter("z", 0.5)

        # 创建速度控制的发布对象
        self.api_id = ROBOT_SPORT_API_IDS["BALANCESTAND"]  # 巡航的api_id
        self.req_pub = self.create_publisher(Request, "/api/sport/request", 10)
        self.timer = self.create_timer(0.1, self.on_timer)

    def on_timer(self):
        # 发布速度指令，保持巡航状态
        request = Request()
        request.header.identity.api_id = self.api_id  # 巡航的api_id
        # 设置速度参数
        js = {
            "x": self.get_parameter("x").value,
            "y": self.get_parameter("y").value,
            "z": self.get_parameter("z").value,
        }
        request.parameter = json.dumps(js)
        self.req_pub.publish(request)

    # 里程计回调函数，获取位置信息
    def odom_callback(self, msg: Odometry):
        self.point = msg.pose.pose.position

    def cruising_callback(self, request: Cruising.Request, response: Cruising.Response):
        # 处理请求
        flag = request.flag
        if flag == 0:
            self.get_logger().info("停止巡航")
            self.api_id = ROBOT_SPORT_API_IDS["STOPMOVE"]
        else:
            self.get_logger().info("开始巡航")
            self.api_id = ROBOT_SPORT_API_IDS["MOVE"]

        # 产生响应
        response.point = self.point
        return response


def main():
    rclpy.init()
    rclpy.spin(Go2CruingService())
    rclpy.shutdown()


if __name__ == "__main__":
    main()
