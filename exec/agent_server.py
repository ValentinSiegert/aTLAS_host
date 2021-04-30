import socket
from threading import Thread, Event

from .client_thread import ClientThread


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

