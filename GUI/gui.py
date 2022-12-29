import os.path
import urllib.request
import urllib.error

from PyQt6.QtCore import QTimer, Qt, QRect
from PyQt6.QtGui import QImage, QPainter, QFontMetrics, QFont, QColor
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QLineEdit, QListWidget, QHBoxLayout, QListWidgetItem


class MainWindow(QWidget):
    """
    GUI
    """

    def __init__(self):
        """
        コンストラクタ
        """
        super().__init__()
        # self.chat = chat

        # Window 全体設定
        self.chat = None
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

    def set_chat(self, chat):
        self.chat = chat

    def reload(self):
        """
        描画更新処理

        :return: なし
        """
        emote = self.chat.get_display_message()
        if not len(emote) == 0:
            widget = ListItem(self.list_widget, emote)
            widget_item = QListWidgetItem(self.list_widget)
            widget_item.setSizeHint(widget.size())
            self.list_widget.addItem(widget_item)
            self.list_widget.setItemWidget(widget_item, widget)

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


class ListItem(QWidget):
    """
    リスト用描画用クラス
    """
    def __init__(self, parent, message):
        """
        コンストラクタ

        :param parent: 親ウィジェット
        :param message: 表示するメッセージ
        """
        super().__init__(parent)
        self.views = {}
        self.font = QFont()
        index = 0
        rect = QFontMetrics(self.font).boundingRect('A')
        self.setFixedHeight(rect.height())

        for element in message:
            (key, value) = element
            if key == 'text':
                self.views[index] = (key, value)
            elif key == 'emote':
                (emote_id, emote_text) = value
                try:
                    url = 'https://static-cdn.jtvnw.net/emoticons/v2/' + emote_id + '/static/light/2.0'
                    image = QImage()
                    file_path = 'cache/' + emote_text
                    if not os.path.isfile(file_path):
                        with urllib.request.urlopen(url) as from_web:
                            row_bytes = from_web.read()
                            with open(file_path, mode='wb') as file:
                                file.write(row_bytes)
                    image.load(file_path)
                    self.views[index] = (key, image)
                    self.setFixedHeight(image.height())
                except urllib.error.URLError as e:
                    # 本来はエモートなので、前後にスペースを入れて読めるようにする
                    self.views[index] = ('text', ' ' + emote_text + ' ')
            index += 1

    def paintEvent(self, event):
        """
        描画処理

        :param event: PaintEvent
        :return: なし
        """
        painter = QPainter(self)
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(self.font)
        point = painter.brushOrigin()
        for index in range(len(self.views)):
            (key, value) = self.views[index]
            if key == 'text':
                font_rect = QFontMetrics(painter.font()).boundingRect(value)
                y = self.height() - font_rect.height()
                draw_rect = QRect(point.x(), y, font_rect.width(), font_rect.height())
                painter.drawText(draw_rect, Qt.AlignmentFlag.AlignBottom, value)
                point.setX(point.x() + draw_rect.width())
            elif key == 'emote':
                painter.drawImage(point, value)
                point.setX(point.x() + value.width())
