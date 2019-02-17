import socket

port = 7777

server_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_s.bind(('', port))
print('Start\n')
message, address = server_s.recvfrom(1024)
print('message:\n{}'.format(message))
print('Stop')
