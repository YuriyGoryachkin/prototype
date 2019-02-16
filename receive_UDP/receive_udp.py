import socketserver

class Receiver:

    def receive(self, data):
        print(data)

class MyUDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request
        mess.receive(data)

        # print("{} wrote:".format(self.client_address[0]))
        # print(data)


if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 7777
    mess = Receiver()
    with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
        print('[UDP_receiver]: start')
        server.serve_forever()
