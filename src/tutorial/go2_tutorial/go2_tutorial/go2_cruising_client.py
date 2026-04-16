"""
需求：客户端向服务端发送整形数据，并接受服务端返回的巡航点数据。
流程：
1：判断提交的数据是否合法
2：ROS2初始化
3：创建自定义节点类对象
4：连接服务端
5：连接成功后向服务端发送数据
6：处理响应结果
7：资源释放

"""

import rclpy
from rclpy.logging import get_logger
from rclpy.node import Node
import sys
from go2_tutorial_inter.srv import Cruising
from rclpy.task import Future


class Go2CruisingClient(Node):
    def __init__(self):
        super().__init__("go2_cruising_client")
        self.client = self.create_client(Cruising, "cruising")

    def connect_Server(self):
        while not self.client.wait_for_service(timeout_sec=1.0):
            if not rclpy.ok():
                get_logger("rclpy").error("服务连接被中断")
                return False
            self.get_logger().info("正在等待服务端...")
        return True

    def send_request(self, flag: int) -> Future:
        # 组织数据
        request = Cruising.Request()
        request.flag = flag
        # 发送请求并等待响应
        return self.client.call_async(request)


def main():
    # 1：判断提交的数据是否合法
    if len(sys.argv) != 2:
        get_logger("rclpy").error("请提供一个整数参数，0表示停止巡航，1表示开始巡航")
        return
    # 2：ROS2初始化
    rclpy.init()
    # 3：创建自定义节点类对象
    cru_client = Go2CruisingClient()
    # 4：连接服务端
    flag = cru_client.connect_Server()
    if not flag:
        return
    # 5：连接成功后向服务端发送数据
    future = cru_client.send_request(int(sys.argv[1]))
    # 6：处理响应结果
    rclpy.spin_until_future_complete(cru_client, future)
    if future.done():
        response = future.result()
        get_logger("rclpy").info(
            "机器人坐标：（%.2f, %.2f）" % (response.point.x, response.point.y)
        )
    else:
        get_logger("rclpy").info("服务调用失败")
    # 7：资源释放
    rclpy.shutdown()


if __name__ == "__main__":
    main()
