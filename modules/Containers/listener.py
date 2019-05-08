import socket
import sys
import pickle
import argparse
import logging

sys.path.append('../')
from modules.Tests import testReciever


def start_listening(ip, port, buffer_size=8192):
    logging.basicConfig(level=logging.INFO)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ip, port))
        s.listen(1)
        logging.info(f'Start listening to {ip}:{port}')

        while True:
            client, _ = s.accept()
            while True:
                data = client.recv(buffer_size)
                if not data: 
                    break
                if sys.getsizeof(data) == buffer_size - 40:
                    logging.error('Buffer overflow!')
                    break
                data = pickle.loads(data)
                logging.info(f'Recived data: {data}, {type(data)}, {sys.getsizeof(data)} bytes')
                passed, outs = testReciever.perform_testing_from_text(data['user_code'], data['tests'], data['language'], test_preproc = lambda t: t.replace('\n',''), user_preproc = lambda t: t.replace('\n',''))
                response = passed, outs
                response = pickle.dumps(response)
                client.send(response)
                logging.info(f'Sended data: {response}, {type(response)}, {sys.getsizeof(response)} bytes')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', required=True,
                        help='IP adress listen to')
    parser.add_argument('-p', '--port', required=True,
                        help='Port listen to')
    parser.add_argument('-bs', '--buffer_size', default=8192,
                        help='Buffer size of recived data')
                            
    args = parser.parse_args()
    start_listening(args.ip, int(args.port), int(args.buffer_size))
