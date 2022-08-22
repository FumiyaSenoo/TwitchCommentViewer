import threading

import const
from Chat.twitch_irc_parser import twitch_parse


class Receiver(threading.Thread):
    """
    IRC 受信用
    """

    def __init__(self, irc, sender, display_message_queue, emote):
        """
        コンストラクタ

        :param irc: 受信用ソケット
        :param sender: 送信用ソケットクラスのインスタンス
        :param display_message_queue: 受信結果表示用キュー
        """
        super().__init__()

        self.irc = irc

        self.display_message_queue = display_message_queue
        self.emote = emote
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
            parsed = twitch_parse(message)
            print(message)

            if parsed.type == const.TWITCH_IRC_MESSAGE_TYPE_NOT_SUPPORTED:
                pass
            elif parsed.type == const.TWITCH_IRC_MESSAGE_TYPE_PING:
                self.sender.send_pong(parsed.received_message)
            elif parsed.type == const.TWITCH_IRC_MESSAGE_TYPE_PRIVMSG:
                self.display_message_queue.put(parsed.original_message)
                # 以下、エモート表示のためのいい加減実装
                self.emote.put(parsed.emote_split_message)
