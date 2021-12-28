import msvcrt
import socket
import time
import os

# System call
os.system("")

class Client:

    def __init__(self):
        """
        in the constructor we initiate the Client class with the Udp port of 13117(given to us) and a TCP socket to connect to the Servers Tcp socket after
        it will be given to us

        """
        self.CRED = '\033[91m'
        self.CGREEN = '\033[32m'
        self.YELLOW = '\033[33m'
        self.BLUE = '\033[34m'
        self.CBLINK ='\33[5m'
        self.CREDBG    = '\33[41m'
        self.CGREENBG  = '\33[42m'
        self.CYELLOWBG = '\33[43m'
        self.CBLUEBG   = '\33[44m'
        self.CEND = '\033[0m'



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
                print(self.BLUE +"Recieved offer from " + str(self.ip) + ", attempting to connect...\n" + self.CEND)
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
            print(self.CRED + "Couldn't connect to server, listening for offer requests..."+ self.CEND)
            return False
        team_msg = bytes(self.name, 'UTF-8')
        try:
            self.tcp_socket.send(team_msg)
            welcome = self.tcp_socket.recv(1024)
            print(welcome.decode('UTF-8'))
            return True
        except:
            print(self.CRED + "Couldn't connect to server, listening for offer requests..." + self.CEND )
            return False

    def game_mode(self):
        """
        this is the game mode state
        in this situation we can either recieve the a summary message if the other player already typed a solution before us or we recieved a message after we typed in a solution
        we check both situations and handle them, first we check if we entered a key , if we havent and 10 seconds passed, this means there was a problem with the server because of the
        format we know.
        if we have pressed a key and then we send this to the server and if we dont get an answer in 10 secconds we know there is a problem with a server because of the format
        :return: the message
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
        """
        function to try to recieve the message from the server
        :return:
        """
        msg = None
        try:
            msg = self.tcp_socket.recv(1024)
        except:
            time.sleep(0.1)
        return msg



    def start(self):
        """
        this function puts everything together
        first we look for a server to connect to , if we found one and the connection was established we play the game,if there was any problem during the game we just print the the disconnection and
        we re-inialize our class and look for a server again.

        """
        print(self.BLUE + "Client started, listening for offer requests..." + self.CEND)
        while True:
            self.looking_for_server()
            if self.connecting_to_server():
                try:
                    msg = self.game_mode()
                except:
                    print(self.CRED + "Server disconnected duo to error, listening for offer requests..." + + self.CEND)
                else:
                    print(self.BLUE + msg.decode('UTF-8') + self.CEND)
                    print(self.BLUE + "Server disconnected, listening for offer requests..." + self.CEND)

            self.__init__()



if __name__ == "__main__":
    client = Client()
    client.start()
