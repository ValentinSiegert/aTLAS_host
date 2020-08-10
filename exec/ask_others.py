import socket


def ask_other_agent(remote_ip, remote_port, message):
    request_message = f"aTLAS_trust_protocol::{message}"
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client.connect((remote_ip, remote_port))
    # send message
    tcp_client.send(bytes(request_message, 'UTF-8'))
    receive_data = tcp_client.recv(2048)
    receive_data = receive_data.decode('utf-8')
    tcp_client.close()
    received_value = float(receive_data.split("::")[2])
    return received_value

