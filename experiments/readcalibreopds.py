import feedparser

calibre_url = "http://localhost:8080/opds"

feed = feedparser.parse(calibre_url)

print feed.keys()
newest_url = feed['entries'][0]['links'][0]['href']

newest_feed = feedparser.parse(newest_url)

print newest_feed['entries'][5]['links']
