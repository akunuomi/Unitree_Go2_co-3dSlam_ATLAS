from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition
from launch.actions import DeclareLaunchArgument


def generate_launch_description():
    # 获取功能包的路径
    go2_description_pkg = get_package_share_directory("go2_description")

    use_joint_state_publisher = DeclareLaunchArgument(
        name="use_joint_state_publisher",
        default_value="true",
    )

    # 只用xacro读取urdf文件里面的内容
    # robot_desc = ParameterValue(
    # 	Command(
    # 		[
    # 			"xacro ",
    # 			os.path.join(go2_description_pkg, "urdf", "go2_description.urdf"),
    # 		]
    # 	)
    # )

    # 相比于上面导入urdf文件内容的方法，下方的方法的urdf有一个默认值，可以再终端输入时修改，以便urdf文件路径发生变化时可以灵活应对！！！
    # 注意这个model需要放进LaunchDescription列表里！！！就是最后一个函数里！！！
    model = DeclareLaunchArgument(
        name="urdf_path",
        default_value=os.path.join(go2_description_pkg, "urdf", "go2_description.urdf"),
    )
    robot_desc = ParameterValue(
        Command(
            [
                "xacro ",
                LaunchConfiguration("urdf_path"),
            ]
        )
    )
    # robot_state_publisher节点 === 加载机器人的urdf文件
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_desc}],
    )
    # joint_state_publisher节点 === 发布关节状态信息 （非固定关节）
    # 以后更合理的方式是由程序动态地获取关节信息并发布
    # 这个节点的启动应该灵活设置，是有条件的
    joint_state_publisher_node = Node(
        package="joint_state_publisher",  # 功能包
        executable="joint_state_publisher",  # 可执行文件
        condition=IfCondition(LaunchConfiguration("use_joint_state_publisher")),
    )

    return LaunchDescription(
        [
            model,
            use_joint_state_publisher,
            robot_state_publisher_node,
            joint_state_publisher_node,
        ]
    )
