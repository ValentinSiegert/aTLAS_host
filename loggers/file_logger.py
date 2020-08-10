from pathlib import Path
import os
from loggers.basic_logger import BasicLogger


class FileLogger(BasicLogger):
    LOG_PATH = Path("log/")
    if not LOG_PATH.is_dir():
        os.mkdir(LOG_PATH.absolute())

    def readlines_from_agent_history(self, agent, len_filter=None):
        log_path = self.log_path / f"{agent}_history.txt"
        with open(log_path.absolute(), "r+") as history_file:
            history_lines = history_file.readlines()
            # TODO implement len_filter change on history_lines
        return history_lines

    def readlines_from_agent_trust_log(self, agent, len_filter=None):
        log_path = self.log_path / f"{agent}_trust_log.txt"
        with open(log_path.absolute(), "r+") as trust_log_file:
            trust_log_lines = trust_log_file.readlines()
            # TODO implement len_filter change on trust_log_lines
        return trust_log_lines

    def readlines_from_agent_topic_trust(self, agent, len_filter=None):
        log_path = self.log_path / f"{agent}_topic.txt"
        with open(log_path.absolute(), "r+") as topic_file:
            topic_lines = topic_file.readlines()
            # TODO implement len_filter change on topic_lines
        return topic_lines

    def readlines_from_trust_log(self, len_filter=None):
        log_path = self.log_path / f"trust_log.txt"
        with open(log_path.absolute(), "r+") as log_file:
            log_lines = log_file.readlines()
            # TODO implement len_filter change on log_lines
        return log_lines

    def write_to_agent_history(self, agent, other_agent, history_value):
        log_path = self.log_path / f"{agent}_history.txt"
        with self.semaphore:
            with open(log_path.absolute(), "a+") as history_file:
                print(f"{BasicLogger.get_current_time()}, history trust value from: '{other_agent}': {history_value}",
                      file=history_file)

    def write_bulk_to_agent_history(self, agent, history):
        log_path = self.log_path / f"{agent}_history.txt"
        with self.semaphore:
            with open(log_path.absolute(), "a+") as history_file:
                for other_agent, history_value in history.items():
                    print(f"{BasicLogger.get_current_time()}, history trust value from '{other_agent}': {history_value}"
                          , file=history_file)

    def write_to_agent_topic_trust(self, agent, other_agent, topic, topic_value):
        log_path = self.log_path / f"{agent}_topic.txt"
        with self.semaphore:
            with open(log_path.absolute(), "a+") as topic_file:
                print(f"{BasicLogger.get_current_time()}, topic trust value from '{other_agent}' regarding '{topic}': "
                      f"{topic_value}", file=topic_file)

    def write_bulk_to_agent_topic_trust(self, agent, topic_trust):
        log_path = self.log_path / f"{agent}_topic.txt"
        with self.semaphore:
            with open(log_path.absolute(), "a+") as topic_file:
                for other_agent, topic_dict in topic_trust.items():
                    if topic_dict:
                        for topic, topic_value in topic_dict.items():
                            print(f"{BasicLogger.get_current_time()}, topic trust value from '{other_agent}' regarding "
                                  f"'{topic}': {topic_value}", file=topic_file)

    def write_to_agent_message_log(self, observation):
        log_path = self.log_path / f"{observation.receiver}.txt"
        write_string = f"{BasicLogger.get_current_time()}, '{observation.receiver}' received from " \
                       f"'{observation.sender}' from author '{observation.author}' with topic '{observation.topic}' " \
                       f"the message: {observation.message}"
        with self.semaphore:
            with open(log_path.absolute(), "a+") as agent_log:
                print(write_string, file=agent_log)

    def write_to_trust_log(self, agent, other_agent, trust_value):
        log_path = self.log_path / "trust_log.txt"
        write_string = f"{BasicLogger.get_current_time()}, '{agent}' trusts '{other_agent}' with value: {trust_value}"
        with self.semaphore:
            with open(log_path.absolute(), 'a+') as trust_log:
                print(write_string, file=trust_log)

    def write_to_agent_trust_log(self, agent, metric_str, other_agent, trust_value):
        log_path = self.log_path / f"{agent}_trust_log.txt"
        write_string = f"{BasicLogger.get_current_time()}, {metric_str} trust value from '{other_agent}': {trust_value}"
        with self.semaphore:
            with open(log_path.absolute(), "a+") as trust_log:
                print(write_string,  file=trust_log)

    def __init__(self, scenario_run_id, semaphore):
        super().__init__(scenario_run_id, semaphore)
        split_index = len(scenario_run_id.split("_")[0]) + 1  # index to cut constant of runId -> 'scenarioRun_'
        self.folder_name = scenario_run_id[split_index:]
        self.log_path = Path("log/" + self.folder_name + "/")
        if not self.log_path.is_dir():
            os.mkdir(self.log_path.absolute())

