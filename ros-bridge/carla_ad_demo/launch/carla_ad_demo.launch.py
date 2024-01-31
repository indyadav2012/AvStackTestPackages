import os
import sys

import launch
import launch_ros.actions
import json
from ament_index_python.packages import get_package_share_directory


data = {
    "scenarios": []
}

#{ 'scenario': { 'scenario_file': '/home/opp/test_ws/src/opina_user_data/resource/scenarios/CyclistCrossing_358.xosc' } }

s_file_dir = os.path.dirname(os.path.realpath('__file__'))

s_file_name = os.path.join(s_file_dir, 'opina_ws/src/opina_json_config/opina_scenarios.json')


with open(s_file_name) as f:
    scenarios=list()
    scenarios= json.load(f)
    for v in scenarios["scenarios_array"]:
        print("\n\n########scenarios information######\n\n")
        scenarios_path = v["Path"]
        scenarios_name = v["Scenario_id"]
        final_path = os.path.join(get_package_share_directory('opina_user_data'), scenarios_path)
        print(scenarios_path)
        scenario = {
            "name": scenarios_name,
            "scenario_file": final_path
        }
        data["scenarios"].append(scenario)

        
ros_topic_msg_string = json.dumps(data, indent=4)
print(ros_topic_msg_string)

# ros_topic_msg_string = "{{ 'scenarios': [{{ 'name': '{}', 'scenario_file': '{}'}}] }}".format(
#     scenarios_name,os.path.join(get_package_share_directory('opina_user_data'), scenarios_path))

# ros_service_msg_string = "{'scenario':{'scenario_file':'/home/opp/test_ws/src/opina_user_data/resource/scenarios/CyclistCrossing_358.xosc'}}"

# ros_service_msg_string = "{{ 'scenario': [{{ 'scenario_file': '/home/opp/test_ws/src/opina_user_data/resource/scenarios/CyclistCrossing_358.xosc'}}] }}"

def launch_carla_spawn_object(context, *args, **kwargs):

    print("\n\n########MAIn demo file loaded ######\n\n")

    file_dir = os.path.dirname(os.path.realpath('__file__'))

    file_name = os.path.join(file_dir, 'opina_ws/src/opina_json_config/opina_vehicles.json')

    with open(file_name) as f:
        vehicles=list()
        vehicles= json.load(f)
        for v in vehicles["vehicle_array"]:
            print("\n\n########vehicle information######\n\n")
            vehicle_path = v["Path"]
            print(vehicle_path)

    # workaround to use launch argument 'role_name' as a part of the string used for the spawn_point param name
    spawn_point_param_name = 'spawn_point_' + \
        launch.substitutions.LaunchConfiguration('role_name').perform(context)

    carla_spawn_objects_launch = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory(
                'carla_spawn_objects'), 'carla_spawn_objects.launch.py')
        ),
        launch_arguments={
            'objects_definition_file': get_package_share_directory('opina_user_data') + vehicle_path,
            spawn_point_param_name: launch.substitutions.LaunchConfiguration('spawn_point')
        }.items()
    )

    return [carla_spawn_objects_launch]

def launch_target_speed_publisher(context, *args, **kwargs):
    topic_name = "/carla/" + launch.substitutions.LaunchConfiguration('role_name').perform(context) + "/target_speed"
    data_string = "{'data': " + launch.substitutions.LaunchConfiguration('target_speed').perform(context) + "}"
    return [
        launch.actions.ExecuteProcess(
            output="screen",
            cmd=["ros2", "topic", "pub", topic_name,
                 "std_msgs/msg/Float64", data_string, "--qos-durability", "transient_local"],
            name='topic_pub_target_speed')]

