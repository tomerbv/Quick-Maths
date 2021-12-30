import os
import socket
import time
from random import randint
from threading import Thread, Event
import scapy.all as scapy
import platform
import struct

class Server:
    time_record = None

    def __init__(self, tcp_port, test_network=False):
        """
        in the constructor for the Server we a UDP and TCP socket to connect to clients. this server can only be connected to two clients for the game.

        :param tcp_port: the servers TCP port given to us
        """
        self.CRED = '\033[91m'
        self.GREEN = '\033[32m'
        self.YELLOW = '\033[33m'
        self.BLUE = '\033[34m'
        self.CBLINK = '\33[5m'
        self.CREDBG = '\33[41m'
        self.CGREENBG = '\33[42m'
        self.CYELLOWBG = '\33[43m'
        self.CBLUEBG = '\33[44m'
        self.CEND = '\033[0m'

        if platform.system() == 'Linux':
            if test_network:
                self.network = scapy.get_if_addr('eth2')
            else:
                self.network = scapy.get_if_addr('eth1')
        else:
            self.network = ''
        self.looking_port = 13117
        self.tcp_port = tcp_port

        self.address = ".".join(self.network.split('.')[:2]) + '.255.255'
        print(self.address)

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.ip = socket.gethostbyname(socket.gethostname())
        self.msg = struct.pack("IbH",0xabcddcba,0x2,self.tcp_port)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((self.ip, tcp_port))

        self.client1 = None
        self.client1_name = None
        self.client2 = None
        self.client2_name = None


    def broadcast(self):
        """
        we broadcast offer messages from our UDP socket until we have two TCP connections
        """


        while not self.players_ready():
            # TODO: change network ip
            # self.network
            self.udp_socket.sendto(self.msg, (self.address, self.looking_port))
            time.sleep(1)

    def players_ready(self):
        """
        :return: true if we have 2 connections and two clients
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
                    self.client1 = None

            elif self.client2 is None:
                try:
                    self.client2, address = self.tcp_socket.accept()
                    self.client2_name = self.client2.recv(1024).decode('UTF-8')
                except:
                    self.client2 = None

        broad.join()

    def wait_for_answer(self, reset_event, client, res, times, i):
        """
        :param reset_event: an Event instance that acts as the communication between the different threads
        :param client: the specific client for which the tread waits for an answer
        :param res: an array of results that the results are kept on by each thread
        :param times: an array of time measurements that the time is kept on by each thread
        :param i: the index of the client to access the arrays above
        """
        current = time.time()
        limit = current + 10
        client.setblocking(0)
        while not reset_event.is_set():
            try:
                res[i] = client.recv(1024).decode('UTF-8')
            except socket.error as msg:
                pass

            if time.time() > limit:
                reset_event.set()
            if res[i] != 767:
                times[i] = time.time() - current
                reset_event.set()

    def game_mode(self):
        """
        the game contains 3 stages:
        1. randomizing the question parameters and forming the text that will be sent to each client accordingly
        2. creating two threads to listen to each client by using wait_for_answer method, once both threads are
         finished duo to a received answer by one of the clients (that will terminate the other's thread as well)
         or duo to a timeout, the game wil proceed to the third part
        3. the game will decide the winner (or draw in case of a timeout) then it will construct a message accordingly
        :return: the constructed game result message
        """
        num1 = randint(0, 9)
        num2 = randint(0, 9 - num1)
        res = str(num1 + num2)
        msg = f"{self.BLUE}Welcome to Quick Maths.{self.CEND}\n" \
              f"{self.GREEN}Player 1: {self.client1_name}{self.CEND}\n" \
              f"{self.YELLOW}Player 2: {self.client2_name}\n{self.CEND}" \
              f"{self.BLUE}==\nPlease answer the following question as fast as you can:\n" \
              f"How much is {num1} + {num2}?{self.CEND}"
        try:
            self.client1.send(bytes(msg, 'UTF-8'))
            self.client2.send(bytes(msg, 'UTF-8'))
        except:
            raise Exception(self.CRED + "could not send to players the welcome message" + self.CEND)

        results = [767, 767]
        times = [10, 10]
        reset_event = Event()
        try:
            t1 = Thread(target=self.wait_for_answer, args=[reset_event, self.client1, results, times, 0])
            t2 = Thread(target=self.wait_for_answer, args=[reset_event, self.client2, results, times, 1])
            t1.start()
            t2.start()
        except:
            pass



        while not reset_event.is_set():
            time.sleep(0.2)

        end_msg = f"{self.CREDBG}Game over!\nThe correct answer was {res}!{self.CEND}\n"

        if (results[0] == 767 and results[1] == 767):
            return end_msg + f"{self.CBLUEBG}Congratulations! both of you are losers, next time don't sleep on your keyboard{self.CEND}"


        elif times[0] < times[1]:
            if results[0] == res:
                end_msg += f"{self.CBLUEBG}Congratulations to the winner: {self.client1_name}{self.CEND}"
                if self.check_time_record(times[0]):
                    end_msg += f"\n{self.YELLOW}Congratulations {self.client1_name} you broke the time record!\nThe record you set is: {self.time_record}{self.CEND}"
                return end_msg
            else:
                return end_msg + f"{self.CBLUEBG}Congratulations to the winner: {self.client2_name}{self.CEND}"

        elif times[0] > times[1]:
            if results[1] == res:
                end_msg += f"{self.CBLUEBG}Congratulations to the winner: {self.client2_name}{self.CEND}"
                if self.check_time_record(times[1]):
                    end_msg += f"\n{self.YELLOW}Congratulations {self.client2_name} you broke the time record!\nThe record you set is: {self.time_record}{self.CEND}"
                return end_msg
            else:
                return end_msg + f"{self.CBLUEBG}Congratulations to the winner: {self.client1_name}{self.CEND}"

    def check_time_record(self, time):
        if not self.time_record:
            self.time_record = time
            return True
        elif time < self.time_record:
            self.time_record = time
            return True
        else:
            return False

    def start(self):
        """
        the servers flow endlessly waits for clients to initiate connection, once a connection is made it proceeds to
        the game itself. when the game is done or an error has occurred the server prints and sends the appropriate
        messages and restarts its own fields.
        """
        while True:

            self.waiting_for_clients()
            print(f"Received offer from {self.client1_name} and {self.client2_name}, attempting to connect...")
            # TODO: change to 10 seconds, game starts 10 seconds after both players have connected.
            time.sleep(0.1)
            try:
                summary = self.game_mode()
                self.client1.send(bytes(summary, 'UTF-8'))
                self.client2.send(bytes(summary, 'UTF-8'))
                self.tcp_socket.close()
                print("Game over, sending out offer requests...")

            except:
                print(self.CRED + "the game has been interrupted due to one of the clients disconnecting" + self.CEND)
                print(self.CRED + "Game over, sending out offer requests..." + self.CEND)
            self.__init__(self.tcp_port)


if __name__ == "__main__":
    server = Server(2031)
    server.start()
