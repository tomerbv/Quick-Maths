from threading import Thread

from Client import Client
from Server import Server

if __name__ == "__main__":
    server = Server(18121)
    t1 = Thread(target=server.start_server, daemon=True)
    t1.start()

    client1 = Client()
    client2 = Client()

    tClient1 = Thread(target=client1.start_client, daemon=True)
    tClient2 = Thread(target=client2.start_client, daemon=True)
    # tClient3 = Thread(target=client3.start_client, daemon=True)

    tClient1.start()
    tClient2.start()

    t1.join()