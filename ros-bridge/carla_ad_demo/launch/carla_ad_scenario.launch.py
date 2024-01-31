import os
import sys

import launch
import launch_ros.actions
import json
from ament_index_python.packages import get_package_share_directory

from string import Template

s_file_dir = os.path.dirname(os.path.realpath('__file__'))

s_file_name = os.path.join(s_file_dir, 'opina_ws/src/opina_json_config/opina_scenarios.json')

s_res_name = os.path.join(s_file_dir, 'opina_ws/src/opina_user_data/')


with open(s_file_name) as f:
    scenarios=list()
    scenarios= json.load(f)
    for v in scenarios["scenarios_array"]:
        print("\n\n########scenarios information######\n\n")
        scenarios_path = v["Path"]
        scenarios_name = v["Scenario_id"]
        print(scenarios_path)



print(s_res_name)

ros_service_msg_string = '{{"scenario": {{"scenario_file": "/home/ubuntu/opina_ws/src/opina_user_data{}"}}}}'.format(scenarios_path)

# ros_service_msg_string = "{'scenario':{'scenario_file':'/home/opp/test_ws/src/opina_user_data/resource/scenarios/CyclistCrossing_358.xosc'}}"

print(ros_service_msg_string)

def generate_launch_description():
    ld = launch.LaunchDescription([

        launch.actions.ExecuteProcess(
            cmd=["ros2", "service", "call", "/scenario_runner/execute_scenario",
                 "carla_ros_scenario_runner_types/srv/ExecuteScenario", ros_service_msg_string],
            name='service_client_scenarios',
        )
    ])
    return ld



if __name__ == '__main__':

    generate_launch_description()