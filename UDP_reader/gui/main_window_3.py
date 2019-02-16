from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import sys
import time
from client import Client_UI, Chat


class MyThread(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(str)

    def __init__(self, chat, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.running = False
        self.chat = chat

    def run(self):
        self.running = True
        while self.running:
            text_ret = self.chat.recv_ui()
            textFormatted = '{}'.format(text_ret)
            self.mysignal.emit(textFormatted)
            self.sleep(0.5)


class MainWindow(QMainWindow):
    """ Класс для приёма сообщений """

    def __init__(self, user_dict):
        super().__init__()
        self.user = user_dict['login']
        self.client = Client_UI(user_dict)
        self.chat = Chat(self.user, self.client)
        self.mythread = MyThread(self.chat)
        self.init_UI()

    def init_UI(self):
        self.label = QLabel(self.user)
        self.label.setAlignment(QtCore.Qt.AlignHCenter)

        self.read_msg = QTextEdit()
        self.read_msg.setReadOnly(True)

        self.mythread.mysignal.connect(self.on_change, QtCore.Qt.QueuedConnection)

        self.vertical_box = QVBoxLayout()
        self.vertical_box.addWidget(self.label)
        self.vertical_box.addWidget(self.read_msg)

        self.central_widget = QFrame(self)
        self.central_widget.setLayout(self.vertical_box)
        self.setCentralWidget(self.central_widget)

        self.show()

        self.client.connect_server()
        self.client.presence_msg()
        self.client.authenticate_msg()

    def on_recv(self):
        if not self.mythread.isRunning():
            self.mythread.start()

    def on_change(self, message):
        self.read_msg.append(message)

    def closeEvent(self, event):
        self.hide()
        self.mythread.running = False
        self.mythread.wait(5000)
        event.accept()


class MainWindow2(QMainWindow):
    """ Класс для отправки сообщений """

    def __init__(self, user_dict):
        super().__init__()
        self.user = user_dict['login']
        self.client = Client_UI(user_dict)
        self.chat = Chat(self.user, self.client)
        self.mythread = MyThread(self.chat)
        self.init_UI()

    def init_UI(self):
        self.label = QLabel(self.user)
        self.label.setAlignment(QtCore.Qt.AlignHCenter)
        self.label.hide()

        self.send_msg = QLineEdit()

        self.btnSend = QPushButton('Send', self)
        self.btnQuit = QPushButton('Quit', self)

        self.horizontal_box = QHBoxLayout()
        self.horizontal_box.addWidget(self.btnQuit)
        self.horizontal_box.addWidget(self.btnSend)

        self.btnSend.clicked.connect(self.on_send)
        self.btnQuit.clicked.connect(qApp.quit)

        self.vertical_box = QVBoxLayout()
        self.vertical_box.addWidget(self.label)
        self.vertical_box.addWidget(self.send_msg)
        self.vertical_box.addLayout(self.horizontal_box)

        self.central_widget = QFrame(self)
        self.central_widget.setLayout(self.vertical_box)
        self.setCentralWidget(self.central_widget)

        self.show()

        self.client.connect_server()
        self.client.presence_msg()
        self.client.authenticate_msg()

    def on_send(self):
        text = self.send_msg.text()
        self.chat.send_ui(text)
        self.send_msg.setText('')
