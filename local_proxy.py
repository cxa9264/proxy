import socket
import sys
import os
import multiprocessing

class LocalProxy:

    def __init__(self, port):
        self.port = port
        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind socket
        self.proxy.bind((socket.gethostname(), self.port))
        self.proxy.listen(5)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.proxy.close()

    def receive_single(self):
        print("Proxy waiting for connection...")
        client, addr = self.proxy.accept()
        print("Proxy connected!")

        message = ""
        while True:
            buffer = client.recv(1024)

        print("Message received:", message.decode('utf-8'))

            





            