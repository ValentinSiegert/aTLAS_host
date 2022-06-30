from abc import ABC, abstractmethod
import multiprocessing as multiproc


class BasicConnector(ABC, multiproc.Process):
    @abstractmethod
    def register_at_director(self):
        pass

    @abstractmethod
    def set_max_agents(self):
        pass

    @abstractmethod
    def run(self):
        pass

    def __init__(self, director_hostname, max_agents, send_queue, pipe_dict, sec_conn, supervisor_info=None):
        multiproc.Process.__init__(self)
        self.director_hostname = director_hostname
        self.max_agents = max_agents
        self.send_queue = send_queue
        self.pipe_dict = pipe_dict
        self.sec_conn = sec_conn
        self.supervisor_info = supervisor_info
