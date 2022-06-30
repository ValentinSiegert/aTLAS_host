import argparse
import aioprocessing
import importlib
import json
import multiprocessing as multiproc
import re
from config import LOG_PATH
from datetime import datetime
from distutils.util import strtobool
from os.path import exists


SCENARIO_NAMES = {
    'Basic Scenario': 3,
    'Basic Authority Scenario': 3,
    'Basic Topic Scenario': 3
}


class Evaluator:
    def run(self):
        self.connector.start()
        if self.lock_mode == "lock":
            self.send_queue.put({'type': 'lock_webUI'})
            received_message = self.receive_pipe.recv()
        elif self.lock_mode == "unlock":
            self.send_queue.put({'type': 'unlock_webUI'})
            received_message = self.receive_pipe.recv()
        else:
            scenario_run_ids = []
            for scenario, raps in SCENARIO_NAMES.items():
                for i in range(0, raps):
                    print(f"Starting scenario '{scenario}' run {i+1}...")
                    run_message = {
                        'type': 'run_scenario',
                        'scenario': {'name': scenario},
                        'is_evaluator': True
                    }
                    self.send_queue.put(run_message)
                    received_message = self.receive_pipe.recv()
                    if received_message['type'] == 'scenario_run_id':
                        print(f"Got run id for '{scenario}' run {i+1}: {received_message['scenario_run_id']}")
                    else:
                        raise RuntimeError(f"Did not receive scenario run ID after starting scenario '{scenario}' "
                                           f"run {i+1}")
                    received_message = self.receive_pipe.recv()
                    if received_message['type'] == 'scenario_results':
                        receiving_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        print(f"Scenario '{scenario}' run {i+1} finished as '{received_message['scenario_run_id']}' "
                              f"at {receiving_time} executed under {received_message['supervisor_amount']} "
                              f"supervisors.\n\n")
                        if self.print_to_file:
                            json_path = LOG_PATH / 'evaluator_log.json'
                            with open(json_path, 'r+' if exists(json_path) else 'w+') as json_file:
                                try:
                                    data = json.load(json_file)
                                except json.decoder.JSONDecodeError:
                                    data = {}
                                json_file.seek(0)
                                data[received_message['scenario_run_id']] = {
                                    'datetime': receiving_time,
                                    'scenario': scenario,
                                    'run': i+1,
                                    'supervisor_amount': received_message['supervisor_amount']}
                                print(json.dumps(data, indent=4), file=json_file)
        exit_message = {
            'type': 'end_socket'
        }
        self.send_queue.put(exit_message)

    def __init__(self, director_hostname, connector, logger_str, sec_conn=False, lock_mode='', print_to_file=False):
        self.director_hostname = director_hostname
        self.logger_str = logger_str
        self.lock_mode = lock_mode
        self.print_to_file = print_to_file
        # setup multiprocessing environment
        self.send_queue = aioprocessing.AioQueue()
        self.manager = multiproc.Manager()
        self.pipe_dict = self.manager.dict()
        self.receive_pipe, self.pipe_dict["evaluator"] = aioprocessing.AioPipe(False)
        # get correct connector to director
        module = importlib.import_module("connectors." + re.sub("([A-Z])", "_\g<1>", connector).lower()[1:])
        connector_class = getattr(module, connector)
        self.connector = connector_class(director_hostname, 0, self.send_queue, self.pipe_dict, sec_conn,
                                         no_registration=True if lock_mode else False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--connector", default="ChannelsConnector", choices=['ChannelsConnector'],
                        help="The connector class to use for connecting to director.")
    parser.add_argument("-d", "--director", default="127.0.0.1:8000",
                        help="The hostname of the director, where the evaluation script shall register at.")
    parser.add_argument("-log", "--logger", default="FileLogger", choices=['FileLogger'],
                        help="The logger class to use for logging trust values during a scenario run.")
    parser.add_argument("-wss", "--sec-socket", type=lambda x: bool(strtobool(x)), nargs='?', const=True,
                        default=False, help="Whether to use a secure websocket connection to the director.")
    parser.add_argument("-L", "--lock_mode", default="", choices=['lock', 'unlock'],
                        help="Changes the evaluator script to only lock or unlock the webUI.")
    parser.add_argument("-p", "--print", type=lambda x: bool(strtobool(x)), nargs='?', const=True,
                        default=False, help="Whether the evaluator prints log information to a file.")
    args = parser.parse_args()
    # set multiprocessing start method
    multiproc.set_start_method('spawn')
    # init supervisor as class and execute
    evaluator = Evaluator(args.director, args.connector, args.logger, args.sec_socket, args.lock_mode, args.print)
    evaluator.run()
