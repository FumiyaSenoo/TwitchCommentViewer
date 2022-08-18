import os
import socket
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from PyQt6.QtWidgets import QApplication

from Chat.chat import Chat
from GUI.gui import MainWindow


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
    """
    エントリーポイント
    """
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
