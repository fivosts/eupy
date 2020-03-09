#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.crawler import CrawlerProcess
import spider

"""
Sample URLS
-----------
'https://www.azlyrics.com/p/pinkfloyd.html'
"""

"""
Directrory of existing spiders for artists.
"""
ARTIST_MAP = {
				'pink floyd': ("https://www.azlyrics.com/p/pinkfloyd.html", "./dataset/pink_floyd")
			}

# urls: list of starting URL to crawl
def crawlAZ(urls, path=None):
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(spider.AZLyricsSpider, urls, path)
    process.start() # the script will block here until the crawling is finished
    return

def getAvailArtists():
	return [x for x in ARTIST_MAP]