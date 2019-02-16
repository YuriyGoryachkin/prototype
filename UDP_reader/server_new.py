import argparse
from socketserver import *
import sys
import json
import os

from jim_message.jim_message import JIMMessageServer
from log import log_config
from DB.server import ServerStorage
from crypto.sec_mes import Crypto_Message


def create_parser(Default_Port, Default_Host):
    parser_serv = argparse.ArgumentParser(prog='server',
                                          description='сервер', epilog='(C)2018')
    parser_serv.add_argument('-p', '--port', type=int,
                             default=Default_Port, help='порт')
    parser_serv.add_argument('-a', '--host', type=str,
                             default=Default_Host, help='IP-адрес')
    return parser_serv


class TcpServer(ThreadingTCPServer):
    allow_reuse_address = True


class Clients_Base:
    def __init__(self):
        self.client_base = []

    def add_client(self, new_client):
        self.client_base.append(new_client)

    def remove_client(self, del_client):
        self.client_base.remove(del_client)


class JIM_Server:
    """ Класс должен обрабатывать полученные сообщения от клиента и ответы сервера """

    def __init__(self, obj_Server):
        self.protocol = JIMMessageServer()
        self.server = obj_Server
        self.base = Clients_Base()

    @staticmethod
    def __deserialization_msg(data):
        """ Декодирует полученное зашифрованное сообщение """
        dec_cry = Crypto_Message()
        data_dec_cry = dec_cry._decrypt(data)
        return json.loads(data_dec_cry.decode('utf-8'))

    def receive_response(self, client, data):
        """ проверка по action """
        try:
            response = self.__deserialization_msg(data)
            if response.get('action').startswith('presence'):
                log_config.log_server.debug('[Server]: receive_response: '
                                            'response:\n{}'.format(response))
                client.send(self.protocol.good_response())

            elif response.get('action').startswith('authenticate'):
                log_config.log_server.debug('[Server]: receive_response: '
                                            'response:\n{}'.format(response))
                try:
                    user = response['user']['account_name']
                    password = response['user']['password']
                    storage.verification(user, password, client.getpeername()[0])
                    client.send(self.protocol.response_2xx(202))
                    log_config.log_server.debug('[Server]: receive_response: '
                                                'user app base')
                except:
                    client.send(self.protocol.response_4xx(402, 'неправильный логин/пароль'))
                    log_config.log_server.error('[Server]: JIM_Server: receive_response: '
                                                'ERROR: {}{}'.format(client, response))
                self.base.add_client(client)

            elif response.get('action').startswith('msg'):
                user = response['user']
                msg = response['message']
                for s_client in self.base.client_base:
                    try:
                        s_client.send(
                            self.protocol.response_6xx(600, user['account_name'], msg))
                    except:
                        pass

            elif response.get('action').startswith('quit'):
                self.base.remove_client(client)
                log_config.log_server.info('[Server]:'
                                           ' receive_response:'
                                           ' client {}'
                                           ' offline'.format(client))
                user = response['user']
                msg = response['message']
                for s_client in self.base.client_base:
                    try:
                        s_client.send(self.protocol.response_6xx(600,
                                                                 user['account_name'], msg))
                    except:
                        pass
                server.close_request(client)

            else:
                log_config.log_server.info('[Server]:'
                                           ' Сообщение содержит'
                                           ' неверный /response/: {}'.format(response))
        except:
            pass

    def response_500(self):
        for s_client in self.base.client_base:
            try:
                s_client.send(self.protocol.response_5xx(500))
            except:
                pass


class Server(StreamRequestHandler):

    def handle(self):
        while True:
            try:
                self.data = self.request.recv(8192)
            except KeyboardInterrupt as error:
                # handler.response_500()
                log_config.log_server.info('[Server]: handle exit: {}'.format(error))
                os._exit(0)
            except ConnectionResetError as error:
                log_config.log_server.info('[Server]: handle:'
                                           ' client offline: {}{}'.format(self.request, error))
            except:
                # handler.response_500()
                log_config.log_server.warning('[Server]: handle error')
                os._exit(0)
            handler.receive_response(client=self.request, data=self.data)


if __name__ == '__main__':
    from config.config import *

    DH = DEFAULT_HOST
    DP = DEFAULT_PORT
    JIM = JIMMessageServer

    parser = create_parser(DP, DH)
    namespace = parser.parse_args(sys.argv[1:])
    host = namespace.host
    port = namespace.port

    server = TcpServer((host, port), Server)
    handler = JIM_Server(server)
    storage = ServerStorage()

    try:
        log_config.log_server.info('[Server]: start')
        server.serve_forever()
    except KeyboardInterrupt as e:
        log_config.log_server.info('[Server]: shutdown')
        handler.response_500()
        # server.server_close()
        os._exit(0)
        # server.server_close()
        sys.exit()
    except:
        # server.shutdown()
        handler.response_500()
        log_config.log_server.warning('[Server]: непредвиденная ошибка')
        os._exit(0)
        sys.exit()
