import socket
from threading import Thread


class AgentClient(Thread):
    def run(self):
        buffer_size = 2048
        tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_client.connect((self.remote_ip, self.remote_port))
        # send message
        tcp_client.send(bytes(self.message, 'UTF-8'))
        receive_data = tcp_client.recv(buffer_size)
        # print("data sent at :"  + time.ctime(time.time()))
        receive_data = receive_data.decode('utf-8')
        print(receive_data)
        tcp_client.close()

    def __init__(self, remote_ip, remote_port, message):
        Thread.__init__(self)
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.message = message




