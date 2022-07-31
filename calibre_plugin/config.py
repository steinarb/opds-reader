"""main.py: Configuration parameter GUI for a Calibre plugin that can read OPDS feeds"""

__author__    = "Steinar Bang"
__copyright__ = "Steinar Bang, 2015-2022"
__credits__   = ["Steinar Bang"]
__license__   = "GPL v3"

from PyQt5.Qt import QWidget, QGridLayout, QLabel, QComboBox, QCheckBox

from calibre.utils.config import JSONConfig

prefs = JSONConfig('plugins/opds_client')

prefs.defaults['opds_url'] = ['http://localhost:8080/opds']
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

        print(type(prefs.defaults['opds_url']))
        print(type(prefs['opds_url']))
        convertSingleStringOpdsUrlPreferenceToListOfStringsPreference()
        self.opdsUrlEditor = QComboBox(self)
        self.opdsUrlEditor.addItems(prefs['opds_url'])
        self.opdsUrlEditor.setEditable(True)
        self.opdsUrlEditor.setInsertPolicy(QComboBox.InsertAtTop)
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
        prefs['hideNewspapers'] = self.hideNewsCheckbox.isChecked()
        prefs['hideBooksAlreadyInLibrary'] = self.hideBooksAlreadyInLibraryCheckbox.isChecked()
        prefs['opds_url'] = saveOpdsUrlCombobox(self.opdsUrlEditor)

def saveOpdsUrlCombobox(opdsUrlEditor):
    opdsUrls = []
    print("item count: %d" % opdsUrlEditor.count())
    for i in range(opdsUrlEditor.count()):
        print("item %d: %s" % (i, opdsUrlEditor.itemText(i)))
        opdsUrls.append(opdsUrlEditor.itemText(i))
    # Move the selected item first in the list
    currentSelectedUrlIndex = opdsUrlEditor.currentIndex()
    if currentSelectedUrlIndex > 0:
        currentUrl = opdsUrls[currentSelectedUrlIndex]
        del opdsUrls[currentSelectedUrlIndex]
        opdsUrls.insert(0, currentUrl)
    return opdsUrls

def convertSingleStringOpdsUrlPreferenceToListOfStringsPreference():
    if type(prefs['opds_url']) != type(prefs.defaults['opds_url']):
        # Upgrade config option from single string to list of strings
        originalUrl = prefs['opds_url']
        prefs['opds_url'] = prefs.defaults['opds_url']
        prefs['opds_url'].insert(0, originalUrl)
