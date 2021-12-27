import socket


class Client:
    def __init__(self):
        self.looking_port = 13117

        self.server_found = False;
        self.tcp_port=None
        self.ip=None

        self.name = "TomOmer"

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.udp_socket.bind(('', self.looking_port))

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.magic_cookie = 0xabcddcba
        self.offer_message_type = 0x2

    def looking_for_server(self):
        while not self.server_found:

            print("Client started, listening for offer requests...")
            verifaction_tcp,adress = self.udp_socket.recv('UTF-8')
            recieved_cookie = hex(int(verifaction_tcp.hex()[:8],16))
            recieved_type=verifaction_tcp.hex()[10:]
            recieved_port = verifaction_tcp.hex()[10:]
            if(recieved_cookie==hex(self.magic_cookie) and int(recieved_type)==self.offer_message_type):
                self.tcp_port=int(recieved_port,16)
                self.ip=adress[0]
            print("Recieved offer from " + str(self.ip) + ", attempting to connect...\n")
            self.server_found=True



    def connecting_to_server(self):
        print("Recieved offer from " + str(self.ip) + ", attempting to connect...to my tcp port" + str(self.tcp_port + '\n'))

        self.tcp_socket.connect((self.ip,self.tcp_port))
        team_msg=bytes(self.name,'UTF-8')
        self.tcp_socket.send((team_msg))

    def game_mode(self):
        return


    def start(self):
        self.looking_for_server()
        self.connecting_to_server()

if __name__ == "__main__":
    while True:
      client = Client()
      client.start()





