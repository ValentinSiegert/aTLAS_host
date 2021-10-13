import json
import socket
from contextlib import closing
import multiprocessing as multiproc

from models import Observation
from exec.agent_server import AgentServer
from exec.agent_client import AgentClient


class ScenarioRun(multiproc.Process):
    """
    The supervisors subprocess proxy for each scenario run to be executed with at least one agent at the supervisor.
    """
    @staticmethod
    def find_free_port():
        """
        Find a free TCP port to use for a new socket.
        Method copied from https://stackoverflow.com/a/45690594

        :return: Free port number.
        """
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    def prepare_scenario(self):
        """
        Prepare the scenario run by `1)` logging for all agents their initial trust value logs,
        `2)` initializing all local agents' server(s), `3)` sending the local discovery to the director,
        and `4)` receiving and saving the global discovery with all agents' addresses.
        """
        local_discovery = {}
        # logging for all Agents their trust history and their topic values if given
        for agent in self.scenario.agents:
            self.logger.write_bulk_to_agent_history(agent, self.scenario.history[agent])
            if self.scenario.agent_uses_metric(agent, 'content_trust.topic'):
                self.logger.write_bulk_to_agent_topic_trust(agent, self.scenario.agents_with_metric(
                    'content_trust.topic')[agent])
        # creating servers
        for agent in self.agents_at_supervisor:
            free_port = self.find_free_port()
            local_discovery[agent] = self.ip_address + ":" + str(free_port)
            server = AgentServer(agent, self.ip_address, free_port, self.scenario.metrics_per_agent[agent],
                                 self.scenario.scales_per_agent[agent], self.logger, self.observations_done)
            self.threads_server.append(server)
            server.start()
        discovery_message = {"type": "agent_discovery", "scenario_run_id": self.scenario_run_id,
                             "discovery": local_discovery}
        self.send_queue.put(discovery_message)
        self.discovery = self.receive_pipe.recv()["discovery"]
        for thread in self.threads_server:
            thread.set_discovery(self.discovery)
        print(self.discovery)

    def assert_scenario_start(self):
        """
        Wait for the scenario run to start by receiving the respective message from the director.
        It further asserts that all scenario's agents have to be discovered before the start and
        thus throws an AssertionError if not.

        :rtype: None
        :raises AssertionError: Not all agents are discovered or the received message is not the start signal.
        """
        start_confirmation = self.receive_pipe.recv()
        assert list(self.discovery.keys()) == self.scenario.agents  # all agents need to be discovered
        assert start_confirmation["scenario_status"] == "started"
        self.scenario_runs = True

    def run(self):
        """
        Executes the scenario run by first preparing the scenario and then awaiting the scenario to start.
        During scenario run, Supervisor is within this run method scheduling the observations by starting
        local observations if all observations before were already executed. Further, it resolves the before
        dependencies of still existing observations to be executed by an agent under this supervisor if receiving
        an observation_done message. It sends out an observation_done message itself if one observation was executed
        by one agent under this supervisor.

        :rtype: None
        """
        self.prepare_scenario()
        self.assert_scenario_start()
        while self.scenario_runs:
            observation_dict = next((obs for obs in self.observations_to_exec if len(obs["before"]) == 0), None)
            if observation_dict is not None:
                observation = Observation(**observation_dict)
                ip, port = self.discovery[observation.receiver].split(":")
                client_thread = AgentClient(ip, int(port), json.dumps(observation_dict))
                self.threads_client.append(client_thread)
                client_thread.start()
                self.observations_to_exec.remove(observation_dict)
            observation_done_dict = next((obs for obs in self.observations_done), None)
            if observation_done_dict is not None:
                done_message = {
                    "type": "observation_done",
                    "scenario_run_id": self.scenario_run_id,
                    "observation_id": observation_done_dict["observation_id"],
                    "receiver": observation_done_dict["receiver"],
                    "trust_log": '<br>'.join(self.logger.read_lines_from_trust_log()),
                    "receiver_trust_log": '<br>'.join(self.logger.read_lines_from_agent_trust_log(
                        observation_done_dict["receiver"])),
                }
                self.send_queue.put(done_message)
                self.remove_observation_dependency([observation_done_dict["observation_id"]])
                self.observations_done.remove(observation_done_dict)
                print(f"Exec after exec observation: {self.observations_to_exec}")
            if self.receive_pipe.poll():
                message = self.receive_pipe.recv()
                if message['type'] == 'observation_done':
                    self.remove_observation_dependency(message["observations_done"])
                    print(f"Exec after done message: {self.observations_to_exec}")
                if message['type'] == 'scenario_end':
                    for thread in self.threads_client:
                        if thread.is_alive():
                            thread.join()
                    for thread in self.threads_server:
                        thread.end_server()
                        if thread.is_alive():
                            thread.join()
                    self.scenario_runs = False
        end_message = {
            'type': 'scenario_end',
            'scenario_run_id': self.scenario_run_id
        }
        self.supervisor_pipe.send(end_message)

    def remove_observation_dependency(self, observations_done):
        """
        Removes any observations given from all `observations_to_exec`'s `before` dependencies.

        :param observations_done: All observation ids to be removed from the `before` dependency.
        :type observations_done: list
        :rtype: None
        """
        for observation in self.observations_to_exec:
            observation["before"] = [obs_id for obs_id in observation["before"] if obs_id not in observations_done]

    def __init__(self, scenario_run_id, agents_at_supervisor, scenario, ip_address, send_queue, receive_pipe, logger,
                 observations_done, supervisor_pipe):
        multiproc.Process.__init__(self)
        self.scenario_run_id = scenario_run_id
        self.agents_at_supervisor = agents_at_supervisor
        self.ip_address = ip_address
        self.send_queue = send_queue
        self.receive_pipe = receive_pipe
        self.discovery = {}
        self.threads_server = []
        self.threads_client = []
        self.scenario = scenario
        self.logger = logger
        self.scenario_runs = False
        self.observations_done = observations_done
        self.supervisor_pipe = supervisor_pipe
        # filter observations that have to start at this supervisor
        self.observations_to_exec = [obs for obs in scenario.observations if obs["sender"] in agents_at_supervisor]