import string

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView

from main import write_oauth


class AuthenticateBrowser(QWebEngineView):
    def __init__(self):
        super().__init__()
        url = 'https://id.twitch.tv/oauth2/authorize?client_id=a326p3d3gudcg1u426siqk43cavshn' \
              '&redirect_uri=http://localhost&response_type=token&scope=user:read:email chat:read chat:edit'
        self.load(QUrl(url))
        self.resize(1000, 600)
        self.move(200, 200)
        self.urlChanged.connect(lambda url: self.url_changed(url.toString()))
        self.show()

    def url_changed(self, url: string):
        if not 'localhost/#' in url:
            return

        is_will_close = False

        elements = url.split('#')[1].split('&')
        for element in elements:
            (key, value) = element.split('=')
            if key == 'access_token':
                write_oauth(value.strip())
                is_will_close = True

        if is_will_close:
            self.close()
