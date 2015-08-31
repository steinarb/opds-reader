from PyQt5.Qt import Qt, QAbstractTableModel

class OpdsBooksModel(QAbstractTableModel):
    column_headers = [_('Title'), _('Author(s)'), _('Updated')]
    column_keys = [u'title', u'author', u'updated']

    def __init__(self, parent, books = []):
        QAbstractTableModel.__init__(self, parent)
        self.books = books

    def rowCount(self, parent):
        return len(self.books)

    def columnCount(self, parent):
        return len(self.column_keys)

    def data(self, index, role):
        if role != Qt.DisplayRole:
            return None
        row, col = index.row(), index.column()
        if row >= len(self.books):
            return None
        opdsBook = self.books[row]
        if col >= len(self.column_keys):
            return None
        return opdsBook[self.column_keys[col - 1]]
