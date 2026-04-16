"""
创建一个request的发布对象
创建Twist订阅对象
在回调函数里实现消息的转换和发布

"""

import rclpy
from rclpy.node import Node
from unitree_api.msg import Request
from geometry_msgs.msg import Twist
import json
from .sport_model import ROBOT_SPORT_API_IDS


class TwistBridge(Node):
    def __init__(self):
        super().__init__("twist_bridge")
        # 创建一个request的发布对象
        self.request_pub = self.create_publisher(Request, "/api/sport/request", 10)
        # 创建Twist订阅对象
        self.twist_sub = self.create_subscription(
            Twist, "/cmd_vel", self.twist_callback, 10
        )

    def twist_callback(self, twist: Twist):
        # 在回调函数里实现消息的转换和发布
        request = Request()
        # 获取速度
        x = twist.linear.x
        y = twist.linear.y
        z = twist.linear.z
        # 设置api_id
        api_id = ROBOT_SPORT_API_IDS["BALANCESTAND"]
        if x != 0 or y != 0 or z != 0:
            api_id = ROBOT_SPORT_API_IDS["MOVE"]
            # 设置参数
            js = {"x": x, "y": y, "z": z}
            request.parameter = json.dumps(js)
        request.header.identity.api_id = api_id
        self.request_pub.publish(request)



def main():
    rclpy.init()
    rclpy.spin(TwistBridge())
    rclpy.shutdown()



if __name__ == "__main__":
    main()



