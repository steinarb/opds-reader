"""main.py: A GUI to download an OPDS feed, filter out parts of the results, and download selected books from the feed into the local library"""

__author__    = "Steinar Bang"
__copyright__ = "Steinar Bang, 2015-2021"
__credits__   = ["Steinar Bang"]
__license__   = "GPL v3"

import sys
import datetime
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QStringListModel
from PyQt6.QtWidgets import QDialog, QGridLayout, QLineEdit, QComboBox, QPushButton, QCheckBox, QMessageBox, QLabel, QAbstractItemView, QTableView, QHeaderView

from calibre_plugins.opds_client.model import OpdsBooksModel
from calibre_plugins.opds_client.config import prefs
from calibre_plugins.opds_client import config
from calibre.ebooks.metadata.book.base import Metadata


class DynamicBook(dict):
    pass

class OpdsDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        self.db = gui.current_db.new_api

        # The model for the book list
        self.model = OpdsBooksModel(None, self.dummy_books(), self.db)
        self.searchproxymodel = QSortFilterProxyModel(self)
        self.searchproxymodel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.searchproxymodel.setFilterKeyColumn(-1)
        self.searchproxymodel.setSourceModel(self.model)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.setWindowTitle('OPDS Client')
        self.setWindowIcon(icon)

        labelColumnWidths = []

        self.opdsUrlLabel = QLabel('OPDS URL: ')
        self.layout.addWidget(self.opdsUrlLabel, 0, 0)
        labelColumnWidths.append(self.layout.itemAtPosition(0, 0).sizeHint().width())

        config.convertSingleStringOpdsUrlPreferenceToListOfStringsPreference()
        self.opdsUrlEditor = QComboBox(self)
        self.opdsUrlEditor.activated.connect(self.opdsUrlEditorActivated)
        self.opdsUrlEditor.addItems(prefs['opds_url'])
        self.opdsUrlEditor.setEditable(True)
        self.opdsUrlEditor.setInsertPolicy(QComboBox.InsertAtTop)
        self.layout.addWidget(self.opdsUrlEditor, 0, 1, 1, 3)
        self.opdsUrlLabel.setBuddy(self.opdsUrlEditor)

        buttonColumnNumber = 7
        buttonColumnWidths = []
        self.about_button = QPushButton('About', self)
        self.about_button.setAutoDefault(False)
        self.about_button.clicked.connect(self.about)
        self.layout.addWidget(self.about_button, 0, buttonColumnNumber)
        buttonColumnWidths.append(self.layout.itemAtPosition(0, buttonColumnNumber).sizeHint().width()) 

        # Initially download the catalogs found in the root catalog of the URL
        # selected at startup.  Fail quietly on failing to open the URL
        catalogsTuple = self.model.downloadOpdsRootCatalog(self.gui, self.opdsUrlEditor.currentText(), False)
        print(catalogsTuple)
        firstCatalogTitle = catalogsTuple[0]
        self.currentOpdsCatalogs = catalogsTuple[1] # A dictionary of title->feedURL

        self.opdsCatalogSelectorLabel = QLabel('OPDS Catalog:')
        self.layout.addWidget(self.opdsCatalogSelectorLabel, 1, 0)
        labelColumnWidths.append(self.layout.itemAtPosition(1, 0).sizeHint().width())

        self.opdsCatalogSelector = QComboBox(self)
        self.opdsCatalogSelector.setEditable(False)
        self.opdsCatalogSelectorModel = QStringListModel(self.currentOpdsCatalogs.keys())
        self.opdsCatalogSelector.setModel(self.opdsCatalogSelectorModel)
        self.opdsCatalogSelector.setCurrentText(firstCatalogTitle)
        self.layout.addWidget(self.opdsCatalogSelector, 1, 1, 1, 3)

        self.download_opds_button = QPushButton('Download OPDS', self)
        self.download_opds_button.setAutoDefault(False)
        self.download_opds_button.clicked.connect(self.download_opds)
        self.layout.addWidget(self.download_opds_button, 1, buttonColumnNumber)
        buttonColumnWidths.append(self.layout.itemAtPosition(1, buttonColumnNumber).sizeHint().width()) 

        # Search GUI
        self.searchEditor = QLineEdit(self)
        self.searchEditor.returnPressed.connect(self.searchBookList)
        self.layout.addWidget(self.searchEditor, 2, buttonColumnNumber - 2, 1, 2)

        self.searchButton = QPushButton('Search', self)
        self.searchButton.setAutoDefault(False)
        self.searchButton.clicked.connect(self.searchBookList)
        self.layout.addWidget(self.searchButton, 2, buttonColumnNumber)
        buttonColumnWidths.append(self.layout.itemAtPosition(2, buttonColumnNumber).sizeHint().width())

        # The main book list
        self.library_view = QTableView(self)
        self.library_view.setAlternatingRowColors(True)
        self.library_view.setModel(self.searchproxymodel)
        self.library_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.library_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.library_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.library_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resizeAllLibraryViewLinesToHeaderHeight()
        self.library_view.resizeColumnsToContents()
        self.layout.addWidget(self.library_view, 3, 0, 3, buttonColumnNumber + 1)

        self.hideNewsCheckbox = QCheckBox('Hide Newspapers', self)
        self.hideNewsCheckbox.clicked.connect(self.setHideNewspapers)
        self.hideNewsCheckbox.setChecked(prefs['hideNewspapers'])
        self.layout.addWidget(self.hideNewsCheckbox, 6, 0, 1, 3)

        self.hideBooksAlreadyInLibraryCheckbox = QCheckBox('Hide books already in library', self)
        self.hideBooksAlreadyInLibraryCheckbox.clicked.connect(self.setHideBooksAlreadyInLibrary)
        self.hideBooksAlreadyInLibraryCheckbox.setChecked(prefs['hideBooksAlreadyInLibrary'])
        self.layout.addWidget(self.hideBooksAlreadyInLibraryCheckbox, 7, 0, 1, 3)

        # Let the checkbox initial state control the filtering
        self.model.setFilterBooksThatAreNewspapers(self.hideNewsCheckbox.isChecked())
        self.model.setFilterBooksThatAreAlreadyInLibrary(self.hideBooksAlreadyInLibraryCheckbox.isChecked())

        self.downloadButton = QPushButton('Download selected books', self)
        self.downloadButton.setAutoDefault(False)
        self.downloadButton.clicked.connect(self.downloadSelectedBooks)
        self.layout.addWidget(self.downloadButton, 6, buttonColumnNumber)
        buttonColumnWidths.append(self.layout.itemAtPosition(6, buttonColumnNumber).sizeHint().width()) 

        self.fixTimestampButton = QPushButton('Fix timestamps of selection', self)
        self.fixTimestampButton.setAutoDefault(False)
        self.fixTimestampButton.clicked.connect(self.fixBookTimestamps)
        self.layout.addWidget(self.fixTimestampButton, 7, buttonColumnNumber)
        buttonColumnWidths.append(self.layout.itemAtPosition(7, buttonColumnNumber).sizeHint().width()) 

        # Make all columns of the grid layout the same width as the button column
        buttonColumnWidth = max(buttonColumnWidths)
        for columnNumber in range(0, buttonColumnNumber):
            self.layout.setColumnMinimumWidth(columnNumber, buttonColumnWidth)

        # Make sure the first column isn't wider than the labels it holds
        labelColumnWidth = max(labelColumnWidths)
        self.layout.setColumnMinimumWidth(0, labelColumnWidth)

        self.resize(self.sizeHint())

    def opdsUrlEditorActivated(self, text):
        prefs['opds_url'] = config.saveOpdsUrlCombobox(self.opdsUrlEditor)
        catalogsTuple = self.model.downloadOpdsRootCatalog(self.gui, self.opdsUrlEditor.currentText(), True)
        firstCatalogTitle = catalogsTuple[0]
        self.currentOpdsCatalogs = catalogsTuple[1] # A dictionary of title->feedURL
        self.opdsCatalogSelectorModel.setStringList(self.currentOpdsCatalogs.keys())
        self.opdsCatalogSelector.setCurrentText(firstCatalogTitle)

    def setHideNewspapers(self, checked):
        prefs['hideNewspapers'] = checked
        self.model.setFilterBooksThatAreNewspapers(checked)
        self.resizeAllLibraryViewLinesToHeaderHeight()

    def setHideBooksAlreadyInLibrary(self, checked):
        prefs['hideBooksAlreadyInLibrary'] = checked
        self.model.setFilterBooksThatAreAlreadyInLibrary(checked)
        self.resizeAllLibraryViewLinesToHeaderHeight()

    def searchBookList(self):
        searchString = self.searchEditor.text()
        print("starting book list search for: %s" % searchString)
        self.searchproxymodel.setFilterFixedString(searchString)

    def about(self):
        text = get_resources('about.txt')
        QMessageBox.about(self, 'About the OPDS Client plugin', text.decode('utf-8'))

    def download_opds(self):
        opdsCatalogUrl = self.currentOpdsCatalogs.get(self.opdsCatalogSelector.currentText(), None)
        if opdsCatalogUrl is None:
            # Just give up quietly
            return
        self.model.downloadOpdsCatalog(self.gui, opdsCatalogUrl)
        if self.model.isCalibreOpdsServer():
            self.model.downloadMetadataUsingCalibreRestApi(self.opdsUrlEditor.currentText())
        self.library_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.library_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.library_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.resizeAllLibraryViewLinesToHeaderHeight()
        self.resize(self.sizeHint())

    def config(self):
        self.do_user_config(parent=self)

    def downloadSelectedBooks(self):
        selectionmodel = self.library_view.selectionModel()
        if selectionmodel.hasSelection():
            rows = selectionmodel.selectedRows()
            for row in reversed(rows):
                book = row.data(Qt.UserRole)
                self.downloadBook(book)

    def downloadBook(self, book):
        if len(book.links) > 0:
            self.gui.download_ebook(book.links[0])

    def fixBookTimestamps(self):
        selectionmodel = self.library_view.selectionModel()
        if selectionmodel.hasSelection():
            rows = selectionmodel.selectedRows()
            for row in reversed(rows):
                book = row.data(Qt.UserRole)
                self.fixBookTimestamp(book)

    def fixBookTimestamp(self, book):
        bookTimestamp = book.timestamp
        identicalBookIds = self.findIdenticalBooksForBooksWithMultipleAuthors(book)
        bookIdToValMap = {}
        for identicalBookId in identicalBookIds:
            bookIdToValMap[identicalBookId] = bookTimestamp
        if len(bookIdToValMap) < 1:
            print("Failed to set timestamp of book: %s" % book)
        self.db.set_field('timestamp', bookIdToValMap)

    def findIdenticalBooksForBooksWithMultipleAuthors(self, book):
        authorsList = book.authors
        if len(authorsList) < 2:
            return self.db.find_identical_books(book)
        # Try matching the authors one by one
        identicalBookIds = set()
        for author in authorsList:
            singleAuthorBook = Metadata(book.title, [author])
            singleAuthorIdenticalBookIds = self.db.find_identical_books(singleAuthorBook)
            identicalBookIds = identicalBookIds.union(singleAuthorIdenticalBookIds)
        return identicalBookIds

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
        for rowNumber in range (0, self.library_view.model().rowCount()):
            self.library_view.setRowHeight(rowNumber, rowHeight)
