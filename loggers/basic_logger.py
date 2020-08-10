from abc import ABC, abstractmethod
from datetime import datetime


class BasicLogger(ABC):
    @abstractmethod
    def readlines_from_agent_history(self, agent, len_filter=None):
        pass

    @abstractmethod
    def readlines_from_agent_trust_log(self, agent, len_filter=None):
        pass

    @abstractmethod
    def readlines_from_agent_topic_trust(self, agent, len_filter=None):
        pass

    @abstractmethod
    def readlines_from_trust_log(self, len_filter=None):
        pass

    @abstractmethod
    def write_to_agent_history(self, agent, other_agent, history_value):
        pass

    @abstractmethod
    def write_bulk_to_agent_history(self, agent, history):
        pass

    @abstractmethod
    def write_to_agent_topic_trust(self, agent, other_agent, topic, topic_value):
        pass

    @abstractmethod
    def write_bulk_to_agent_topic_trust(self, agent, topic_trust):
        pass

    @abstractmethod
    def write_to_agent_message_log(self, observation):
        pass

    @abstractmethod
    def write_to_trust_log(self, agent, other_agent, trust_value):
        pass

    @abstractmethod
    def write_to_agent_trust_log(self, agent, metric_str, other_agent, trust_value):
        pass

    @staticmethod
    def get_current_time():
        # %f is current microsecond
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")

    def __init__(self, scenario_run_id, semaphore):
        self.scenario_run_id = scenario_run_id
        self.semaphore = semaphore

