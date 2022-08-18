import threading

from Chat.twitch_irc_parser import TwitchIrcParser


class Receiver(threading.Thread):
    """
    IRC 受信用
    """

    def __init__(self, irc, sender, display_message_queue):
        """
        コンストラクタ

        :param irc: 受信用ソケット
        :param sender: 送信用ソケットクラスのインスタンス
        :param display_message_queue: 受信結果表示用キュー
        """
        super().__init__()

        self.irc = irc
        self.irc_parser = TwitchIrcParser()

        self.display_message_queue = display_message_queue
        self.sender = sender
        self.start()

    def run(self):
        """
        受信処理スレッド

        :return: なし
        """
        while True:
            # 本当は末尾が \r\n で終了していることを確認する必要あり
            # \r\n で終了していない場合、受信途中
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
                self.display_message_queue.put(parsed[2])
