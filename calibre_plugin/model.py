"""model.py: This is a QAbstractTableModel that holds a list of Metadata objects created from books in an OPDS feed"""

__author__    = "Steinar Bang"
__copyright__ = "Steinar Bang, 2015-2022"
__credits__   = ["Steinar Bang"]
__license__   = "GPL v3"

import datetime
from PyQt5.Qt import Qt, QAbstractTableModel, QCoreApplication
from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import error_dialog
from calibre.web.feeds import feedparser
import urllib.parse
import urllib.request
import json
import re


class OpdsBooksModel(QAbstractTableModel):
    column_headers = [_('Title'), _('Author(s)'), _('Updated')]
    booktableColumnCount = 3
    filterBooksThatAreNewspapers = False
    filterBooksThatAreAlreadyInLibrary = False

    def __init__(self, parent, books = [], db = None):
        QAbstractTableModel.__init__(self, parent)
        self.db = db
        self.books = self.makeMetadataFromParsedOpds(books)
        self.filterBooks()

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Vertical:
            return section + 1
        if section >= len(self.column_headers):
            return None
        return self.column_headers[section]

    def rowCount(self, parent):
        return len(self.filteredBooks)

    def columnCount(self, parent):
        return self.booktableColumnCount

    def data(self, index, role):
        row, col = index.row(), index.column()
        if row >= len(self.filteredBooks):
            return None
        opdsBook = self.filteredBooks[row]
        if role == Qt.UserRole:
            # Return the Metadata object underlying each row
            return opdsBook
        if role != Qt.DisplayRole:
            return None
        if col >= self.booktableColumnCount:
            return None
        if col == 0:
            return opdsBook.title
        if col == 1:
            return u' & '.join(opdsBook.author)
        if col == 2:
            if opdsBook.timestamp is not None:
                return opdsBook.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            return opdsBook.timestamp
        return None

    def downloadOpdsRootCatalog(self, gui, opdsUrl, displayDialogOnErrors):
        feed = feedparser.parse(opdsUrl)
        if 'bozo_exception' in feed:
            exception = feed['bozo_exception']
            message = 'Failed opening the OPDS URL ' + opdsUrl + ': '
            reason = ''
            if hasattr(exception, 'reason') :
                reason = str(exception.reason)
            error_dialog(gui, _('Failed opening the OPDS URL'), message, reason, displayDialogOnErrors)
            return (None, {})
        self.serverHeader = feed.headers['server']
        print("serverHeader: %s" % self.serverHeader)
        print("feed.entries: %s" % feed.entries)
        catalogEntries = {}
        firstTitle = None
        for entry in feed.entries:
            title = entry.get('title', 'No title')
            if firstTitle is None:
                firstTitle = title
            links = entry.get('links', [])
            firstLink = next(iter(links), None)
            if firstLink is not None:
                print("firstLink: %s" % firstLink)
                catalogEntries[title] = firstLink.href
        return (firstTitle, catalogEntries)

    def downloadOpdsCatalog(self, gui, opdsCatalogUrl):
        print("downloading catalog: %s" % opdsCatalogUrl)
        opdsCatalogFeed = feedparser.parse(opdsCatalogUrl)
        self.books = self.makeMetadataFromParsedOpds(opdsCatalogFeed.entries)
        self.filterBooks()
        QCoreApplication.processEvents()
        nextUrl = self.findNextUrl(opdsCatalogFeed.feed)
        while nextUrl is not None:
            nextFeed = feedparser.parse(nextUrl)
            self.books = self.books + self.makeMetadataFromParsedOpds(nextFeed.entries)
            self.filterBooks()
            QCoreApplication.processEvents()
            nextUrl = self.findNextUrl(nextFeed.feed)

    def isCalibreOpdsServer(self):
        return self.serverHeader.startswith('calibre')

    def setFilterBooksThatAreAlreadyInLibrary(self, value):
        if value != self.filterBooksThatAreAlreadyInLibrary:
            self.filterBooksThatAreAlreadyInLibrary = value
            self.filterBooks()

    def setFilterBooksThatAreNewspapers(self, value):
        if value != self.filterBooksThatAreNewspapers:
            self.filterBooksThatAreNewspapers = value
            self.filterBooks()

    def filterBooks(self):
        self.beginResetModel()
        self.filteredBooks = []
        for book in self.books:
            if (not self.isFilteredNews(book)) and (not self.isFilteredAlreadyInLibrary(book)):
                self.filteredBooks.append(book)
        self.endResetModel()

    def isFilteredNews(self, book):
        if self.filterBooksThatAreNewspapers:
            if u'News' in book.tags:
                return True
        return False

    def isFilteredAlreadyInLibrary(self, book):
        if self.filterBooksThatAreAlreadyInLibrary:
            return self.db.has_book(book)
        return False

    def makeMetadataFromParsedOpds(self, books):
        metadatalist = []
        for book in books:
            metadata = self.opdsToMetadata(book)
            metadatalist.append(metadata)
        return metadatalist

    def opdsToMetadata(self, opdsBookStructure):
        authors = opdsBookStructure.author.replace(u'& ', u'&') if 'author' in opdsBookStructure else ''
        metadata = Metadata(opdsBookStructure.title, authors.split(u'&'))
        metadata.uuid = opdsBookStructure.id.replace('urn:uuid:', '', 1) if 'id' in opdsBookStructure else ''
        rawTimestamp = opdsBookStructure.updated
        parsableTimestamp = re.sub('((\.[0-9]+)?\+0[0-9]:00|Z)$', '', rawTimestamp)
        metadata.timestamp = datetime.datetime.strptime(parsableTimestamp, '%Y-%m-%dT%H:%M:%S')
        tags = []
        summary = opdsBookStructure.get(u'summary', u'')
        summarylines = summary.splitlines()
        for summaryline in summarylines:
            if summaryline.startswith(u'TAGS: '):
                tagsline = summaryline.replace(u'TAGS: ', u'')
                tagsline = tagsline.replace(u'<br />',u'')
                tagsline = tagsline.replace(u', ', u',')
                tags = tagsline.split(u',')
        metadata.tags = tags
        bookDownloadUrls = []
        links = opdsBookStructure.get('links', [])
        for link in links:
            url = link.get('href', '')
            bookType = link.get('type', '')
            # Skip covers and thumbnails
            if not bookType.startswith('image/'):
                if bookType == 'application/epub+zip':
                    # EPUB books are preferred and always put at the head of the list if found
                    bookDownloadUrls.insert(0, url)
                else:
                    # Formats other than EPUB (eg. AZW), are appended as they are found
                    bookDownloadUrls.append(url)
        metadata.links = bookDownloadUrls
        return metadata

    def findNextUrl(self, feed):
        for link in feed.links:
            if link.rel == u'next':
                return link.href
        return None

    def downloadMetadataUsingCalibreRestApi(self, opdsUrl):
        # The "updated" values on the book metadata, in the OPDS returned
        # by calibre, are unrelated to the books they are returned with:
        # the "updated" value is the same value for all books metadata,
        # and this value is the last modified date of the entire calibre
        # database.
        #
        # It is therefore necessary to use the calibre REST API to get
        # a meaningful timestamp for the books

        # Get the base of the web server, from the OPDS URL
        parsedOpdsUrl = urllib.parse.urlparse(opdsUrl)

        # GET the search URL twice: the first time is to get the total number
        # of books in the other calibre.  The second GET gets arguments
        # to retrieve all book ids in the other calibre.
        parsedCalibreRestSearchUrl = urllib.parse.ParseResult(parsedOpdsUrl.scheme, parsedOpdsUrl.netloc, '/ajax/search', '', '', '')
        calibreRestSearchUrl = parsedCalibreRestSearchUrl.geturl()
        calibreRestSearchResponse = urllib.request.urlopen(calibreRestSearchUrl)
        calibreRestSearchJsonResponse = json.load(calibreRestSearchResponse)
        getAllIdsArgument = 'num=' + str(calibreRestSearchJsonResponse['total_num']) + '&offset=0'
        parsedCalibreRestSearchUrl = urllib.parse.ParseResult(parsedOpdsUrl.scheme, parsedOpdsUrl.netloc, '/ajax/search', '', getAllIdsArgument, '').geturl()
        calibreRestSearchResponse = urllib.request.urlopen(parsedCalibreRestSearchUrl)
        calibreRestSearchJsonResponse = json.load(calibreRestSearchResponse)
        bookIds = list(map(str, calibreRestSearchJsonResponse['book_ids']))

        # Get the metadata for all books by adding the list of
        # all IDs as a GET argument
        bookIdsGetArgument = 'ids=' + ','.join(bookIds)
        parsedCalibreRestBooksUrl = urllib.parse.ParseResult(parsedOpdsUrl.scheme, parsedOpdsUrl.netloc, '/ajax/books', '', bookIdsGetArgument, '')
        calibreRestBooksResponse = urllib.request.urlopen(parsedCalibreRestBooksUrl.geturl())
        booksDictionary = json.load(calibreRestBooksResponse)
        self.updateTimestampInMetadata(bookIds, booksDictionary)

    def updateTimestampInMetadata(self, bookIds, booksDictionary):
        bookMetadataById = {}
        for bookId in bookIds:
            bookMetadata = booksDictionary[bookId]
            uuid = bookMetadata['uuid']
            bookMetadataById[uuid] = bookMetadata
        for book in self.books:
            bookMetadata = bookMetadataById[book.uuid]
            rawTimestamp = bookMetadata['timestamp']
            parsableTimestamp = re.sub('(\.[0-9]+)?\+00:00$', '', rawTimestamp)
            timestamp = datetime.datetime.strptime(parsableTimestamp, '%Y-%m-%dT%H:%M:%S')
            book.timestamp = timestamp
        self.filterBooks()
