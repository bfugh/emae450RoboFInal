import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='tb4_2',
        description='Robot namespace (e.g. tb4_2, tb4_4, tb4_6)'
    )

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=os.path.expanduser('~/terraformers-ws/maps/maze_map.yaml'),
        description='Full path to map yaml file'
    )

    namespace = LaunchConfiguration('namespace')
    map_path  = LaunchConfiguration('map')

    # Localization
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('turtlebot4_navigation'),
                'launch',
                'localization.launch.py'
            ])
        ]),
        launch_arguments={
            'namespace': namespace,
            'map': map_path,
        }.items()
    )

    # Nav2
    nav2 = TimerAction(
        period=20.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([
                        FindPackageShare('turtlebot4_navigation'),
                        'launch',
                        'nav2.launch.py'
                    ])
                ]),
                launch_arguments={
                    'namespace': namespace,
                }.items()
            )
        ]
    )

    # RViz
    rviz = TimerAction(
        period=12.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([
                        FindPackageShare('turtlebot4_viz'),
                        'launch',
                        'view_navigation.launch.py'
                    ])
                ]),
                launch_arguments={
                    'namespace': namespace,
                }.items()
            )
        ]
    )

    return LaunchDescription([
        namespace_arg,
        map_arg,
        localization,
        nav2,
        rviz,
    ])