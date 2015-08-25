from PyQt5.Qt import QWidget, QHBoxLayout, QLabel, QLineEdit

from calibre.utils.config import JSONConfig

prefs = JSONConfig('plugins/opds_client')

prefs.defaults['opds_url'] = 'http://localhost:8080/opds'

class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QHBoxLayout()
        self.setLayout(self.l)

        self.label = QLabel('OPDS URL: ')
        self.l.addWidget(self.label)

        self.opds_url = QLineEdit(self)
        self.opds_url.setText(prefs['opds_url'])
        self.l.addWidget(self.opds_url)
        self.label.setBuddy(self.opds_url)

    def save_settings(self):
        prefs['opds_url'] = self.opds_url.text()

            