def generate_launch_description():
    ld = launch.LaunchDescription([
        launch.actions.DeclareLaunchArgument(
            name='host',
            default_value='localhost'
        ),
        launch.actions.DeclareLaunchArgument(
            name='port',
            default_value='2000'
        ),
        launch.actions.DeclareLaunchArgument(
            name='town',
            default_value='Town02'
        ),
        launch.actions.DeclareLaunchArgument(
            name='timeout',
            default_value='10'
        ),
        launch.actions.DeclareLaunchArgument(
            name='synchronous_mode_wait_for_vehicle_control_command',
            default_value='False'
        ),
        launch.actions.DeclareLaunchArgument(
            name='fixed_delta_seconds',
            default_value='0.05'
        ),
        launch.actions.DeclareLaunchArgument(
            name='role_name',
            default_value='ego_vehicle'
        ),
        launch.actions.DeclareLaunchArgument(
            name='spawn_point',
            default_value='127.4,-195.4,2,0,0,180'
        ),
        launch.actions.DeclareLaunchArgument(
            name='target_speed',
            default_value='8.33' # in m/s
        ),
        launch.actions.DeclareLaunchArgument(
            name='avoid_risk',
            default_value='True'
        ),
        launch.actions.DeclareLaunchArgument(
            name='sigterm_timeout',
            default_value='15'
        ),
        launch.actions.DeclareLaunchArgument(
            name='scenario_runner_path',
            default_value=os.environ.get('SCENARIO_RUNNER_PATH')
        ),
        launch.actions.DeclareLaunchArgument(
            name='control_id',
            default_value='control'
        ),
        launch_ros.actions.Node(
            package='carla_twist_to_control',
            executable='carla_twist_to_control',
            name='carla_twist_to_control',
            remappings=[
                (
                    ["/carla/",
                        launch.substitutions.LaunchConfiguration('role_name'), "/vehicle_control_cmd"],
                    ["/carla/",
                        launch.substitutions.LaunchConfiguration('role_name'), "/vehicle_control_cmd_manual"]
                )
            ],
            parameters=[
                {
                    'role_name': launch.substitutions.LaunchConfiguration('role_name')
                }
            ]
        ),
        launch.actions.OpaqueFunction(function=launch_carla_spawn_object),
        launch.actions.OpaqueFunction(function=launch_target_speed_publisher),
        launch.actions.IncludeLaunchDescription(
            launch.launch_description_sources.PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory(
                    'carla_ad_agent'), 'carla_ad_agent.launch.py')
            ),
            launch_arguments={
                'role_name': launch.substitutions.LaunchConfiguration('role_name'),
                'avoid_risk': launch.substitutions.LaunchConfiguration('avoid_risk')
            }.items()
        ),
        launch.actions.IncludeLaunchDescription(
            launch.launch_description_sources.PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory(
                    'carla_waypoint_publisher'), 'carla_waypoint_publisher.launch.py')
            ),
            launch_arguments={
                'host': launch.substitutions.LaunchConfiguration('host'),
                'port': launch.substitutions.LaunchConfiguration('port'),
                'timeout': launch.substitutions.LaunchConfiguration('timeout'),
                'role_name': launch.substitutions.LaunchConfiguration('role_name')
            }.items()
        ),
        launch.actions.IncludeLaunchDescription(
            launch.launch_description_sources.PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory(
                    'carla_ros_scenario_runner'), 'carla_ros_scenario_runner.launch.py')
            ),
            launch_arguments={
                'host': launch.substitutions.LaunchConfiguration('host'),
                'port': launch.substitutions.LaunchConfiguration('port'),
                'role_name': launch.substitutions.LaunchConfiguration('role_name'),
                'scenario_runner_path': launch.substitutions.LaunchConfiguration('scenario_runner_path'),
                'wait_for_ego': 'True'
            }.items()
        ),
        launch.actions.IncludeLaunchDescription(
            launch.launch_description_sources.PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory(
                    'carla_manual_control'), 'carla_manual_control.launch.py')
            ),
            launch_arguments={
                'role_name': launch.substitutions.LaunchConfiguration('role_name')
            }.items()
        ),
        launch.actions.ExecuteProcess(
            cmd=["ros2", "topic", "pub", "/carla/available_scenarios",
                 "carla_ros_scenario_runner_types/CarlaScenarioList", ros_topic_msg_string],
            name='topic_pub_vailable_scenarios',
        )
        # ,
        # launch.actions.IncludeLaunchDescription(
        #     launch.launch_description_sources.PythonLaunchDescriptionSource(
        #         os.path.join(get_package_share_directory(
        #             'carla_spawn_objects'), 'set_initial_pose.launch.py')
        #     ),
        #     launch_arguments={
        #         'role_name': launch.substitutions.LaunchConfiguration('role_name'),
        #         'control_id': launch.substitutions.LaunchConfiguration('control_id')
        #     }.items()
        # )
        
    ])
    return ld


if __name__ == '__main__':

    
            # for k in v.keys():

            #     print("{}:{}".format(k,v[k]))

    generate_launch_description()
