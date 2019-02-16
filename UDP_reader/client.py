from socket import *
import json
import argparse
import sys
import time
from threading import Thread

from jim_message.jim_message import JIMMessageClient
from log import log_config
# from start_test import *
from DB.client import ClientStorage
from crypto.sec_hach import crypto_hash_psw
from crypto.sec_mes import Crypto_Message


def create_parser(Default_Port, Default_Host, Default_Name):
    parser_client = argparse.ArgumentParser(prog='server', description='сервер', epilog='(C)2018')
    parser_client.add_argument('-p', '--port', type=int, default=Default_Port, help='порт')
    parser_client.add_argument('-a', '--host', type=str, default=Default_Host, help='IP-адрес')
    parser_client.add_argument('-name', '--name', type=str, default=Default_Name, help='Имя')
    parser_client.add_argument('-r', action='store_const', const=False,
                               help='Клиент запущен в режиме чтения чата')
    parser_client.add_argument('-w', action='store_const', const=False,
                               help='Клиент запущен в режиме передачи сообщений в чат')
    return parser_client


class JIM_Client:
    """ Класс должен обрабатывать полученные сообщения от сервера и ответы клиента """

    def __init__(self, account_name='TestName', password='testpassword'):
        self.protocol = JIMMessageClient(account_name)
        self.user = account_name
        self.password = crypto_hash_psw(password)
        self.storage = ClientStorage('Client')
        self.storage.add_contact(account_name)

    @staticmethod
    def __deserialization_msg(data):
        """ Декодирует полученное зашифрованное сообщение """
        dec_cry = Crypto_Message()
        data_dec_cry = dec_cry._decrypt(data)
        return json.loads(data_dec_cry.decode('utf-8'))

    def authenticate_msg(self):
        return self.protocol.authenticate_msg(self.password)

    def send_msg(self, msg_client):
        return self.protocol.msg_msg(msg_client)

    def receiver(self, ):
        return self.protocol.receiver()

    def presence_msg(self):
        return self.protocol.presence_msg()

    def msg_msg(self, msg_client):
        self.storage.add_message(self.user, msg_client)
        return self.protocol.msg_msg(msg_client)

    def quit_msg(self):
        return self.protocol.quit_msg()

    def receive_response(self, data):
        """ проверка по response """
        response = self.__deserialization_msg(data)

        if response.get('response') == 200:
            log_config.log_client.info('[Client]: подключение к серверу выполнено')

        elif response.get('response') == 202:
            log_config.log_client.info('[Client]: авторизация прошла успешно')
            return True
        elif not response.get('response') < 400 and response.get('response') < 500:
            log_config.log_client.error('[Client]: {}'.format(response['error']))
            return False

        elif response.get('response') == 500:
            log_config.log_client.info('[Client]: {}'.format(response['error']))
            log_config.log_client.error('[Client]: {}'.format(response))
            quit_client()

        elif response.get('response') == 600:
            # self.storage.add_message(response['user'], response['message'])
            #  sqlalchemy.exc.ProgrammingError: (sqlite3.ProgrammingError)
            return response

        else:
            log_config.log_client.error('[Client]: Ошибка response')


class Chat:
    def __init__(self, user_name, obj_Client):
        self.user_name = user_name
        self.client_chat = obj_Client
        self.response = None

    def send_ui(self, message):
        """ загатовка для UI """
        self.client_chat.send_msg(message)

    def recv_ui(self):
        """ загатовка для UI """
        self.response = self.client_chat.ret_msg()
        print(self.message())
        return self.message()

    def transmitter_thread(self):
        try:
            while True:
                time.sleep(0.5)
                msg_client = input('>>>')
                if 'quit' == msg_client:
                    self.quit()
                self.client_chat.send_msg(msg_client)
        except KeyboardInterrupt:
            self.quit()
        except BrokenPipeError as e:
            log_config.log_client.error('Client stop, error: {}'.format(e))
            log_config.log_client.info('[Client]: выход из чата')
            sys.exit()

    def receiver_thread(self):
        while True:
            self.response = self.client_chat.ret_msg()
            print(self.message())

    def message(self):
        return '<{}>: {}'.format(self.response['user'], self.response['message'])

    def quit(self):
        try:
            self.client_chat.disconnect_server()
            log_config.log_client.info('[Client]: выход из чата')
            sys.exit()
        except BrokenPipeError as e:
            log_config.log_client.error('Client stop, error: {}'.format(e))
            log_config.log_client.info('[Client]: выход из чата')
            sys.exit()


