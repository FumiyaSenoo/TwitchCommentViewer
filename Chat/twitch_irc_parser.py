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
