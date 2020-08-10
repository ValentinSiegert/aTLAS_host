import json
import socket
from threading import Thread, Event
from trust_metrics import calc_trust_metrics
from artifacts.final_trust import final_trust
from models import Observation
from artifacts.recommendation import recommendation_response
from artifacts.popularity import popularity_response

untrustedAgents = []


class ClientThread(Thread):
    def run(self):
        try:
            message = self.conn.recv(2048)
            if message != '':
                decoded_msg = message.decode('utf-8')
                if decoded_msg == "END":
                    self.conn.close()
                elif decoded_msg.startswith("aTLAS_trust_protocol::"):
                    trust_protocol_head, trust_protocol_message = decoded_msg.split("::")
                    trust_operation = trust_protocol_message.split("_")[0]
                    trust_value = 0.0
                    if trust_operation == "recommendation":
                        trust_value = recommendation_response(self.agent, trust_protocol_message.split("_")[1],
                                                              self.logger)
                    elif trust_operation == "popularity":
                        trust_value = popularity_response(self.agent, self.discovery,
                                                          self.trust_thresholds['cooperation'], self.logger)
                    trust_response = f"{trust_protocol_head}::{trust_protocol_message}::{trust_value}"
                    self.conn.send(bytes(trust_response, 'UTF-8'))
                else:
                    observation = Observation(**json.loads(decoded_msg))
                    self.logger.write_to_agent_message_log(observation)
                    calc_trust_metrics(self.agent, observation.sender, observation.topic, self.agent_behavior,
                                       self.weights, self.trust_thresholds, self.authorities,
                                       self.logger, self.discovery)
                    trust_value = final_trust(self.agent, observation.sender, self.logger)
                    self.logger.write_to_agent_history(self.agent, observation.sender, trust_value)
                    self.logger.write_to_agent_topic_trust(self.agent, observation.sender, observation.topic, trust_value)
                    self.logger.write_to_trust_log(self.agent, observation.sender, trust_value)
                    # if float(trust_value) < self.scenario.trust_thresholds['lower_limit']:
                    #     untrustedAgents.append(other_agent)
                    #     print("+++" + current_agent + ", nodes beyond redemption: " + other_agent + "+++")
                    # if float(trust_value) > self.scenario.trust_thresholds['upper_limit'] or float(trust_value) > 1:
                    #     self.scenario.authority.append(current_agent[2:3])
                    # print("Node " + str(self.id) + " Server received data:", observation[2:-1])
                    self.conn.send(bytes('standard response', 'UTF-8'))
                    self.observations_done.append(observation.serialize())
        except BrokenPipeError:
            pass
        return True

    def __init__(self, conn, agent, agent_behavior, weights, trust_thresholds, authorities, logger,
                 observations_done, discovery):
        Thread.__init__(self)
        self.conn = conn
        self.agent = agent
        self.logger = logger
        self.agent_behavior = agent_behavior
        self.weights = weights
        self.trust_thresholds = trust_thresholds
        self.authorities = authorities
        self.observations_done = observations_done
        self.discovery = discovery


class AgentServer(Thread):
    def run(self):
        buffer_size = 2048
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_server.bind((self.ip_address, self.port))
        print(f"Agent '{self.agent}' listens on {self.ip_address}:{self.port}")
        while not self._stop_event.isSet():
            tcp_server.listen(4)
            (conn, (ip, port)) = tcp_server.accept()
            print(f"Connection established with: {ip}:{port}")
            new_thread = ClientThread(conn, self.agent, self.agent_behavior, self.weights, self.trust_thresholds,
                                      self.authorities, self.logger, self.observations_done, self.discovery)
            new_thread.start()
            self.threads.append(new_thread)
        for thread in self.threads:
            if thread.is_alive():
                thread.join()

    def end_server(self):
        self._stop_event.set()
        close_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        close_sock.connect((self.ip_address, self.port))
        close_sock.send(bytes("END", 'UTF-8'))
        close_sock.close()

    def set_discovery(self, discovery):
        self.discovery = discovery

    def __init__(self, agent, ip_address, port, agent_behavior, weights, trust_thresholds, authorities, logger,
                 observations_done):
        Thread.__init__(self)
        self.agent = agent
        self.ip_address = ip_address
        self.port = port
        self.threads = []
        self.logger = logger
        self.agent_behavior = agent_behavior
        self.weights = weights
        self.trust_thresholds = trust_thresholds
        self.authorities = authorities
        self.observations_done = observations_done
        self._stop_event = Event()
        self.discovery = {}

