from launch import LaunchDescription
from launch_ros.actions import Node



def generate_launch_description():

    return LaunchDescription(
        [
            Node(
                package="go2_tutorial",
                executable="go2_ctrl",
            ),
        ]
    )