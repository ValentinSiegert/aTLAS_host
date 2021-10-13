import argparse
import importlib
import re
import multiprocessing as multiproc
import aioprocessing

from models import Scenario
from scenario_run import ScenarioRun


class Supervisor:
    """
    The class of an aTLAS supervisor. This module is also used as starting point for a trustlab environment part at one
    host and thus registers at the director by init as well as it represents the IO interface to the director
    and other supervisors in the lab.
    """
    def run(self):
        """
        Represents the run method of a supervisor who receives messages from the director and sends scenario dependent
        other messages to the director. It uses a connector class to handle the actual connection to the director and
        a ScenarioRun objects to represent each scenario run by one subprocess.

        :rtype: None
        """
        self.connector.start()
        while self.takes_new_scenarios:
            received_msg = self.receive_pipe.recv()
            if received_msg['type'] == "scenario_end":
                finished_scenario_run_id = received_msg['scenario_run_id']
                finished_scenario_run = self.scenario_runs[finished_scenario_run_id]
                finished_scenario_run.terminate()
                finished_scenario_run.join()
                del self.scenario_runs[finished_scenario_run_id]
                index_logger = [i for i in range(len(self.logger_semaphores)) if self.logger_semaphores[i]["used_by"] ==
                                finished_scenario_run_id][0]
                self.logger_semaphores[index_logger]["used_by"] = ""
                index_done = [i for i in range(len(self.observations_done)) if self.observations_done[i]["used_by"] ==
                              finished_scenario_run_id][0]
                self.observations_done[index_done]["used_by"] = ""
                self.send_queue.put(received_msg)
            elif received_msg['type'] == 'scenario_registration':
                # TODO: check if enough agents are left and scenario can be really started
                new_scenario_run_id = received_msg["scenario_run_id"]
                self.agents_in_use += len(received_msg["agents_at_supervisor"])
                recv_end, send_end = aioprocessing.AioPipe(False)
                self.pipe_dict[new_scenario_run_id] = send_end
                # creating logger for new scenario run with already registered semaphore
                index_logger, logger_semaphore_dict = next((index, semaphore) for (index, semaphore) in
                                                           enumerate(self.logger_semaphores) if semaphore["used_by"] == "")
                logger_semaphore = logger_semaphore_dict["semaphore"]
                self.logger_semaphores[index_logger]["used_by"] = new_scenario_run_id
                module = importlib.import_module("loggers." + re.sub("([A-Z])", "_\g<1>", self.logger_str).lower()[1:])
                logger_class = getattr(module, self.logger_str)
                logger = logger_class(new_scenario_run_id, logger_semaphore)
                # taking one observations_done list
                index_done, done_dict = next((index, obs_done_dict) for (index, obs_done_dict) in
                                             enumerate(self.observations_done) if obs_done_dict["used_by"] == "")
                observations_done = done_dict["list"]
                self.observations_done[index_done]["used_by"] = new_scenario_run_id
                # create and start scenario_run
                new_scenario_run = ScenarioRun(new_scenario_run_id, received_msg["agents_at_supervisor"],
                                               Scenario(**received_msg["scenario"]), self.ip_address, self.send_queue,
                                               recv_end, logger, observations_done, self.pipe_dict["supervisor"])
                self.scenario_runs[new_scenario_run_id] = new_scenario_run
                new_scenario_run.start()

    def __init__(self, ip_address, max_agents, director_hostname, connector, logger_str):
        self.ip_address = ip_address
        self.director_hostname = director_hostname
        self.max_agents = max_agents
        self.agents_in_use = 0
        self.takes_new_scenarios = True
        self.scenario_runs = {}
        self.logger_str = logger_str
        # setup multiprocessing environment
        self.send_queue = aioprocessing.AioQueue()
        self.manager = multiproc.Manager()
        self.pipe_dict = self.manager.dict()
        self.receive_pipe, self.pipe_dict["supervisor"] = aioprocessing.AioPipe(False)
        # setup logger semaphores for all possible scenario runs
        self.logger_semaphores = [{"semaphore": self.manager.Semaphore(1), "used_by": ""} for i in range(max_agents)]
        # setup observations_done lists
        self.observations_done = [{"list": self.manager.list(), "used_by": ""} for i in range(max_agents)]
        # get correct connector to director
        module = importlib.import_module("connectors." + re.sub("([A-Z])", "_\g<1>", connector).lower()[1:])
        connector_class = getattr(module, connector)
        self.connector = connector_class(director_hostname, max_agents, self.send_queue, self.pipe_dict)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--connector", default="ChannelsConnector", choices=['ChannelsConnector'],
                        help="The connector class to use for connecting to director.")
    parser.add_argument("-d", "--director", default="127.0.0.1:8000",
                        help="The hostname of the director, where the supervisor shall register at.")
    parser.add_argument("-ip", "--address", default="127.0.0.1",
                        help="The IP address of the supervisor itself.")
    parser.add_argument("-log", "--logger", default="FileLogger", choices=['FileLogger'],
                        help="The logger class to use for logging trust values during a scenario run.")
    parser.add_argument("max_agents", type=int,
                        help="The maximal number of agents existing in parallel under this supervisor.")
    args = parser.parse_args()
    # set multiprocessing start method
    multiproc.set_start_method('spawn')
    # init supervisor as class and execute
    supervisor = Supervisor(args.address, args.max_agents, args.director, args.connector, args.logger)
    supervisor.run()


