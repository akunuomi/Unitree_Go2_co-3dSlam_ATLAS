from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    go2_driver_pkg = get_package_share_directory("go2_driver_py")

    # 包含驱动功能
    go2_driver_launch = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource(
            launch_file_path=os.path.join(go2_driver_pkg, "launch", "driver.launch.py")
        )
    )
    # 包含巡航功能
    go2_tutorial_pkg = get_package_share_directory("go2_tutorial")

    # 包含巡航起停服务端，客户端专门调用
    cru_nav_node = Node(
        package="go2_tutorial",
        executable="go2_nav_server",
        # parameters=[
        #     os.path.join(go2_tutorial_pkg, "params", "go2_nav_server.yaml")
        # ],
    )

    return LaunchDescription(
        [
            go2_driver_launch,
            cru_nav_node,
        ]
    )
