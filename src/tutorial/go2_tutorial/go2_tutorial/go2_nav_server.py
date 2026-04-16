"""
导航服务端
                                需求：
                                1.处理客户端请求
                                提交的请求为浮点数（前进距离）
                                如果大于0,那么控制机器人往前运动，否则认为数据不合法
                                2.处理客户端取消请求
                                当客户端发送取消请求时，需要让机器人停止运动
                                3.产生连续反馈和最终响应
                                根据机器人当前坐标，结合起点坐标，结合前进距离计算剩余距离并周期性反馈
                                当机器人到达目标点，响应机器人坐标
                                实现：
                                1.创建action服务端，执行相关操作
                                2发布速度指令控制机器人运动
                                3.需要订阅里程计信息获取机器人坐标
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from go2_tutorial_inter.action import Nav
from geometry_msgs.msg import Point
from nav_msgs.msg import Odometry
from unitree_api.msg import Request
from .sport_model import ROBOT_SPORT_API_IDS
import json
from rclpy.action.server import CancelResponse, GoalResponse, ServerGoalHandle
import time
import math
import threading
from rclpy.executors import MultiThreadedExecutor


class Go2NavServer(Node):
    def __init__(self):
        super().__init__("go2_nav_server")

        # 创建一个空point
        self.point = Point()
        # 订阅里程计信息，获取机器人的位置信息
        self.odom_sub = self.create_subscription(
            Odometry, "odom", self.odom_callback, 10
        )
        # 设置巡航参数
        self.declare_parameter("speed", 0.6)

        # 创建速度控制的发布对象
        self.api_id = ROBOT_SPORT_API_IDS["BALANCESTAND"]  # 巡航的api_id
        self.req_pub = self.create_publisher(Request, "/api/sport/request", 10)

        # 增加一个标志位，用于控制是否发布指令
        self.publishing = False
        self.motion_dir_x = 1.0
        self.motion_dir_y = 0.0
        self.target_point = Point()

        self.timer = self.create_timer(0.1, self.on_timer)
        self.action_server = ActionServer(
            self,
            Nav,
            "nav",
            self.execute,
            goal_callback=self.goal_cb,
            cancel_callback=self.cancel_cb,
        )

    def execute(self, goal_handle: ServerGoalHandle):  # 主逻辑处理函数

        feedback = Nav.Feedback()

        # 生成连续反馈
        while rclpy.ok():
            # 休眠
            time.sleep(0.5)
            # 组织数据
            # 剩余距离（当前点到目标点）
            dis_x = self.target_point.x - self.point.x
            dis_y = self.target_point.y - self.point.y
            distance = math.sqrt(math.pow(dis_x, 2) + math.pow(dis_y, 2))
            feedback.distance = distance  # 前进距离
            # 发布
            goal_handle.publish_feedback(feedback)  # 反馈剩余距离
            # 退出
            if distance <= 0.2:  # 到达目标点，认为任务完成
                self.api_id = ROBOT_SPORT_API_IDS["STOPMOVE"]  # 停止运动
                self.get_logger().info("到达目标点，任务完成")
                # 给一点时间让STOPMOVE指令发布出去
                time.sleep(1.0)
                self.publishing = False
                break

        # 响应最终结果
        goal_handle.succeed()  # 设置状态为成功
        result = Nav.Result()
        result.point = self.point  # 机器人当前坐标
        return result  # 最终响应，返回机器人坐标

    # 目标处理，无条件接受
    def goal_cb(self, goal_request: Nav.Goal):  # 处理客户端请求
        vector_norm = math.sqrt(
            math.pow(goal_request.x, 2) + math.pow(goal_request.y, 2)
        )

        if goal_request.m > 0.0 and vector_norm > 1e-6:
            self.start_point = Point()  # 起点坐标（拷贝，避免与self.point引用同一对象）
            self.start_point.x = self.point.x
            self.start_point.y = self.point.y
            self.start_point.z = self.point.z

            # 方向向量归一化
            self.motion_dir_x = goal_request.x / vector_norm
            self.motion_dir_y = goal_request.y / vector_norm

            # 计算目标点：起点 + 方向 * 距离m
            self.target_point = Point()
            self.target_point.x = (
                self.start_point.x + self.motion_dir_x * goal_request.m
            )
            self.target_point.y = (
                self.start_point.y + self.motion_dir_y * goal_request.m
            )
            self.target_point.z = self.start_point.z

            self.get_logger().info(
                f"提交的数据合法，机器人运动，向量=({goal_request.x:.2f},{goal_request.y:.2f})，距离={goal_request.m:.2f}m"
            )
            self.api_id = ROBOT_SPORT_API_IDS["MOVE"]  # 巡航的api_id
            self.publishing = True  # 开始发布指令
            return GoalResponse.ACCEPT
        else:
            self.get_logger().error("提交的数据非法：要求m>0且(x,y)不能同时为0")
            self.api_id = ROBOT_SPORT_API_IDS["STOPMOVE"]  # 巡航的api_id
            self.publishing = False
            return GoalResponse.REJECT

    # 无条件取消
    def cancel_cb(self, cancel_request):  # 处理客户端取消请求
        return CancelResponse.REJECT

    # 里程计回调函数，获取位置信息
    def odom_callback(self, msg: Odometry):
        self.point = msg.pose.pose.position

    def on_timer(self):
        # 仅在有活动任务时或者是需要保持某种状态时发布
        if not self.publishing:
            return

        # 发布速度指令，保持巡航状态
        request = Request()
        # self.get_logger().info(f"发布速度指令，api_id={self.api_id}")
        request.header.identity.api_id = self.api_id  # 巡航的api_id
        # 设置速度参数
        js = {
            "x": self.motion_dir_x * self.get_parameter("speed").value,
            "y": self.motion_dir_y * self.get_parameter("speed").value,
            "z": 0.0,
        }
        request.parameter = json.dumps(js)
        self.req_pub.publish(request)


def main():
    rclpy.init()
    # 使用多线程执行器运行节点
    node = Go2NavServer()

    # 创建多线程执行器
    executor = MultiThreadedExecutor()
    # 把节点添加进执行器
    executor.add_node(node)
    # 调节执行器的spin
    executor.spin()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
