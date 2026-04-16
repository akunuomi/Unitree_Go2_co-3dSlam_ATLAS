"""
编写键盘控制节点

实现规则

实现流程：
1引入读取键盘输入的库
2编写ros2节点，创建话题发布对象
3编写按键映射逻辑


他是做了一个字典，按键对应指令id和参数

"""

import rclpy
from rclpy.node import Node
from unitree_api.msg import Request
import termios
import sys
import tty
import threading
import json


moveBindings = {
    "w": (1, 0, 0, 0),  # x*1,y*0,z*0,角速度*0
    "e": (1, 0, 0, -1),
    "a": (0, 0, 0, 1),
    "d": (0, 0, 0, -1),
    "q": (1, 0, 0, 1),
    "s": (-1, 0, 0, 0),
    "c": (-1, 0, 0, 1),
    "z": (-1, 0, 0, -1),
    "E": (1, -1, 0, 0),
    "W": (1, 0, 0, 0),
    "A": (0, 1, 0, 0),
    "D": (0, -1, 0, 0),
    "Q": (1, 1, 0, 0),
    "S": (-1, 0, 0, 0),
    "C": (-1, -1, 0, 0),
    "Z": (-1, 1, 0, 0),
}

SpeedBindings = {
    "r": (1.1, 1.1),  # 增加线速度和角速度
    "t": (0.9, 0.9),  # 减小线速度和角速度
    "f": (1.1, 1),  # 增加线速度
    "g": (0.9, 1),  # 减小线速度
    "v": (1, 1.1),  # 增加角速度
    "b": (1, 0.9),  # 减小角速度
}


class TeleopNode(Node):
    def __init__(self):
        super().__init__("teleop_node")
        self.pub = self.create_publisher(Request, "/api/sport/request", 10)
        # 以参数方式设置线速度和角速度
        self.declare_parameter("speed", 0.2)  # x和y线速度默认0.2m/s
        self.declare_parameter("angular", 0.5)  # 角速度默认0

        self.speed = self.get_parameter("speed").value
        self.angular = self.get_parameter("angular").value

    # 发布速度指令
    def publish(self, api_id, x=0.0, y=0.0, z=0.0):
        req = Request()
        req.header.identity.api_id = api_id
        js = {"x": x, "y": y, "z": z}
        req.parameter = json.dumps(js)
        self.pub.publish(req)


# 读取按键
def getkey(settings):
    # 设置读取模式
    tty.setraw(sys.stdin.fileno())
    # 获取一个按键
    key = sys.stdin.read(1)
    # 恢复终端原始设置
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    # 返回按键值
    return key


def main():
    # 读取键盘输入的库
    # 1.获取标准输入流终端属性并返回
    settings = termios.tcgetattr(sys.stdin)
    # 2.ros2节点，创建话题发布对象,单独一个线程
    rclpy.init()
    teleopnode = TeleopNode()
    spinner = threading.Thread(target=rclpy.spin, args=(teleopnode,))
    spinner.start()

    # 3.循环读取按键,并映射到对应的指令
    # 异常处理,利用finally保证程序退出时恢复终端设置,保证资源释放
    try:
        while True:
            key = getkey(settings)
            # print(f"按键：{key}")
            # if key == 'h':
            # 	teleopnode.publish(1016)
            # print("发送指令：1016")
            # 结束终端判断
            if key == "\x03":  # Ctrl-C
                teleopnode.publish(1002)  # 平衡站立
                break
            # 运动模式切换
            elif key == "h":
                teleopnode.publish(1016)  # 运动模式切换

            # 运动控制 x线速度 y线速度 z角速度
            elif key in moveBindings.keys():
                x_bind = moveBindings[key][0]
                y_bind = moveBindings[key][1]
                z_bind = moveBindings[key][3]

                teleopnode.publish(
                    1001,
                    x=x_bind * teleopnode.speed,
                    y=y_bind * teleopnode.speed,
                    z=z_bind * teleopnode.angular,
                )  # 运动控制指令id为1001
            # 速度调整
            elif key in SpeedBindings.keys():
                s_bind = SpeedBindings[key][0]
                a_bind = SpeedBindings[key][1]
                teleopnode.speed *= s_bind
                teleopnode.angular *= a_bind
                print(
                    f"当前线速度: {teleopnode.speed:.2f} m/s, 角速度: {teleopnode.angular:.2f} rad/s"
                )

            else:
                # 停止运动
                teleopnode.publish(1002)
    finally:
        teleopnode.publish(1002)  # 平衡站立
        rclpy.shutdown()


if __name__ == "__main__":
    main()
