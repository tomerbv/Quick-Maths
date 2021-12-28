import select
import socket
import time
from random import randint
from threading import Thread, Event


class Server:
    def __init__(self, tcp_port):
        """
        in the constructor for the Server we a UDP and TCP socket to connect to clients. this server can only be connected to two clients for the game.

        :param tcp_port: the servers TCP port given to us
        """
        self.CRED = '\033[91m'
        self.CGREEN = '\033[32m'
        self.YELLOW = '\033[33m'
        self.BLUE = '\033[34m'
        self.CBLINK = '\33[5m'
        self.CREDBG = '\33[41m'
        self.CGREENBG = '\33[42m'
        self.CYELLOWBG = '\33[43m'
        self.CBLUEBG = '\33[44m'
        self.CEND = '\033[0m'



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
        """
        we broadcast offer messages from our UDP socket untill we have to TCP connections
        """
        while not self.players_ready():
            self.udp_socket.sendto(self.msg, ('255.255.255.255', self.looking_port))
            time.sleep(1)


    def players_ready(self):
        """

        :return: true if we have 2 connections to clients
        """
        return self.client1 is not None and self.client2 is not None

    def waiting_for_clients(self):
        """
        in this state  we start listening on the servers TCP socket, the UDP socket will send broadcast offers and find clients that will connect to our Tcp SOCKET that will open a socket for each client(as learned in the course)
        after connection the clients will send the Server their team names, then we are read to start the game
        """
        print(self.BLUE + "Server started, listening on IP address " + self.ip + self.CEND)
        self.tcp_socket.listen()
        broad = Thread(target=self.broadcast)
        broad.start()
        self.tcp_socket.listen(2)
        while not self.players_ready():
            if self.client1 is None:
                try:

                    self.client1, address = self.tcp_socket.accept()
                    self.client1_name = self.client1.recv(1024).decode('UTF-8')

                except:

                    self.client1=None

            elif self.client2 is None:
                try:

                    self.client2, address = self.tcp_socket.accept()
                    self.client2_name = self.client2.recv(1024).decode('UTF-8')

                except:

                    self.client2 = None






        broad.join()




    def wait_for_answer(self, reset_event, client, res, times, i):
        """

        :param reset_event:
        :param client:
        :param res:
        :param times:
        :param i:
        """
        current = time.time()
        limit = current + 10
        client.setblocking(0)
        while not reset_event.is_set():
            try:
                res[i] = client.recv(1024).decode('UTF-8')
            except socket.error as msg:
                if msg.errno==10054:
                    raise Exception("client disconnected at the start of the game")
                else:
                    pass




            if time.time() > limit:
                reset_event.set()
            if res[i] != 767:
                times[i] = time.time() - current
                reset_event.set()


    def game_mode(self):
        """
        we start the game and send the clients the question, the we create a Thread for each client
        :return:
        """
        num1 = randint(0,9)
        num2 = randint(0,9 - num1)
        res = num1 + num2
        msg = self.BLUE + "Welcome to Quick Maths.\n" \
            f"Player 1: {self.client1_name} \n" \
            f"Player 2: {self.client2_name} \n==\n" \
            "Please answer the following question as fast as you can:\n" \
            f"How much is {num1} + {num2}?" + self.CEND
        try:

            self.client1.send(bytes(msg, 'UTF-8'))
            self.client2.send(bytes(msg, 'UTF-8'))
        except:
            raise Exception(self.CRED + "could not send to players the welcome message" + self.CEND)


        results = [767, 767]
        times = [10, 10]
        reset_event = Event()

        t1 = Thread(target=self.wait_for_answer, args=[reset_event, self.client1, results, times, 0])
        t2 = Thread(target=self.wait_for_answer, args=[reset_event, self.client2, results, times, 1])
        t1.start()
        t2.start()

        while not reset_event.is_set():
            time.sleep(0.2)

        end_msg = self.BLUE + f"Game over!\nThe correct answer was {res}!\n"

        if(results[0] == 767 and results[1] == 767):
            return end_msg + "Both of you are losers, next time don't sleep on your keyboard"

        elif(times[0] < times[1]):
            if(results[0] == res):
                return end_msg + f"Congratulations to the winner: {self.client1_name}" + self.CEND
            else:
                return  end_msg + f"Congratulations to the winner: {self.client2_name}" + self.CEND

        elif (times[0] > times[1]):
            if(results[1] == res):
                return  end_msg + f"Congratulations to the winner: {self.client2_name}" + self.CEND
            else:
                return  end_msg + f"Congratulations to the winner: {self.client1_name}" + self.CEND


    def start(self):
        while True:

            self.waiting_for_clients()
            print(self.BLUE + f"Received offer from {self.client1_name} and {self.client2_name}, attempting to connect..."+ self.CEND)
            # TODO: change to 10 seconds, game starts 10 seconds after both players have connected.
            time.sleep(3)
            try:

                summary = self.game_mode()
                self.client1.send(bytes(summary, 'UTF-8'))
                self.client2.send(bytes(summary, 'UTF-8'))
                self.tcp_socket.close()
                print(self.BLUE + "Game over, sending out offer requests..." + self.CEND)

            except:
                print(self.CRED + "the game has been interupted due to one of the clients disconnectiong" + self.CEND )
                print(self.CRED + "Game over, sending out offer requests..." + self.CEND)
            self.__init__(self.tcp_port)

if __name__ == "__main__":
    server = Server(11111)
    server.start()