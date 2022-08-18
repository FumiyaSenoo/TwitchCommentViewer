import queue
import threading
from time import sleep


class Sender(threading.Thread):
    """
    IRC 送信用
    """

    def __init__(self, irc, message_queue):
        """
        コンストラクタ

        :param irc: 受信用ソケット
        :param message_queue: 送信用メッセージが詰められるキュー
        """
        super().__init__()

        self.irc = irc

        self.message_queue = message_queue
        self.start()

    def run(self):
        """
        送信処理スレッド

        :return: なし
        """
        while True:
            try:
                if not self.message_queue.empty():
                    msg = self.message_queue.get(False)
                    print(msg)
                    self.irc.send(msg.encode('utf-8'))
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
        self.message_queue.put(msg)

    def send_pong(self, message):
        """
        PING に対応する PONG を送信する

        :param message: PONG と合わせて送信するメッセージ
        :return: なし
        """
        self.message_queue.put('PONG ' + message + '\r\n')

    def send_join(self, channel):
        """
        チャンネルに参加する

        :param channel: チャンネル名
        :return: なし
        """
        message = 'JOIN #' + channel + '\r\n'
        self.message_queue.put(message)
