import socket
import time
from threading import Thread


class Server:
    def __init__(self, tcp_port):
        self.looking_port = 13117
        self.tcp_port = tcp_port

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.ip = socket.gethostbyname(socket.gethostname())
        self.msg = 0xabcddcba.to_bytes(byteorder='big', length=4) + 0x2.to_bytes(byteorder='big', length=1) + tcp_port.to_bytes(byteorder='big', length=2)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind(("" , tcp_port))

        self.client1 = None
        self.client1_name = None
        self.client2 = None
        self.client2_name = None

    def broadcast(self):
        while not self.players_ready():
            self.udp_socket.sendto(self.msg, ('255.255.255.255', self.looking_port))
            time.sleep(1)

    def players_ready(self):
        return self.client1 is not None and self.client2 is not None

    def waiting_for_clients(self):
        print("Server started, listening on IP address " + self.ip)
        self.tcp_socket.listen()
        broad = Thread(target=self.broadcast)
        broad.start()
        self.tcp_socket.listen(2)
        while not self.players_ready():
            if self.client1 is None:
                self.client1, address = self.tcp_socket.accept()
                self.client1_name = self.client1.recv(1024).decode('UTF-8')
                print("connected 1")

            elif self.client2 is None:
                self.client2, address = self.tcp_socket.accept()
                self.client2_name = self.client2.recv(1024).decode('UTF-8')
                print("connected 2")

        broad.join()





    def game_mode(self):
        self.client1.send(bytes("hello client", 'UTF-8'))
        self.client2.send(bytes("hello client", 'UTF-8'))
        ans1 = self.client1.recv(1024)
        ans2 = self.client2.recv(1024)
        print(ans1.decode('UTF-8'))
        print(ans2.decode('UTF-8'))
        self.tcp_socket.close()


    def start(self):
        self.waiting_for_clients()
        print(f"Received offer from {self.client1_name} and {self.client2_name}, attempting to connect...")
        summary = self.game_mode()
        print("done")

while True:
    server = Server(18121)
    server.start()