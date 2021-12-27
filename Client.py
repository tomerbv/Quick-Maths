import socket


class Client:
    def __init__(self):
        self.looking_port = 13117

        self.server_found = False;

        self.name = "TomOmer"

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.udp_socket.bind(('', self.looking_port))

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.magic_cookie = 0xabcddcba
        self.offer_message_type = 0x2

    def looking_for_server(self):
        while not self.server_found:

            msg = self.udp_socket.recv("utf-8")


    def connecting_to_server(self):
        print("Received offer from , attempting to connect...")

    def game_mode(self):
        return





