import msvcrt
import socket
import time


class Client:
    def __init__(self):
        self.looking_port = 13117

        self.server_found = False;
        self.tcp_port = None
        self.ip = None

        self.name = "TomOmer"

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(('', self.looking_port))

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.magic_cookie = 0xabcddcba
        self.offer_message_type = 0x2

    def looking_for_server(self):
        while True:

            verifaction_tcp, adress = self.udp_socket.recvfrom(1024)
            recieved_cookie = hex(int(verifaction_tcp.hex()[:8], 16))
            recieved_type = verifaction_tcp.hex()[9:10]
            recieved_port = verifaction_tcp.hex()[10:]

            if (recieved_cookie == hex(self.magic_cookie) and int(recieved_type) == self.offer_message_type):
                self.tcp_port = int(recieved_port, 16)
                self.ip = adress[0]
                print("Recieved offer from " + str(self.ip) + ", attempting to connect...\n")
                break

    def connecting_to_server(self):
        try:
            self.tcp_socket.connect((self.ip, self.tcp_port))
        except:
            print("Couldn't connect to server, listening for offer requests...")
            return False
        team_msg = bytes(self.name, 'UTF-8')
        try:
            self.tcp_socket.send(team_msg)
            welcome = self.tcp_socket.recv(1024)
            print(welcome.decode('UTF-8'))
            return True
        except:
            print("Couldn't connect to server, listening for offer requests...")
            return False

    def game_mode(self):
        current = time.time()
        self.tcp_socket.setblocking(0)
        msg = None
        while not msvcrt.kbhit():
            msg = self.expect_message()
            if msg:
                break
            #timeout in case the server has disconnected
            if current + 11 <= time.time():
                raise Exception("Server disconnected")

        if not msg:
            char = msvcrt.getch()
            self.tcp_socket.send(char)
            while not msg:
                msg = self.expect_message()
                if current + 11 <= time.time():
                    raise Exception("Server disconnected")
        return msg


    def expect_message(self):
        msg = None
        try:
            msg = self.tcp_socket.recv(1024)
        except:
            time.sleep(0.1)
        return msg

    def disconnected(self):
        print("Disconnected from server, listening for offer requests...")

    def start(self):
        print("Client started, listening for offer requests...")
        while True:
            self.looking_for_server()
            if self.connecting_to_server():
                try:
                    msg = self.game_mode()
                except:
                    print("Server disconnected duo to error, listening for offer requests...")
                else:
                    print(msg.decode('UTF-8'))
                    print("Server disconnected, listening for offer requests...")

            self.__init__()



if __name__ == "__main__":
    client = Client()
    client.start()
