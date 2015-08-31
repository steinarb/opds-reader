import sys
from PyQt5.Qt import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel, QAbstractItemView, QTableView, QHeaderView
from calibre.web.feeds import feedparser

from calibre_plugins.opds_client.model import OpdsBooksModel
from calibre_plugins.opds_client.config import prefs

class OpdsDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        self.db = gui.current_db

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.opds_url = QLabel(prefs['opds_url'])

        self.setWindowTitle('OPDS Client')
        self.setWindowIcon(icon)

        self.library_view = QTableView(self)
        self.library_view._model = OpdsBooksModel(self.library_view)
        self.library_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.layout.addWidget(self.library_view)

        self.about_button = QPushButton('About', self)
        self.about_button.clicked.connect(self.about)
        self.layout.addWidget(self.about_button)

        self.download_opds_button = QPushButton('Download OPDS', self)
        self.download_opds_button.clicked.connect(self.download_opds)
        self.layout.addWidget(self.download_opds_button)

        self.conf_button = QPushButton('Plugin configuration', self)
        self.conf_button.clicked.connect(self.config)
        self.layout.addWidget(self.conf_button)

        self.resize(self.sizeHint())

    def about(self):
        text = get_resources('about.txt')
        QMessageBox.about(self, 'About the OPDS Client plugin', text.decode('utf-8'))

    def download_opds(self):
        feed = feedparser.parse(prefs['opds_url'])
        print feed
        newest_url = feed['entries'][0]['links'][0]['href']
        print newest_url
        newest_feed = feedparser.parse(newest_url)
        newest_model = OpdsBooksModel(None, newest_feed['entries'])
        self.library_view.setModel(newest_model)
        self.library_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.library_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.library_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.resize(self.sizeHint())

    def config(self):
        self.do_user_config(parent=self)
        self.opds_url.setText(prefs['opds_url'])
