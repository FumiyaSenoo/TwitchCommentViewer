import const


class TwitchIrcParser:
    """
    Twitch から受信した IRC メッセージをパースするクラス
    """

    def __init__(self):
        """
        コンストラクタ

        何もしない
        """
        pass

    @staticmethod
    def parse(lines: str):
        """
        パース処理

        :param lines: 受信した IRC メッセージ
        :return: パースした結果
        """
        for line in lines.split('\r\n'):
            elements = line.split(' ')
            if 'PING' in line:
                return PingMessage(const.TWITCH_IRC_MESSAGE_TYPE_PING, elements[1])
            elif 'PRIVMSG' in line:
                index = line.index('PRIVMSG')
                msg = line[index + 8:len(line)]
                index = msg.index(':')
                channel = msg[1:index - 1]
                message = msg[index + 1:len(msg)]
                return PrivmsgMessage(const.TWITCH_IRC_MESSAGE_TYPE_PRIVMSG, channel, message)
            else:
                return FromTwitchMessage(const.TWITCH_IRC_MESSAGE_TYPE_NOT_SUPPORTED)


class FromTwitchMessage:
    """
    Twitch から受信したメッセージをパースしたものを保持するベースクラス
    """

    type: str

    def __init__(self, message_type: str):
        """
        コンストラクタ

        :param message_type: メッセージのタイプ
        """
        self.type = message_type

    def get_type(self):
        """
        メッセージタイプを返す

        :return: メッセージタイプ
        """
        return self.type


class PingMessage(FromTwitchMessage):
    """
    PING メッセージ
    """

    received_message: str

    def __init__(self, message_type: str, received_message):
        """
        コンストラクタ

        :param message_type: メッセージタイプ
        :param received_message: 受信したメッセージ(PONG で応答する際に利用するメッセージ)
        """
        super().__init__(message_type)
        self.type = message_type
        self.received_message = received_message


class PrivmsgMessage(FromTwitchMessage):
    """
    PRIVMSG メッセージ
    """
    channel: str
    original_message: str

    def __init__(self, message_type: str, channel: str, original_message: str):
        """
        コンストラクタ

        :param message_type: メッセージタイプ
        :param channel: チャンネル名
        :param original_message: 受信したメッセージ部(エモートは単なる文字列のまま)
        """
        super().__init__(message_type)
        self.type = message_type
        self.channel = channel
        self.original_message = original_message

