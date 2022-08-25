import threading
import queue

from Chat.receiver import Receiver
from Chat.sender import Sender


class Chat(threading.Thread):
    """
    チャット処理本体
    """
    joined = []
    send_message_queue = queue.Queue()
    display_message_queue = queue.Queue()
    original_message_queue = queue.Queue()

    def __init__(self, irc, nick, oauth):
        """
        コンストラクタ

        :param irc: 通信用ソケット
        :param nick: ユーザー名
        :param oauth: 認証情報
        """
        super().__init__()

        # 全体への参加処理
        cap_message = 'CAP REQ :twitch.tv/membership twitch.tv/tags twitch.tv/commands\r\n'.encode('utf-8')
        pass_message = str('PASS oauth:' + oauth + '\r\n').encode('utf-8')
        nick_message = str('NICK ' + nick + '\r\n').encode('utf-8')
        irc.send(cap_message)
        irc.send(pass_message)
        irc.send(nick_message)

        # 送信用
        self.sender = Sender(irc, self.send_message_queue)

        # 受信用
        self.receiver = Receiver(irc, self.sender, self.display_message_queue, self.original_message_queue)

    def send_comment(self, channel, message):
        """
        コメントする

        :param channel: チャンネル名
        :param message: 送信するコメント
        :return: なし
        """
        self.send_join(channel)
        self.sender.send_message(channel.strip(), message.strip())

    def get_display_message(self):
        """
        表示用のメッセージを返す

        :return: 表示用のメッセージ
        """
        try:
            if self.display_message_queue.empty():
                return ''
            else:
                return self.display_message_queue.get(False)
        except queue.Empty:
            return ''

    def get_original_message_queue(self):
        try:
            if self.original_message_queue.empty():
                return ''
            else:
                return self.original_message_queue.get(False)
        except queue.Empty:
            return ''

    def send_join(self, channel):
        """
        チャンネルに未参加の場合は参加する

        :param channel: 参加するチャンネル
        :return: なし
        """
        if not channel in self.joined:
            self.sender.send_join(channel.strip())
            self.joined.append(channel)
