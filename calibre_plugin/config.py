"""main.py: Configuration parameter GUI for a Calibre plugin that can read OPDS feeds"""

__author__    = "Steinar Bang"
__copyright__ = "Steinar Bang, 2015"
__credits__   = ["Steinar Bang"]
__license__   = "GPL v3"

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

            
