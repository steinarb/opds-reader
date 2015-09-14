"""main.py: A GUI to download an OPDS feed, filter out parts of the results, and download selected books from the feed into the local library"""

__author__    = "Steinar Bang"
__copyright__ = "Steinar Bang, 2015"
__credits__   = ["Steinar Bang"]
__license__   = "GPL v3"

import sys
import datetime
from PyQt5.Qt import Qt, QDialog, QGridLayout, QPushButton, QCheckBox, QMessageBox, QLabel, QAbstractItemView, QTableView, QHeaderView

from calibre_plugins.opds_client.model import OpdsBooksModel
from calibre_plugins.opds_client.config import prefs

class DynamicBook(dict):
    pass

class OpdsDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        self.db = gui.current_db

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.opds_url = QLabel(prefs['opds_url'])

        self.setWindowTitle('OPDS Client')
        self.setWindowIcon(icon)

        self.library_view = QTableView(self)
        self.library_view.setAlternatingRowColors(True)
        self.model = OpdsBooksModel(None, self.dummy_books(), self.db)
        self.library_view.setModel(self.model)
        self.library_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.library_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.library_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.library_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resizeAllLibraryViewLinesToHeaderHeight()
        self.library_view.resizeColumnsToContents()
        buttonRowColumnNumber = 7
        self.layout.addWidget(self.library_view, 0, 0, 3, buttonRowColumnNumber + 1)

        self.hideNewsCheckbox = QCheckBox('Hide Newspapers', self)
        self.hideNewsCheckbox.clicked.connect(self.setHideNewspapers)
        self.hideNewsCheckbox.setChecked(prefs['hideNewspapers'])
        self.layout.addWidget(self.hideNewsCheckbox, 3, 0)

        self.hideBooksAlreadyInLibraryCheckbox = QCheckBox('Hide books already in library', self)
        self.hideBooksAlreadyInLibraryCheckbox.clicked.connect(self.setHideBooksAlreadyInLibrary)
        self.hideBooksAlreadyInLibraryCheckbox.setChecked(prefs['hideBooksAlreadyInLibrary'])
        self.layout.addWidget(self.hideBooksAlreadyInLibraryCheckbox, 4, 0)

        # Let the checkbox initial state control the filtering
        self.model.setFilterBooksThatAreNewspapers(self.hideNewsCheckbox.isChecked())
        self.model.setFilterBooksThatAreAlreadyInLibrary(self.hideBooksAlreadyInLibraryCheckbox.isChecked())

        buttonColumnWidths = []
        self.about_button = QPushButton('About', self)
        self.about_button.clicked.connect(self.about)
        self.layout.addWidget(self.about_button, 3, buttonRowColumnNumber)
        buttonColumnWidths.append(self.layout.itemAtPosition(3, buttonRowColumnNumber).sizeHint().width()) 

        self.download_opds_button = QPushButton('Download OPDS', self)
        self.download_opds_button.clicked.connect(self.download_opds)
        self.layout.addWidget(self.download_opds_button, 4, buttonRowColumnNumber)
        buttonColumnWidths.append(self.layout.itemAtPosition(4, buttonRowColumnNumber).sizeHint().width()) 

        self.conf_button = QPushButton('Plugin configuration', self)
        self.conf_button.clicked.connect(self.config)
        self.layout.addWidget(self.conf_button, 5, buttonRowColumnNumber)
        buttonColumnWidths.append(self.layout.itemAtPosition(5, buttonRowColumnNumber).sizeHint().width()) 

        self.downloadButton = QPushButton('Download selected books', self)
        self.downloadButton.clicked.connect(self.downloadSelectedBooks)
        self.layout.addWidget(self.downloadButton, 6, buttonRowColumnNumber)
        buttonColumnWidths.append(self.layout.itemAtPosition(6, buttonRowColumnNumber).sizeHint().width()) 

        # Make all columns of the grid layout the same width as the button column
        buttonColumnWidth = max(buttonColumnWidths)
        for columnNumber in range(0, buttonRowColumnNumber):
            self.layout.setColumnMinimumWidth(columnNumber, buttonColumnWidth)

        self.resize(self.sizeHint())

    def setHideNewspapers(self, checked):
        prefs['hideNewspapers'] = checked
        self.model.setFilterBooksThatAreNewspapers(checked)
        self.resizeAllLibraryViewLinesToHeaderHeight()

    def setHideBooksAlreadyInLibrary(self, checked):
        prefs['hideBooksAlreadyInLibrary'] = checked
        self.model.setFilterBooksThatAreAlreadyInLibrary(checked)
        self.resizeAllLibraryViewLinesToHeaderHeight()

    def about(self):
        text = get_resources('about.txt')
        QMessageBox.about(self, 'About the OPDS Client plugin', text.decode('utf-8'))

    def download_opds(self):
        self.model.downloadOpds(prefs['opds_url'])
        self.library_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.library_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.library_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.resizeAllLibraryViewLinesToHeaderHeight()
        self.resize(self.sizeHint())

    def config(self):
        self.do_user_config(parent=self)
        self.opds_url.setText(prefs['opds_url'])

    def downloadSelectedBooks(self):
        selectionmodel = self.library_view.selectionModel()
        if selectionmodel.hasSelection():
            rows = selectionmodel.selectedRows()
            for row in reversed(rows):
                book = row.data(Qt.UserRole)
                self.downloadBook(book)

    def downloadBook(self, book):
        title = book.title
        if len(book.links) > 0:
            print "Downloading: %s" % title
            self.gui.download_ebook(book.links[0])

    def dummy_books(self):
        dummy_author = ' ' * 40
        dummy_title = ' ' * 60
        books_list = []
        for line in range (1, 10):
            book = DynamicBook()
            book.author = dummy_author
            book.title = dummy_title
            book.updated = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')
            book.id = ''
            books_list.append(book)
        return books_list

    def resizeAllLibraryViewLinesToHeaderHeight(self):
        rowHeight = self.library_view.horizontalHeader().height()
        for rowNumber in range (0, self.library_view.model().rowCount(None)):
            self.library_view.setRowHeight(rowNumber, rowHeight)
