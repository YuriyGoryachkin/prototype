import sys
from PyQt5.QtWidgets import QApplication, QDialog
from gui.start_window import StartWindow
from gui.main_window_3 import MainWindow, MainWindow2


if __name__ == '__main__':
    app = QApplication(sys.argv)
    user = StartWindow()
    if user.exec_() == QDialog.Accepted:
        window1 = MainWindow(user.get_login())
        window1.on_recv()
        window2 = MainWindow2(user.get_login())
        # window.resize(300, 500)
        window1.move(200, 200)
        window2.move(480, 200)
        window1.setWindowTitle('Receiver')
        window2.setWindowTitle('Transmitter')
        # window.show()
        sys.exit(app.exec_())