import os
import queue
import socket
import sys
import threading
from time import sleep

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLineEdit, QListWidget


class IrcParser:
    """
    Twitch から受信した IRC メッセージをパースするクラス
    """

    def __init__(self):
        """
        コンストラクタ

        何もしない
        """
        pass

    def parse(self, lines):
        """
        パース処理

        :param lines: 受信した IRC メッセージ
        :return: パースした結果
        """
        for line in lines.split('\r\n'):
            elements = line.split(' ')
            if 'PING' in line:
                return 'PING', elements[1]
            elif 'PRIVMSG' in line:
                index = line.index('PRIVMSG')
                msg = line[index + 8:len(line)]
                index = msg.index(':')
                channel = msg[1:index - 1]
                message = msg[index + 1:len(msg)]
                return 'PRIVMSG', channel, message
            else:
                return ''


class Receiver(threading.Thread):
    """
    IRC 受信用
    """

    def __init__(self, irc, sender, displayQueue):
        """
        コンストラクタ

        :param irc: 受信用ソケット
        :param sender: 送信用ソケットクラスのインスタンス
        :param displayQueue: 受信結果表示用キュー
        """
        super().__init__()

        self.irc = irc
        self.irc_parser = IrcParser()

        self.displayQueue = displayQueue
        self.sender = sender
        self.start()

    def run(self):
        """
        受信処理スレッド

        :return: なし
        """
        while True:
            non_striped_message = self.irc.recv(4096).decode('utf-8')
            # message_length = len(non_striped_message)
            # while not non_striped_message[message_length-2:message_length-1] == '\r\n':
            #     print('&&&&&' + non_striped_message)
            #     non_striped_message = non_striped_message + self.irc.recv(4096).decode('utf-8')
            message = non_striped_message.strip()
            parsed = self.irc_parser.parse(message)
            print(message)
            if len(parsed) == 0:
                continue

            if parsed[0] == 'PING':
                self.sender.send_pong(parsed[1])
            elif parsed[0] == 'PRIVMSG':
                self.displayQueue.put(parsed[2])


class Sender(threading.Thread):
    """
    IRC 送信用
    """

    def __init__(self, irc, messageQueue):
        """

        :param irc: 受信用ソケット
        :param messageQueue: 送信用メッセージが詰められるキュー
        """
        super().__init__()

        self.irc = irc

        self.messageQueue = messageQueue
        self.start()

    def run(self):
        """
        送信処理スレッド

        :return: なし
        """
        while True:
            try:
                if not self.messageQueue.empty():
                    msg = self.messageQueue.get(False)
                    print(msg)
                    irc.send(msg.encode('utf-8'))
            except queue.Empty:
                sleep(0.25)

    def send_message(self, channel, message):
        """
        Twitch にコメントする

        :param channel: チャンネル名
        :param message: 送信するメッセージ
        :return: なし
        """
        msg = 'PRIVMSG #' + channel + ' :' + message + '\r\n'
        self.messageQueue.put(msg)

    def send_pong(self, message):
        """
        PING に対応する PONG を送信する

        :param message: PONG と合わせて送信するメッセージ
        :return: なし
        """
        self.messageQueue.put('PONG ' + message + '\r\n')

    def send_join_message(self, channel):
        """
        チャンネルに参加する

        :param channel: チャンネル名
        :return: なし
        """
        msg = 'JOIN #' + channel + '\r\n'
        self.messageQueue.put(msg)


class Chat(threading.Thread):
    """
    チャット処理本体
    """
    joined = []
    sendMessageQueue = queue.Queue()
    displayQueue = queue.Queue()

    def __init__(self, irc, nick, oauth):
        """
        コンストラクタ

        :param irc: 通信用ソケット
        :param nick: ユーザー名
        :param oauth: 認証情報
        """
        super().__init__()

        # 全体への参加処理
        capMessage = 'CAP REQ :twitch.tv/membership twitch.tv/tags twitch.tv/commands\r\n'.encode('utf-8')
        passMessage = str('PASS oauth:' + oauth + '\r\n').encode('utf-8')
        nickMessage = str('NICK ' + nick + '\r\n').encode('utf-8')
        irc.send(capMessage)
        irc.send(passMessage)
        irc.send(nickMessage)

        # 送信用
        self.sender = Sender(irc, self.sendMessageQueue)

        # 受信用
        self.receiver = Receiver(irc, self.sender, self.displayQueue)

    def send_comment(self, channel, message):
        """
        コメントする

        :param channel: チャンネル名
        :param message: 送信するコメント
        :return: なし
        """
        # チャンネルに未参加の場合は参加する
        if not channel in self.joined:
            self.sender.send_join_message(channel.strip())

        self.sender.send_message(channel.strip(), message.strip())


class MainWindow(QWidget):
    """
    GUI
    """
    listWidget = None
    chat = None
    layout = None
    editor = None

    def __init__(self, chat):
        """
        コンストラクタ

        :param chat: チャットインスタンス
        """
        super().__init__()
        self.chat = chat

        self.layout = QVBoxLayout(self)

        # Window 全体設定
        self.title = 'Twitch CommentViewer'
        self.width = 400
        self.height = 200
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, self.width, self.height)

        # 受信したコメント表示欄
        self.listWidget = QListWidget(self)

        # チャンネル名入力欄
        self.channel = QLineEdit(self)
        self.channel.setPlaceholderText('channel')

        # コメント入力欄
        self.editor = QLineEdit(self)
        self.editor.returnPressed.connect(lambda: self.send())
        self.editor.setPlaceholderText('message')

        # 送信ボタン
        button = QPushButton(self)
        button.setText('send')
        button.clicked.connect(self.send)

        # 描画更新用タイマー
        timer = QTimer(self)
        timer.timeout.connect(self.reload)
        timer.start(1000)

        # レイアウト処理
        self.layout.addWidget(self.listWidget)
        self.layout.addWidget(self.channel)
        self.layout.addWidget(self.editor)
        self.layout.addWidget(button)

        # 表示
        self.show()

    def reload(self):
        """
        描画更新処理

        :return:
        """
        try:
            if self.chat.displayQueue.empty():
                return
            else:
                msg = self.chat.displayQueue.get(False)
        except queue.Empty:
            return

        self.listWidget.addItem(msg)

    def send(self):
        """
        コメント送信

        :return: なし
        """
        message = self.editor.text()
        channel = self.channel.text()
        self.editor.setText('')
        self.chat.send_comment(channel, message)


def get_oauth():
    """
    ファイルから oauth 情報を取得する

    :return: oauth 情報
    """
    oauth_path = 'settings/oauth'
    is_exist = os.path.isfile(oauth_path)
    if not is_exist:
        return ''
    return open(oauth_path).read()


def get_nick():
    """
    ファイルからユーザー名を取得する

    :return: ユーザー名
    """
    nick_path = 'settings/nick'
    is_exist = os.path.isfile(nick_path)
    if not is_exist:
        return ''
    return open(nick_path).read()


def get_irc():
    """
    Twitch とのデータやり取りするための socket を生成する

    :return: ソケット
    """
    result = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc_port = 6667
    result.connect(('irc.chat.twitch.tv', irc_port))
    return result


if __name__ == '__main__':
    app = QApplication(sys.argv)

    nick = get_nick()
    if len(nick) == 0:
        sys.exit(1)

    oauth = get_oauth()
    if not len(oauth) == 30:
        sys.exit(2)

    irc = get_irc()
    chat = Chat(irc, nick, oauth)

    window = MainWindow(chat)

    return_code = app.exec()

    irc.close()

    sys.exit(return_code)
