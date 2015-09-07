"""main.py: Configuration parameter GUI for a Calibre plugin that can read OPDS feeds"""

__author__    = "Steinar Bang"
__copyright__ = "Steinar Bang, 2015"
__credits__   = ["Steinar Bang"]
__license__   = "GPL v3"

from PyQt5.Qt import QWidget, QGridLayout, QLabel, QLineEdit, QCheckBox

from calibre.utils.config import JSONConfig

prefs = JSONConfig('plugins/opds_client')

prefs.defaults['opds_url'] = 'http://localhost:8080/opds'
prefs.defaults['hideNewspapers'] = True
prefs.defaults['hideBooksAlreadyInLibrary'] = True

class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        labelColumnWidths = []

        self.opdsUrlLabel = QLabel('OPDS URL: ')
        self.layout.addWidget(self.opdsUrlLabel, 0, 0)
        labelColumnWidths.append(self.layout.itemAtPosition(0, 0).sizeHint().width())

        self.opdsUrlEditor = QLineEdit(self)
        self.opdsUrlEditor.setText(prefs['opds_url'])
        self.layout.addWidget(self.opdsUrlEditor, 0, 1)
        self.opdsUrlLabel.setBuddy(self.opdsUrlEditor)

        self.hideNewsCheckbox = QCheckBox('Hide Newspapers', self)
        self.hideNewsCheckbox.setChecked(prefs['hideNewspapers'])
        self.layout.addWidget(self.hideNewsCheckbox, 1, 0)
        labelColumnWidths.append(self.layout.itemAtPosition(1, 0).sizeHint().width())

        self.hideBooksAlreadyInLibraryCheckbox = QCheckBox('Hide books already in library', self)
        self.hideBooksAlreadyInLibraryCheckbox.setChecked(prefs['hideBooksAlreadyInLibrary'])
        self.layout.addWidget(self.hideBooksAlreadyInLibraryCheckbox, 2, 0)
        labelColumnWidths.append(self.layout.itemAtPosition(2, 0).sizeHint().width())

        labelColumnWidth = max(labelColumnWidths)
        self.layout.setColumnMinimumWidth(1, labelColumnWidth * 2)

    def save_settings(self):
        prefs['opds_url'] = self.opdsUrlEditor.text()
        prefs['hideNewspapers'] = self.hideNewsCheckbox.isChecked()
        prefs['hideBooksAlreadyInLibrary'] = self.hideBooksAlreadyInLibraryCheckbox.isChecked()

            
