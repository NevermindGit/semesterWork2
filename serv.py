from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QGridLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QObject, QTimer
import pixelui
import sys
from threading import Thread
import socket

conn = None


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, x):
        super(MainWindow, self).__init__()
        self.ui = pixelui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.nicknameLine.setText(x.name)
        self.timer = QTimer()
        self.timer.timeout.connect(self.end_game)

    def end_game(self):
        self.close()

    def setupButtons(self):
        colors = ['white', 'black', 'red', 'green', 'blue', 'yellow', 'purple']
        for i in range(len(colors)):
            getattr(self.ui, 'pushButton_%s' % colors[i]).clicked.connect(self.getColor)
            getattr(self.ui, 'pushButton_%s' % colors[i]).setStyleSheet(
                "background-color: %s; height: 35px; width: 35px; border-radius: 16px" % colors[i])

        for i in range(10):
            for j in range(10):
                button_name = 'btn' + str(i) + str(j)
                self.ui.button_name = QtWidgets.QPushButton(self.ui.gridLayoutWidget)
                self.ui.button_name.setMinimumSize(47, 47)
                self.ui.button_name.setObjectName(button_name)
                self.ui.button_name.setStyleSheet("QPushButton {background-color: white; border: 1px solid white}"
                                                  "QPushButton::hover {border: 1px solid cyan}"
                                                  )

                self.ui.gridLayout.addWidget(self.ui.button_name, i, j, 1, 1)
                self.ui.button_name.clicked.connect(self.change_color)

    def getColor(self):
        btn = self.sender()
        color = str(btn.objectName())
        x.pick_color(color)
        # btn.setStyleSheet("background-color: %s; border: 1px solid cyan" % color)

        return color

    def btntap(self):
        btn = self.sender()
        print(btn.objectName() + 'tapped')

    def change_color(self):
        btn = self.sender()
        color = x.returnColor()
        btn.setStyleSheet("QPushButton {background-color: %s; border: 0.5px solid %s}"
                          "QPushButton::hover {border: 1px solid cyan}" % (color, color))
        data = (btn.objectName()[3] + ' ' + btn.objectName()[4] + ' ' + color).encode()  # 'x y color'
        print(data)
        global conn
        conn.send(data)
        print(f'Player {x.name} colored pixel {btn.objectName()[3]},{btn.objectName()[4]} with {color} color.')

    def data_handler(self, data):
        # data [x, y, color]
        data = data.decode().split()
        x = int(data[0])
        y = int(data[1])
        color = data[2]
        if data:
            self.ui.gridLayout.itemAtPosition(x, y).widget().setStyleSheet(
                "QPushButton {background-color: %s; border: 0.5px solid %s}"
                "QPushButton::hover {border: 1px solid cyan}" % (color, color))


class Player:
    def __init__(self, name):
        self.color = None
        self.name = name

    def pick_color(self, color):
        self.color = color
        print(f'Player {self.name} picked {color} color.')

    def returnColor(self):
        if self.color is None:
            return 'white'
        else:
            return self.color


class ClientThread(Thread):

    def __init__(self, ip, port, window):
        Thread.__init__(self)
        self.window = window
        self.ip = ip
        self.port = port
        print("[+] New server socket thread started for " + ip + ":" + str(port))

    def run(self):
        while True:
            # (conn, (self.ip,self.port)) = serverThread.tcpServer.accept()
            global conn
            data = conn.recv(2048)
            window.data_handler(data)
            print(data, "123")


class ServerThread(Thread):
    def __init__(self, window):
        Thread.__init__(self)
        self.window = window

    def run(self):
        TCP_IP = '0.0.0.0'
        TCP_PORT = 80
        BUFFER_SIZE = 20
        tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcpServer.bind((TCP_IP, TCP_PORT))
        threads = []

        tcpServer.listen(5)
        while True:
            print("Multithreaded Python server : Waiting for connections from TCP clients...")
            global conn
            (conn, (ip, port)) = tcpServer.accept()
            newthread = ClientThread(ip, port, window)
            newthread.start()
            threads.append(newthread)

        for t in threads:
            t.join()


x = Player(name='123')
app = QtWidgets.QApplication([])
window = MainWindow(x)
serverThread = ServerThread(window)
serverThread.start()
window.setupButtons()
window.show()
sys.exit(app.exec())