class Client:

    def __init__(self, user):
        self.handler = JIM_Client(user['login'], user['password'])

    @log_config.log(__qualname__)
    def connect_server(self, server_host='127.0.0.1', server_port=7777):
        """ Соединение с сервером """
        try:
            self.host = server_host
            self.port = server_port
            self.address = (self.host, self.port)
            self.s = socket(AF_INET, SOCK_STREAM)
            self.s.connect(self.address)
            return True
        except ConnectionRefusedError as e:
            log_config.log_client.error('Client stop, error: {}'.format(e))

    @log_config.log(__qualname__)
    def disconnect_server(self):
        self.s.send(self.handler.quit_msg())
        self.s.shutdown(SHUT_RDWR)
        return 'Correct stop'

    def send_msg(self, msg_client):
        self.s.send(self.handler.msg_msg(msg_client))

    def receiver(self):
        self.s.send(self.handler.receiver())

    def ret_msg(self):
        response_server = self.s.recv(8192)
        return self.handler.receive_response(response_server)

    def presence_msg(self):
        self.s.send(self.handler.presence_msg())
        response_server = self.s.recv(8192)
        self.handler.receive_response(response_server)

    def authenticate_msg(self):
        self.s.send(self.handler.authenticate_msg())
        response_server = self.s.recv(8192)
        return self.handler.receive_response(response_server)


class Client_UI(Client):
    def __init__(self, user):
        super().__init__(user)
        self.user = user

    def start(self, flag):
        chat = Chat(self.user['login'], self)
        if flag == 't':
            log_config.log_client.debug('[Client]: transmitter')
            chat.transmitter()
        elif flag == 'r':
            log_config.log_client.debug('[Client]: receiver')
            chat.receiver()
        else:
            self.disconnect_server()


def menu():
    answer = input('\nДобро пожаловать!\n'
                   'Выберите дальнейшее действие:\n'
                   'new_chat: перейти в chat(потоки)\n'
                   'test: test\n'
                   'help: справка\n'
                   'quit: выход\n')
    return answer


def new_chat():
    chat = Chat(user_name=user['login'], obj_Client=client)
    client.send_msg('[Hi]')

    th_receiver = Thread(target=chat.receiver_thread)
    th_receiver.daemon = True
    log_config.log_client.info('[Client]: CHAT')
    th_receiver.start()
    chat.transmitter_thread()
    th_receiver.join()


@log_config.log('Client')
def test():
    if client.connect_server(host, port):
        return 'test выполнен'
    else:
        return 'test провален'


@log_config.log('Client')
def menu_help():
    menu_help_msg = '\nnew_ chat: переход в chat(потоки)\n' \
                    'test: test\n' \
                    'help: справка\n' \
                    'quit: выход \n'
    return menu_help_msg


def quit_client():
    try:
        client.disconnect_server()
        log_config.log_client.debug('[Client]: shutdown')
        sys.exit()
    except BrokenPipeError as e:
        log_config.log_client.error('[Client]: shutdown\nERROR: {}'.format(e))
        sys.exit()


def menu_select(answer):
    try:
        menu_answer = {'new_chat': new_chat,
                       'test': test,
                       'help': menu_help,
                       'quit': quit_client,
                       }
        menu_answer[answer]()
        answer_2 = input('Продолжить работу с программой?\n"y" - Да: ')
        menu_select(menu()) if answer_2 == 'y' else menu_select('quit')
    except KeyError:
        log_config.log_client.debug('[Client]: Вы ввели неверную команду, попробуйте ещё раз!')
        menu_select(menu())


def auth(name_cl):
    try:
        account_name = input('Введите имя пользователя:')
        if account_name:
            name_user = account_name
        else:
            name_user = name_cl
        password = input('Введите пароль:')
        user_client = {'login': name_user, 'password': password}
        return user_client
    except KeyboardInterrupt:
        log_config.log_client.info('[Client]: выход без авторизации')


if __name__ == '__main__':
    from config.config import *

    DH = DEFAULT_HOST
    DP = DEFAULT_PORT
    DN = DEFAULT_NAME
    JIM = JIM_Client

    parser = create_parser(DP, DH, DN)
    namespace = parser.parse_args(sys.argv[1:])
    host = namespace.host
    port = namespace.port
    name = namespace.name
    user = auth(name)
    client = Client(user)
    if client.connect_server(host, port):
        client.presence_msg()
        if client.authenticate_msg():
            try:
                menu_select(menu())
            except KeyboardInterrupt:
                client.disconnect_server()
                print('Досрочное завершение!')
                sys.exit()
        else:
            log_config.log_client.error('[Client]: Ошибка при авторизации: {}'.format(user))
    else:
        log_config.log_client.error('[Client]: сервер не отвечает')
        sys.exit()
