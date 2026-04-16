"""
导航客户端
需求：客户端要发送数据到服务端并处理服务端的响应结果
流程：
    1.判断程序执行时参数个数是否合法
    2.初始化ROS2；
    3.创建actions客户端对象；
    4.连接服务端
    5.连接成功后，发送请求数据，并处理响应结果。连接失败 ，直接退出；
    6.调用spin函数，并传入节点对象指针
    7.释放资源


"""

import rclpy
from rclpy.node import Node
import sys
from rclpy.logging import get_logger
from rclpy.action import ActionClient
from go2_tutorial_inter.action import Nav

import time


class Go2NavClient(Node):
    def __init__(self):
        super().__init__("go2_nav_client")
        self.client = ActionClient(self, Nav, "nav")

    def connect_server(self):
        while not self.client.wait_for_server(timeout_sec=1.0):
            self.get_logger().info("等待服务端连接...")
            if not rclpy.ok():
                self.get_logger().error("程序被中断，无法连接到服务端！")
                return False
        self.get_logger().info("已连接到服务端！")
        return True

    # ======================================重难点==========================================

    def send_goal(self, x, y, m):
        # 组织数据
        goal_msg = Nav.Goal()
        goal_msg.x = x
        goal_msg.y = y
        goal_msg.m = m
        # 发送数据，并处理响应,一石二鸟，发送请求goal_msg的同时，处理连续反馈feedback_callback
        future: rclpy.task.Future = self.client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback
        )  # 异步发送
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future: rclpy.task.Future):
        goal_handle: rclpy.action.client.ClientGoalHandle = (
            future.result()
        )  # 获取服务端响应结果
        # self.get_logger().info("%s" % goal_handle.__str__())  ClientGoHandle对象
        if goal_handle.accepted:
            self.get_logger().info("请求被接收")
            future: rclpy.task.Future = (
                goal_handle.get_result_async()
            )  # 异步处理最终响应结果
            future.add_done_callback(self.result_response_callback)
        else:
            self.get_logger().error("请求被拒绝")
            rclpy.shutdown()

    def result_response_callback(self, future: rclpy.task.Future):
        result: Nav.Result = future.result().result  # 获取最终响应结果
        self.get_logger().info(
            f"最终响应结果：机器人当前坐标（x={result.point.x:.2f},y={result.point.y:.2f}）"
        )

    def feedback_callback(self, feedback_msg):
        # 处理连续反馈
        feedback: Nav.Feedback = feedback_msg.feedback
        self.get_logger().info(f"收到反馈：剩余距离={feedback.distance:.2f}")


# ======================================重点==========================================


def main():
    # 判断程序执行时参数个数是否合法
    if len(sys.argv) != 4:
        get_logger("rclpy").error("请提交三个浮点参数：x y m")
        return
    rclpy.init()
    # 创建actions客户端对象
    go2_nav_client = Go2NavClient()
    # 连接服务端
    flag = go2_nav_client.connect_server()
    # 连接成功后，发送请求数据，并处理响应结果。连接失败 ，直接退出；
    if not flag:
        get_logger("rclpy").error("连接服务端失败！")
        return
    get_logger("rclpy").info("连接服务端成功！发送请求")

    # 发送请求
    go2_nav_client.send_goal(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]))

    rclpy.spin(go2_nav_client)  # 一提到回调函数，肯定要调用spin函数，并传入节点对象指针
    rclpy.shutdown()


if __name__ == "__main__":
    main()
