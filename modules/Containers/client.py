import pickle
import socket
import argparse


def send_request(data, ip='examinelab_tests_1', port=12345, buffer_size=8192):
    with socket.socket() as s:
        s.connect((ip, port))
        
        data = pickle.dumps(data)
        s.send(data)

        response = s.recv(buffer_size)
        response = pickle.loads(response)

        return response
