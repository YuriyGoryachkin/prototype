from PyQt5.QtWidgets import *
import sys


class StartWindow(QDialog):
    def __init__(self, parent=None):
        super(StartWindow,self).__init__(parent)
        self.loginLabel = QLabel('Login')
        self.loginPass = QLabel('Password')
        self.login = QLineEdit(self)
        self.password = QLineEdit(self)
        self.btnQuit = QPushButton('QUIT', self)
        self.btnEntry = QPushButton('ENTRY', self)
        self.btnQuit.clicked.connect(qApp.quit)
        self.btnEntry.clicked.connect(self.on_clicked)
        layout = QVBoxLayout(self)
        layout.addWidget(self.loginLabel)
        layout.addWidget(self.login)
        layout.addWidget(self.loginPass)
        layout.addWidget(self.password)
        layout.addWidget(self.btnEntry)
        layout.addWidget(self.btnQuit)


    def on_clicked(self):
        # print(self.login.text())
        # print(self.password.text())
        if self.login.text():
            self.accept()
        else:
            QMessageBox.warning(
                self, 'Error', '')

    def get_login(self):
        user_dict = {'login': self.login.text(),
                'password': self.password.text()}
        return user_dict



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StartWindow()
    window.show()
    sys.exit(app.exec_())