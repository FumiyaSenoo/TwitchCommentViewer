from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QLineEdit, QListWidget, QHBoxLayout


class MainWindow(QWidget):
    """
    GUI
    """

    def __init__(self, chat):
        """
        コンストラクタ

        :param chat: チャットインスタンス
        """
        super().__init__()
        self.chat = chat

        # Window 全体設定
        self.title = 'Twitch CommentViewer'
        self.width = 400
        self.height = 200
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, self.width, self.height)

        # 受信したコメント表示欄
        self.list_widget = QListWidget(self)

        # チャンネル名入力欄
        self.channel = QLineEdit(self)
        self.channel.setPlaceholderText('channel')
        self.channel.returnPressed.connect(lambda: self.join())

        # チャンネル参加ボタン
        self.join_button = QPushButton(self)
        self.join_button.setText('join')
        self.join_button.clicked.connect(lambda: self.join())

        # コメント入力欄
        self.comment = QLineEdit(self)
        self.comment.returnPressed.connect(lambda: self.send())
        self.comment.setPlaceholderText('message')

        # 送信ボタン
        self.send_button = QPushButton(self)
        self.send_button.setText('send')
        self.send_button.clicked.connect(self.send)

        # 描画更新用タイマー
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.reload)
        self.timer.start(1000)

        # レイアウト処理
        self.v_box_layout = QVBoxLayout(self)
        self.v_box_layout.addWidget(self.list_widget)
        self.h_box_layout = QHBoxLayout(self)
        self.h_box_layout.addWidget(self.channel)
        self.h_box_layout.addWidget(self.join_button)
        self.v_box_layout.addLayout(self.h_box_layout)
        self.v_box_layout.addWidget(self.comment)
        self.v_box_layout.addWidget(self.send_button)

        # 表示
        self.show()

    def reload(self):
        """
        描画更新処理

        :return: なし
        """
        msg = self.chat.get_display_message()
        if msg == '':
            return

        self.list_widget.addItem(msg)

    def send(self):
        """
        コメント送信

        :return: なし
        """
        comment = self.comment.text()
        channel = self.channel.text()
        self.comment.setText('')
        self.chat.send_comment(channel, comment)

    def join(self):
        """
        チャンネル参加処理

        :return: なし
        """
        channel = self.channel.text()
        self.chat.send_join(channel)