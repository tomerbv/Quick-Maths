import select
import socket
import time
from random import randint
from threading import Thread, Event


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





        print("2 players are ready, tcp server closed until end of game")
        broad.join()




    def wait_for_answer(self, reset_event, client, res, times, i):
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
        num1 = randint(0,9)
        num2 = randint(0,9 - num1)
        res = num1 + num2
        msg = "Welcome to Quick Maths.\n" \
            f"Player 1: {self.client1_name} \n" \
            f"Player 2: {self.client2_name} \n==\n" \
            "Please answer the following question as fast as you can:\n" \
            f"How much is {num1} + {num2}?"
        try:

            self.client1.send(bytes(msg, 'UTF-8'))
            self.client2.send(bytes(msg, 'UTF-8'))
        except:
            raise Exception("could not send to players the welcome message")


        results = [767, 767]
        times = [10, 10]
        reset_event = Event()

        t1 = Thread(target=self.wait_for_answer, args=[reset_event, self.client1, results, times, 0])
        t2 = Thread(target=self.wait_for_answer, args=[reset_event, self.client2, results, times, 1])
        t1.start()
        t2.start()

        while not reset_event.is_set():
            time.sleep(0.2)

        end_msg = f"Game over!\nThe correct answer was {res}!\n"

        if(results[0] == 767 and results[1] == 767):
            return end_msg + "Both of you are losers, next time don't sleep on your keyboard"

        elif(times[0] < times[1]):
            if(results[0] == res):
                return end_msg + f"Congratulations to the winner: {self.client1_name}"
            else:
                return end_msg + f"Congratulations to the winner: {self.client2_name}"

        elif (times[0] > times[1]):
            if(results[1] == res):
                return end_msg + f"Congratulations to the winner: {self.client2_name}"
            else:
                return end_msg + f"Congratulations to the winner: {self.client1_name}"


    def start(self):
        while True:

            self.waiting_for_clients()
            print(f"Received offer from {self.client1_name} and {self.client2_name}, attempting to connect...")
            # TODO: change to 10 seconds, game starts 10 seconds after both players have connected.
            time.sleep(3)
            try:

                summary = self.game_mode()
                self.client1.send(bytes(summary, 'UTF-8'))
                self.client2.send(bytes(summary, 'UTF-8'))
                self.tcp_socket.close()
                print("Game over, sending out offer requests...")

            except:
                print("the game has been interupted due to one of the clients disconnectiong")
                print("Game over, sending out offer requests...")
            self.__init__(self.tcp_port)

if __name__ == "__main__":
    server = Server(11111)
    server.start()