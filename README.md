# Calibre OPDS Client

[![build](https://github.com/goodlibs/calibre-opds-client/workflows/build/badge.svg)](https://github.com/goodlibs/calibre-opds-client/actions?query=workflow%3Abuild)  [![Code Style: Black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/python/black)

Download books from an OPDS catalog using a Calibre plugin.

## :books: Background

[Calibre](https://calibre-ebook.com) is a cross-platform open-source suite of e-book software.
Calibre supports organizing existing e-books into virtual libraries, displaying, editing, creating and converting e-books, as well as syncing e-books with a variety of e-readers.

The [Open Publication Distribution System](https://en.wikipedia.org/wiki/Open_Publication_Distribution_System) (OPDS) catalog format is a syndication format for electronic publications based on Atom and HTTP.
OPDS catalogs enable the aggregation, distribution, discovery, and acquisition of electronic publications.

The **Calibre OPDS Client** is a Calibre plugin that reads from an OPDS server and downloads the contents to a Calibre library.

## :hammer_and_wrench: Installation

Requires git and calibre installed:

  - Clone the repository:
    
    ``` example
    git clone https://github.com/steinarb/opds-reader.git
    ```

  - Install the plugin in calibre
    
    ``` example
    cd opds-reader/calibre_plugin/
    calibre-customize -b .
    ```

  - Start calibre (if calibre was already running, stop calibre and
    start it again)

  - Click the button "Preferences"

  - In the dialog "calibre - Preferences":
    
      - Under "Interface", click on the button "Toolbar"
      - In the dialog "calibre - Preferences - Toolbar":
          - In the dropdown, select "The main toolbar"
          - In "Available actions" scroll down to find "OPDS Client" and
            select it
          - Click the top arrow button (arrow pointing right)
          - Click the "Apply" button
      - Click the "Close" button

## :computer: Usage

I made this tool to backup my book collection between two PCs in my home
LAN, and that is the procedure I will document here:

1.  In the calibre you wish to copy from (in this example called
    calibre1.home.lan):
    1.  Click Preferences
    2.  In the "calibre - Preferences" dialog:
        1.  Click "Sharing over the net"
        2.  In the "calibre - Preferences - Sharing over the net"
            dialog:
            1.  Click the "Start Server" button
            2.  Select the checkbox "Run server automatically when
                calibre starts"
            3.  Click the "Apply" button
        3.  Click the "close" button
2.  In the calibre you wish to copy to
    1.  Install this plugin (see the "How do I install it?" section)
    2.  Click the "OPDS client" button
    3.  In the "OPDS client" dialog
        1.  Edit the "OPDS URL" value, change
            
            ``` example
            http://localhost:8080/opds
            ```
            
            to
            
            ``` example
            http://calibre1.home.lan:8080/opds
            ```
            
            and then press the RETURN key on the keyboard
        
        2.  Click the "Download OPDS" button
        
        3.  Wait until the OPDS feed has finished loading (this may take
            some time if there is a large number of books to load)
            
              - Note: if no books appear, try unchecking the "Hide books
                already in the library" checkbox. If that makes a lot of
                books appear, it means that the two calibre instances
                have the same books
        
        4.  select the books you wish to copy into the current calibre
            and click the "Download selected books"
            
              - calibre will start downloading and installing the books:
                  - The Jobs counter in calibre's lower right corner,
                    will show a decrementing number and the icon will
                    spin
                  - The book list will be updated as the books are
                    downloaded
        
        5.  The downloaded books will be in approximately the same order
            as in the original, but the time stamp will be the download
            time. To fix the time stamp, click on the "Fix timestamps of
            the selection" button
            
              - The updated timestamps may not show up immediatly, but
                they will show up after the first update of the display,
                and the books will be ordered according to the timestamp
                after stopping and starting calibre

## :balance_scale: License

This code is licensed under the GNU General Public License v3.0.
For more details, please take a look at the [LICENSE](https://github.com/goodlibs/calibre-opds-client/blob/master/LICENSE) file.

## :handshake: Contributing

Contributions are welcome!
Please feel free to open an issue or submit a pull request.

## TODO

- Read OPDS feeds other than calibre

  - \<2015-09-18 fr 19:01\> Some examples
      - feedbooks:
        
        ``` example
        http://www.feedbooks.com/books/top.atom?category=FBFIC028000&lang=en
        ```
        
        or
        
        ``` example
        http://www.feedbooks.com/catalog.atom
        ```
    
      - Internet archive:
        
        ``` example
        http://bookserver.archive.org/catalog/
        ```
    
      - Pragmatic bookshelf:
        
        ``` example
        http://pragprog.com/magazines.opds
        ```
    
      - ManyBooks:
        
        ``` example
        http://www.manybooks.net/opds/index.php
        ```
    
      - Project Gutenberg:
        
        ``` example
        http://m.gutenberg.org/ebooks/?format=opds
        ```
    
      - O'Reilly:
        
        ``` example
        http://opds.oreilly.com/opds/
        ```
    
      - Baen ebooks:
        
        ``` example
        http://www.baenebooks.com/stanza.aspx
        ```

- Add auto discovery of calibre instances in the LAN

  - \<2015-09-06 søn 11:49\> Perhaps use the Bonjour protocol? (is this
    what FBReaderJ uses?)

- Find out why the OPDS reader dialog sometimes disappear after downloading the OPDS

- Add username/password information to saved opds<sub>url</sub> values

- Migrate own code from underscore separation to camelCase (Python has a camelCase modula/pascal feel to it)

- Find out why some books (in PDF…?) aren't downloaded

- Explore the documentation format to see if it is relevant to this plugin

- Try to keep the line length correct during intermediate model updates

  - \<2015-09-06 søn 16:10\> When updating the book list model after
    each OPDS chunk, the line heights are wrong
      - They are corrected after the final read but they look a bit
        silly during the intermediate chunks

- Get better matching with existing books (the "Maven cookbook" was already present, but it still showed up)

- Remove all leftover debug trace

- Copy read marks in calibre's reader from the remote

- Refresh the list as books are downloaded (suppress downloaded books from the list)

- Add cover thumbnails to the list of books

- Add an exclusion list (a list of books that should be permanently hidden from the comparison)
