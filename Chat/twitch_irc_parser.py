import const


def parse_privmsg(line):
    """
    PRIVMSG をパースする

    :param line: PRIVMSG を含む行
    :return: PRIVMSG パース結果
    """
    if not 'PRIVMSG' in line:
        return None

    is_message_include = True
    is_emote_include = False
    channel = ''
    message = ''
    message_with_emote = []
    emotes = []
    user_name = ''

    for elements in line.split(';'):
        (key, value) = elements.split('=')

        if key == 'user-type':
            index = line.index('PRIVMSG')
            msg = line[index + 8:len(line)]
            index = msg.index(':')
            channel = msg[1:index - 1]
            message = msg[index + 1:len(msg)]

            if not len(emotes) == 0:
                index = 0
                for emote in emotes:
                    (emote_id, emote_position) = emote
                    (emote_start, emote_end) = emote_position.split('-')
                    emote_start_position = int(emote_start)
                    emote_end_position = int(emote_end)

                    if index < emote_start_position:
                        normal_text = message[index:emote_start_position - 1]
                        message_with_emote.append(('text', normal_text))
                        index = emote_start_position
                    if index == emote_start_position:
                        message_with_emote.append(('emote', emote_id))
                        index = emote_end_position + 2

                # 末尾のメッセージ処理
                if index != len(message):
                    message_with_emote.append(('text', message[index:len(message)]))
        elif key == 'emote-only':
            is_emote_include = True
            is_message_include = False
        elif key == 'emotes':
            if value == '':
                continue

            is_emote_include = True
            orders = []
            dictionary = {}
            for emote in value.split('/'):
                (emote_id, emote_position) = emote.split(':')
                (start, end) = emote_position.split('-')
                start_position = int(start)
                dictionary[start_position] = (emote_id, emote_position)
                orders.append(start_position)
            orders.sort()
            for order in orders:
                emotes.append(dictionary[order])
        elif key == 'display-name':
            user_name = value

    return PrivmsgMessage(const.TWITCH_IRC_MESSAGE_TYPE_PRIVMSG, channel, user_name,
                          message, message_with_emote, is_emote_include, is_message_include)


def twitch_parse(lines: str):
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
            result = parse_privmsg(line)
            if result is None:
                result = FromTwitchMessage(const.TWITCH_IRC_MESSAGE_TYPE_NOT_SUPPORTED)
            return result
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
    user_name: str
    original_message: str
    emote_split_message: []
    is_emote_include: bool
    is_message_include: bool

    def __init__(self, message_type: str, channel: str, user_name: str, original_message: str, emote_split_message: [],
                 is_emote_include: bool, is_message_include: bool):
        """
        コンストラクタ

        :param message_type: メッセージタイプ
        :param channel: チャンネル名
        :param user_name: ユーザー名
        :param original_message: そのままのメッセージ(エモートは単なる文字列のまま)
        :param emote_split_message: エモート置換用の文字列
        :param is_emote_include: エモートを含んでいるか
        :param is_message_include: メッセージを含んでいるか
        """
        print(emote_split_message)
        super().__init__(message_type)
        self.type = message_type
        self.channel = channel
        self.user_name = user_name
        self.original_message = original_message
        self.emote_split_message = emote_split_message
        self.is_emote_include = is_emote_include
        self.is_message_include = is_message_include
