from pathlib import Path
import os
import re
from loggers.basic_logger import BasicLogger
from config import LOG_PATH


class FileLogger(BasicLogger):
    """
    Provides the class to log data lines from and to text files by inheriting from `BasicLogger`.
    """
    if not LOG_PATH.exists():
        os.mkdir(LOG_PATH)

    @staticmethod
    def apply_len_filter(lines, len_filter):
        len_filter = 0 - len_filter if len_filter > 0 else len_filter
        lines = lines[len_filter:]
        return lines

    def read_lines_from_agent_history(self, agent, len_filter=None):
        log_path = self.log_path / f"{agent}_history.log"
        rex = r"(?P<date_time>.*), history trust on '(?P<other_agent>.*)': (?P<trust_value>.*)"
        rex_resource = r"(?P<date_time>.*), history trust on '(?P<other_agent>.*)' " \
                       r"in resource <(?P<resource_id>.*)>: (?P<trust_value>.*)"
        groups = ['date_time', 'other_agent', 'trust_value']
        groups_resource = ['date_time', 'other_agent', 'resource_id', 'trust_value']
        return self.read_in_dicts(log_path, rex, rex_resource, groups, groups_resource, len_filter)

    def read_lines_from_agent_topic_trust(self, agent, len_filter=None):
        log_path = self.log_path / f"{agent}_topic.log"
        rex = r"(?P<date_time>.*), topic trust on '(?P<other_agent>.*)' regarding '(?P<topic>.*)': (?P<trust_value>.*)"
        rex_resource = r"(?P<date_time>.*), topic trust on '(?P<other_agent>.*)' in resource <(?P<resource_id>.*)> " \
                       r"regarding '(?P<topic>.*)': (?P<trust_value>.*)"
        groups = ['date_time', 'other_agent', 'topic', 'trust_value']
        groups_resource = ['date_time', 'other_agent', 'resource_id', 'topic', 'trust_value']
        return self.read_in_dicts(log_path, rex, rex_resource, groups, groups_resource, len_filter)

    def read_lines_from_agent_trust_log(self, agent, len_filter=None):
        log_path = self.log_path / f"{agent}_trust_log.log"
        rex = r"(?P<date_time>.*), '(?P<metric_str>.*)' trust value for '(?P<other_agent>.*)': (?P<trust_value>.*)"
        rex_resource = r"(?P<date_time>.*), '(?P<metric_str>.*)' trust value for '(?P<other_agent>.*)' " \
                       r"in resource <(?P<resource_id>.*)>: (?P<trust_value>.*)"
        groups = ['date_time', 'metric_str', 'other_agent', 'trust_value']
        groups_resource = ['date_time', 'metric_str', 'other_agent', 'resource_id', 'trust_value']
        return self.read_in_dicts(log_path, rex, rex_resource, groups, groups_resource, len_filter)

    def read_lines_from_agent_trust_log_str(self, agent, len_filter=None):
        log_path = self.log_path / f"{agent}_trust_log.log"
        return self.read_lines(log_path, len_filter)

    def read_lines_from_trust_log(self, len_filter=None):
        log_path = self.log_path / f"trust_log.log"
        rex = r"(?P<date_time>.*), '(?P<agent>.*)' trusts '(?P<other_agent>.*)': (?P<trust_value>.*)"
        rex_resource = r"(?P<date_time>.*), '(?P<agent>.*)' trusts '(?P<other_agent>.*)' " \
                       r"in resource <(?P<resource_id>.*)>: (?P<trust_value>.*)"
        groups = ['date_time', 'agent', 'other_agent', 'trust_value']
        groups_resource = ['date_time', 'agent', 'other_agent', 'resource_id', 'trust_value']
        return self.read_in_dicts(log_path, rex, rex_resource, groups, groups_resource, len_filter)

    def read_lines_from_trust_log_str(self, len_filter=None):
        log_path = self.log_path / f"trust_log.log"
        return self.read_lines(log_path, len_filter)

    def read_lines(self, log_path, len_filter, strip=False):
        """
        Reads file in list of strings with only recent number of elements if len_filter is set.

        :param log_path: File to be read.
        :type log_path: Path
        :param len_filter: Number of lines to return.
        :type len_filter: int
        :param strip: Decides whether lines will get stripped or not.
        :type strip: bool
        :rtype: list
        """
        try:
            with open(log_path.absolute(), "r+") as log_file:
                # strip deletes new line feeds, and filter deletes empty lines from list
                log_lines = list(filter(None, [line.strip() if strip else line for line in log_file.readlines()]))
            if len_filter and type(len_filter) is int:
                log_lines = self.apply_len_filter(log_lines, len_filter)
            return log_lines
        except FileNotFoundError:
            return []

    def read_in_dicts(self, log_path, rex, rex_resource, groups, groups_resource, len_filter):
        """
        Reads file in list of dicts, where each dict represents info of one line in file.

        :param log_path: File to be read.
        :type log_path: Path
        :param rex: Regex to match per line if resource ID was not logged.
        :type rex: str
        :param rex_resource: Regex to match per line if resource ID was logged.
        :type rex_resource: str
        :param groups: Groups in defined in param rex.
        :type groups: list
        :param groups_resource: Groups in defined in param rex_resource.
        :type groups_resource: list
        :param len_filter: Number of lines to return.
        :type len_filter: int
        :rtype: list
        """
        log_lines = self.read_lines(log_path, len_filter, strip=True)
        lines = []
        for line in log_lines:
            match = re.search(rex, line)
            match_resource = re.search(rex_resource, line)
            if match and not match_resource:
                line_dict = {key: '' for key in groups}
                for key in groups:
                    line_dict[key] = match.group(key)
                lines.append(line_dict)
            elif not match and match_resource:
                line_dict = {key: '' for key in groups_resource}
                for key in groups_resource:
                    line_dict[key] = match_resource.group(key)
                lines.append(line_dict)
            else:
                raise ValueError(f"'{log_path}' included unmatchable line: {line}")
        return lines

    def write_to_agent_history(self, agent, other_agent, history_value, resource_id=None):
        log_path = self.log_path / f"{agent}_history.log"
        write_string = f"{BasicLogger.get_current_time()}, history trust on '{other_agent}'" \
                       f"{f' in resource <{resource_id}>' if resource_id else ''}: {history_value}"
        with self.semaphore:
            with open(log_path.absolute(), "a+") as history_file:
                print(write_string, file=history_file)

    def write_bulk_to_agent_history(self, agent, history, resource_id=None):
        log_path = self.log_path / f"{agent}_history.log"
        with self.semaphore:
            with open(log_path.absolute(), "a+") as history_file:
                if type(history) == list:
                    for entry in history:
                        other_agent, resource_id, history_value = entry[0], entry[1], entry[2]
                        write_string = f"{BasicLogger.get_current_time()}, history trust on '{other_agent}'" \
                                       f"{f' in resource <{resource_id}>' if resource_id else ''}: {history_value}"
                        print(write_string, file=history_file)
                elif type(history) == dict:
                    for other_agent, history_value in history.items():
                        write_string = f"{BasicLogger.get_current_time()}, history trust on '{other_agent}'" \
                                       f"{f' in resource <{resource_id}>' if resource_id else ''}: {history_value}"
                        print(write_string, file=history_file)
                else:
                    raise TypeError("Unexpected type for History object")

    def write_to_agent_topic_trust(self, agent, other_agent, topic, topic_value, resource_id=None):
        log_path = self.log_path / f"{agent}_topic.log"
        write_string = f"{BasicLogger.get_current_time()}, topic trust on '{other_agent}'" \
                       f"{f' in resource <{resource_id}>' if resource_id else ''} regarding '{topic}': {topic_value}"
        with self.semaphore:
            with open(log_path.absolute(), "a+") as topic_file:
                print(write_string, file=topic_file)

    def write_bulk_to_agent_topic_trust(self, agent, topic_trust, resource_id=None):
        log_path = self.log_path / f"{agent}_topic.log"
        with self.semaphore:
            with open(log_path.absolute(), "a+") as topic_file:
                for other_agent, topic_dict in topic_trust.items():
                    if topic_dict:
                        for topic, topic_value in topic_dict.items():
                            write_string = f"{BasicLogger.get_current_time()}, topic trust on '{other_agent}'" \
                                           f"{f' in resource <{resource_id}>' if resource_id else ''}" \
                                           f" regarding '{topic}': {topic_value}"
                            print(write_string, file=topic_file)

    def write_to_agent_message_log(self, observation):
        log_path = self.log_path / f"{observation.receiver}.log"
        write_string = f"{BasicLogger.get_current_time()}, '{observation.receiver}' received from " \
                       f"'{observation.sender}' with observation id '{observation.observation_id}' " \
                       f"the message: {observation.message}"
        with self.semaphore:
            with open(log_path.absolute(), "a+") as agent_log:
                print(write_string, file=agent_log)

    def write_to_trust_log(self, agent, other_agent, trust_value, resource_id=None):
        log_path = self.log_path / "trust_log.log"
        write_string = f"{BasicLogger.get_current_time()}, '{agent}' trusts '{other_agent}'" \
                       f"{f' in resource <{resource_id}>' if resource_id else ''}: {trust_value}"
        with self.semaphore:
            with open(log_path.absolute(), 'a+') as trust_log:
                print(write_string, file=trust_log)

    def write_to_agent_trust_log(self, agent, metric_str, other_agent, trust_value, resource_id=None):
        log_path = self.log_path / f"{agent}_trust_log.log"
        write_string = f"{BasicLogger.get_current_time()}, '{metric_str}' trust value for '{other_agent}'" \
                       f"{f' in resource <{resource_id}>' if resource_id else ''}: {trust_value}"
        with self.semaphore:
            with open(log_path.absolute(), "a+") as trust_log:
                print(write_string,  file=trust_log)

    def __init__(self, scenario_run_id, semaphore):
        super().__init__(scenario_run_id, semaphore)
        split_index = len(scenario_run_id.split("_")[0]) + 1  # index to cut constant of runId -> 'scenarioRun_'
        self.folder_name = scenario_run_id[split_index:]
        self.log_path = Path(f"{LOG_PATH}/{self.folder_name}/")
        if not self.log_path.is_dir():
            os.mkdir(self.log_path.absolute())

