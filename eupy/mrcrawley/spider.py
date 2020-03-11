#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
from scrapy.crawler import CrawlerProcess
import logging, sys, os
from eupy.native import logger as l

class AZLyricsSpider(scrapy.Spider):

    name = 'AZSpider'
    start_urls = []
    custom_settings = {
                        'CONCURRENT_REQUESTS': 1,
                        'DOWNLOAD_DELAY': 3
                        }

    def __init__(self, urls):
        self.start_urls = urls
        self.__excl_str = "<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->"
        self.logger.setLevel(logging.INFO)
        return

    ### Parsing Methods
    def parse(self, response):
        print("AA")
        LINK_SELECTOR = 'div.listalbum-item'
        for song in response.css(LINK_SELECTOR):
            song_page = song.css('::attr(href)').extract_first()
            yield scrapy.Request(response.urljoin(song_page), 
                                callback=self._parse_song)

    def _parse_song(self, response):
        lyrics, artist, title = "", "", ""
        LYRIC_SELECTOR = 'div:not([class])'
        TITLE_SELECTOR = '//script[@type=\'text/javascript\']'
        
        for div in response.css(LYRIC_SELECTOR):
            lyrics = self.__parse_lyrics(div.get())

        for script in response.xpath(TITLE_SELECTOR):
            artist, title = self.__parse_artist_title(script.xpath("text()").get())
            if artist != "" and title != "":
                break
        self.__logAndStore({'artist': artist, 'title': title, 'lyrics': lyrics})
        return

    def __parse_lyrics(self, division) -> list:
        divList = division.replace("\r", "").replace("<i>", "").replace("</i>", "").replace("<br>", "").split('\n')
        assert '<div>' == divList[0] and '</div>' == divList[-1] and self.__excl_str == divList[1], "Wrong lyric format"
        return divList[2:-1]

    def __parse_artist_title(self, script) -> str:
        artist, title = "", ""
        for l in script.split('\n'):
            try:
                if "SongName" in l:
                    title = l.split('\"')[1]
                elif "ArtistName" in l:
                    artist = l.split('\"')[1]
            except IndexError:
                assert False, "Parsing title and artist failed"
        assert title != "" and artist != "", "Title and/or artist fields are empty"
        return artist, title

    def __logAndStore(self, song):
        self.logger.info("\n\n{} - {}\n{}\n".format(song['artist'],
                                                song['title'], 
                                                "\n".join(song['lyrics'])))
        global _data
        _data.append(song)
        return

_data = []

"""
Return raw Data in list
"""
def getData():
    return _data

"""
Return formatted data to str, ready to be written in file
"""
def getDataStr():
    return ["{}\n{}\n\n{}".format(x['artist'], x['title'], "\n".join(x['lyrics']))
                for x in _data]

"""
Directrory of existing spiders for artists.
Sample URLS
-----------
'https://www.azlyrics.com/p/pinkfloyd.html'
"""
ARTIST_MAP = {
                'pink_floyd': "https://www.azlyrics.com/p/pinkfloyd.html"
            }

def getAvailArtists():
    return [x for x in ARTIST_MAP]
    
"""
Interface method for AZ Spider

artist: string value of requested artist for crawling
path: target path to write files
"""
def crawl(artist):
    if artist not in ARTIST_MAP:
        raise ValueError("{} not available for crawling".format(artist))
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(AZLyricsSpider, "https://www.azlyrics.com/p/pinkfloyd.html")
    process.start() # the script will block here until the crawling is finished
    return
