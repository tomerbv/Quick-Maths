import msvcrt
import socket
import time


class Client:

    def __init__(self):
        """
        in the constructor we initiate the Client class with the Udp port of 13117(given to us) and a TCP socket to connect to the Servers Tcp socket after
        it will be given to us

        """
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
        """
        this is the looking for server state:
        in this function we are looking for a UDP brodacast.
        after we find one we break the first part of the message to three parts: Message_cookie = we check that is it is the message right message cookie : 0xabcddcba
                                                                                 offer_message_type = we check that is it is the right message type : 0x2
                                                                                 tcp_port : this will be the port the Clients tcp socket will connect to from the Servers side
        the second part of the message is the ip of the socket to connect to
        """
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
        """
        this is the connecting to server state
        we try to establish a connection with the TCP socket of the server. if it is established we send the server our team name.
        then we receive a message from the server that welcomes us to the game and ask us the math question
        :return: True if no problems occured
                 Fales if a problem occured
        """
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
        """
        this is the game mode state
        in this situation
        :return:
        """
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
