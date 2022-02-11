import socket
from config import BUFFER_SIZE


def ask_other_agent(remote_ip, remote_port, message):
    """
    Connects via TCP socket to other agent, sends message and return response.

    :param remote_ip: IP address of other agent.
    :type remote_ip: str
    :param remote_port: TCP port of other agent.
    :type remote_port: int
    :param message: Message to send to other agent.
    :type message: str
    :return: Response of other agent.
    :rtype: str
    """

    request_message = f"aTLAS_trust_protocol::{message}"
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client.connect((remote_ip, remote_port))
    # send message
    tcp_client.send(bytes(request_message, 'UTF-8'))
    receive_data = tcp_client.recv(BUFFER_SIZE)
    receive_data = receive_data.decode('utf-8')
    tcp_client.close()
    return receive_data.split("::")[2]

