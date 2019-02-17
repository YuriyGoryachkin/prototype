import socket

port = 7777

server_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_s.bind(('192.168.0.115', port))
print('Start\n')
message, address = server_s.recvfrom(4096)
print('message:\n{}'.format(message))
print('Stop')
