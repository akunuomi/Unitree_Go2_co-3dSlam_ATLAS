from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


"""
加载一下驱动
加载自实现的节点
"""


def generate_launch_description():

    go2_driver_pkg = get_package_share_directory("go2_driver_py")

    go2_driver_launch = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource(
            launch_file_path=os.path.join(go2_driver_pkg, "launch", "driver.launch.py")
        )
    )

    return LaunchDescription(
        [
            go2_driver_launch,
            Node(
                package="go2_tutorial",
                executable="go2_state",
                parameters=[
                    os.path.join(
                        get_package_share_directory("go2_tutorial"),
                        "params",
                        "go2_state.yaml",
                    )
                ]
            ),
            
        ]
    )
