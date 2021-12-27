




class Server:
    def __init__(self):







        self.magic_cookie = 0xabcddcba
        self.offer_message_type = 0x2











    def waiting_for_clients(self):
        while not self.server_found:
            print("Client started, listening for offer requests...")

    def hame_mode(self):
        print("Received offer from 172.1.0.4, attempting to connect...")