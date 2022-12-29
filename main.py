import os
import socket
import sys

from PyQt6.QtWidgets import QApplication

from Authenticate.authenticate_browser import AuthenticateBrowser
from Authenticate.authenticate_server import AuthenticateServer
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


def write_oauth(oauth):
    oauth_path = 'settings/oauth'
    is_exist = os.path.isfile(oauth_path)
    if is_exist:
        return
    open(oauth_path).write(oauth)


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

    is_exist_settings_directory = os.path.isdir('settings')
    if not is_exist_settings_directory:
        os.mkdir('settings')
    is_exist_cache_directory = os.path.isdir('cache')
    if not is_exist_cache_directory:
        os.mkdir('cache')

    is_authenticated = True
    nick = get_nick()
    if len(nick) == 0:
        is_authenticated = False

    oauth = get_oauth()
    if not len(oauth) == 30:
        is_authenticated = False

    irc = get_irc()

    if is_authenticated:
        window = MainWindow()
        chat = Chat(irc, nick, oauth)
        window.set_chat(chat)
    else:
        server = AuthenticateServer()
        browser = AuthenticateBrowser()

    return_code = app.exec()

    irc.close()

    sys.exit(return_code)
