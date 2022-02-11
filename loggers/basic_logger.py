from abc import ABC, abstractmethod
from datetime import datetime
from models import Observation


class BasicLogger(ABC):
    """
    Provides the abstract class for any logger class to interface the logs and provide functionalities to
    read and write the logs' data lines.
    """
    @staticmethod
    @abstractmethod
    def apply_len_filter(lines, len_filter):
        """
        Returns the number of lines sorted by the newest first.

        :param lines: Data lines to filter in length.
        :type lines: list
        :param len_filter: Number of lines to return.
        :type len_filter: int
        :rtype: list
        """
        pass

    @abstractmethod
    def read_lines_from_agent_history(self, agent, len_filter=None):
        """
        Reads in the `agent`'s history log and returns all or max. len given by `len_filter`,
        where return is list of dicts representing information per line.

        :param agent: Agent to read log data lines about.
        :type agent: str
        :param len_filter: Number of lines to return.
        :type len_filter: int
        :rtype: list
        """
        pass

    @abstractmethod
    def read_lines_from_agent_topic_trust(self, agent, len_filter=None):
        """
        Reads in the agent`'s topic trust log and returns all or max. len given by `len_filter`,
        where return is list of dicts representing information per line.

        :param agent: Agent to read log data lines about.
        :type agent: str
        :param len_filter: Number of lines to return.
        :type len_filter: int
        :rtype: list
        """
        pass

    @abstractmethod
    def read_lines_from_agent_trust_log(self, agent, len_filter=None):
        """
        Reads in the `agent`'s trust logs and returns all or max. len given by `len_filter`,
        where return is list of dicts representing information per line.

        :param agent: Agent to read log data lines about.
        :type agent: str
        :param len_filter: Number of lines to return.
        :type len_filter: int
        :rtype: list
        """
        pass

    @abstractmethod
    def read_lines_from_agent_trust_log_str(self, agent, len_filter=None):
        """
        Reads in the `agent`'s trust logs and returns all or max. len given by `len_filter`,
        where return is list of log strings.

        :param agent: Agent to read log data lines about.
        :type agent: str
        :param len_filter: Number of lines to return.
        :type len_filter: int
        :rtype: list
        """
        pass

    @abstractmethod
    def read_lines_from_trust_log(self, len_filter=None):
        """
        Reads in the supervisor's local trust log and returns all or max. len given by `len_filter`,
        where return is list of dicts representing information per line.

        :param len_filter: Number of lines to return.
        :type len_filter: int
        :rtype: list
        """
        pass

    @abstractmethod
    def read_lines_from_trust_log_str(self, len_filter=None):
        """
        Reads in the supervisor's local trust log and returns all or max. len given by `len_filter`,
        where return is list of log strings.

        :param len_filter: Number of lines to return.
        :type len_filter: int
        :rtype: list
        """
        pass

    @abstractmethod
    def write_to_agent_history(self, agent, other_agent, history_value, resource_id=None):
        """
        Writes `history_value` with reference to `other_agent` in the `agent`'s history log.

        :param agent: Agent which log is updated.
        :type agent: str
        :param other_agent: Agent to write log for.
        :type other_agent: str
        :param history_value: Trust value.
        :type history_value: float or int
        :param resource_id: The ID of a resource to (dis)trust in.
        :type resource_id: str
        :rtype: None
        """
        pass

    @abstractmethod
    def write_bulk_to_agent_history(self, agent, history, resource_id=None):
        """
        Writes all items in `history` in the `agent`'s history log.

        :param agent: Agent which log is updated.
        :type agent: str
        :param history: History to add to history log with other agents as keys and their trust values as dict values.
        :type history: dict
        :param resource_id: The ID of a resource to (dis)trust in.
        :type resource_id: str
        :rtype: None
        """
        pass

    @abstractmethod
    def write_to_agent_topic_trust(self, agent, other_agent, topic, topic_value, resource_id=None):
        """
        Writes `topic_value` with reference to `other_agent` and `topic` in the `agent`'s topic log.

        :param agent: Agent which log is updated.
        :type agent: str
        :param other_agent: Agent to write log for.
        :type other_agent: str
        :param topic: Topic which trust value is related to.
        :type topic: str
        :param topic_value: Trust value.
        :type topic_value: float or int
        :param resource_id: The ID of a resource to (dis)trust in.
        :type resource_id: str
        :rtype: None
        """
        pass

    @abstractmethod
    def write_bulk_to_agent_topic_trust(self, agent, topic_trust, resource_id=None):
        """
        Writes all items in `topic_trust` in the `agent`'s topic log.

        :param agent: Agent which log is updated.
        :type agent: str
        :param topic_trust: Topic trusts with {other_agent: {topic: trust_value}}
        :type topic_trust: dict
        :param resource_id: The ID of a resource to (dis)trust in.
        :type resource_id: str
        :rtype: None
        """
        pass

    @abstractmethod
    def write_to_agent_message_log(self, observation):
        """
        Writes `observation` to message log.

        :param observation: Observation to log.
        :type observation: Observation
        :rtype: None
        """
        pass

    @abstractmethod
    def write_to_trust_log(self, agent, other_agent, trust_value, resource_id=None):
        """
        Writes `trust_value` with reference to `other_agent` in the trust log.

        :param agent: Agent which log is updated.
        :type agent: str
        :param other_agent: Agent to write log for.
        :type other_agent: str
        :param trust_value: Trust value.
        :type trust_value: float or int
        :param resource_id: The ID of a resource to (dis)trust in.
        :type resource_id: str
        :rtype: None
        """
        pass

    @abstractmethod
    def write_to_agent_trust_log(self, agent, metric_str, other_agent, trust_value, resource_id=None):
        """
        Writes `trust_value` with reference to `other_agent` and `metric_str` in the `agent`'s trust log.

        :param agent: Agent which log is updated.
        :type agent: str
        :param metric_str: Name of metric trust value is related to.
        :type metric_str: str
        :param other_agent: Agent to write log for.
        :type other_agent: str
        :param trust_value: Trust value.
        :type trust_value: float or int
        :param resource_id: The ID of a resource to (dis)trust in.
        :type resource_id: str
        :rtype: None
        """
        pass

    @staticmethod
    def get_current_time():
        # %f is current microsecond
        return datetime.now().strftime(BasicLogger.get_time_format_string())

    @staticmethod
    def get_time_format_string():
        return '%Y-%m-%d %H:%M:%S:%f'

    def __init__(self, scenario_run_id, semaphore):
        self.scenario_run_id = scenario_run_id
        self.semaphore = semaphore
