import json
from threading import Thread
from trust.trust_evaluation import eval_trust
from trust.init_trust import eval_trust_with_init
from models import Observation, init_scale_object
from trust.artifacts.content_trust.recommendation import recommendation_response
from trust.artifacts.content_trust.popularity import popularity_response
from config import BUFFER_SIZE
from datetime import datetime
from loggers.basic_logger import BasicLogger


class ServerThread(Thread):
    def run(self):
        try:
            message = self.conn.recv(BUFFER_SIZE)
            if message != '':
                decoded_msg = message.decode('utf-8')
                if decoded_msg == "END":
                    self.conn.close()
                elif decoded_msg.startswith("aTLAS_trust_protocol::"):
                    trust_protocol_head, trust_protocol_message = decoded_msg.split("::")
                    trust_operation = trust_protocol_message.split("_")[0]
                    trust_value = 0.0
                    if trust_operation == "recommendation":
                        resource_id = trust_protocol_message.split("_")[1]
                        recency_str = trust_protocol_message.split("_")[-1]
                        recency_limit = datetime.strptime(recency_str, BasicLogger.get_time_format_string())
                        trust_value = recommendation_response(self.agent, resource_id, recency_limit, self.scale,
                                                              self.logger)
                    elif trust_operation == "popularity":
                        resource_id = trust_protocol_message.split("_")[1]
                        recency_str = trust_protocol_message.split("_")[-1]
                        recency_limit = datetime.strptime(recency_str, BasicLogger.get_time_format_string())
                        trust_value = popularity_response(self.agent, resource_id, recency_limit, self.scale,
                                                          self.logger)
                    trust_response = f"{trust_protocol_head}::{trust_protocol_message}::{trust_value}"
                    self.conn.send(bytes(trust_response, 'UTF-8'))
                else:
                    observation = Observation(**json.loads(decoded_msg))
                    resource_id = None
                    if 'uri' in observation.details:
                        resource_id = observation.details['uri']
                    self.logger.write_to_agent_message_log(observation)
                    if '__init__' in self.agent_behavior:
                        trust_value = eval_trust_with_init(self.agent, observation.sender, observation.topic,
                                                           self.agent_behavior, self.scale, self.logger, self.discovery)
                    else:
                        trust_value = eval_trust(self.agent, observation.sender, observation, self.agent_behavior,
                                                 self.scale, self.logger, self.discovery)
                    self.logger.write_to_agent_history(self.agent, observation.sender, trust_value, resource_id)
                    self.logger.write_to_trust_log(self.agent, observation.sender, trust_value, resource_id)

                    # topic trust log is written within the trust evaluation
                    # self.logger.write_to_agent_topic_trust(self.agent, observation.sender, observation.topic, trust_value, resource_id)

                    # TODO: how to work with trust decisions in general?
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

    def __init__(self, conn, agent, agent_behavior, scale, logger, observations_done, discovery):
        Thread.__init__(self)
        self.conn = conn
        self.agent = agent
        self.logger = logger
        self.agent_behavior = agent_behavior
        self.scale = init_scale_object(scale)
        self.observations_done = observations_done
        self.discovery = discovery
