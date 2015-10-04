import feedparser

calibre_url = "http://localhost:8080/opds"

feed = feedparser.parse(calibre_url)

"""main.py: Experimental code using feedparser on OPDS feeds from calibre"""

__author__    = "Steinar Bang"
__copyright__ = "Steinar Bang, 2015"
__credits__   = ["Steinar Bang"]
__license__   = "GPL v3"

print feed
newest_url = feed.entries[0].links[0].href
authors_url = feed.entries[2].links[0].href

#authors_feed = feedparser.parse(authors_url)
newest_feed = feedparser.parse(newest_url)

#print newest_feed.keys()
#newest_feed_feed_links = newest_feed.feed.links
#print newest_feed_feed_links
#next_link = newest_feed_feed_links[len(newest_feed_feed_links) - 1]
#print next_link
#print newest_feed.entries[9].keys()
#print newest_feed.entries[8]
#print newest_feed.entries[0].links

#print newest_feed
#print authors_feed
