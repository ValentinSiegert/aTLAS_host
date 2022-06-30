import socket
from threading import Thread, Event

from .agent_server_thread import ServerThread


class AgentServer(Thread):
    def run(self):
        self.tcp_server.bind((self.ip_address, self.port))
        print(f"Agent '{self.agent}' listens on {self.ip_address}:{self.port}")
        while not self._stop_event.is_set():
            self.tcp_server.listen(4)
            (conn, (ip, port)) = self.tcp_server.accept()
            # print(f"Connection established with: {ip}:{port}")
            new_thread = ServerThread(conn, ip, port, self.agent, self.agent_behavior, self.scale, self.logger,
                                      self.observations_done, self.discovery)
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
        close_sock.shutdown(socket.SHUT_RDWR)
        # close_sock.close()
        socket.close(close_sock.fileno())

    def set_discovery(self, discovery):
        self.discovery = discovery

    def __init__(self, agent, ip_address, port, agent_behavior, scale, logger,
                 observations_done):
        Thread.__init__(self)
        self.agent = agent
        self.ip_address = ip_address
        self.port = port
        self.threads = []
        self.logger = logger
        self.agent_behavior = agent_behavior
        self.scale = scale
        self.observations_done = observations_done
        self._stop_event = Event()
        self.discovery = {}
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def __del__(self):
        # print("Closing server socket:", self.sock)
        self.tcp_server.shutdown(socket.SHUT_RDWR)
        # self.tcp_server.close()
        socket.close(self.tcp_server.fileno())

