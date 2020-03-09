#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import logging, sys, os
# import lazytools

class AZLyricsSpider(scrapy.Spider):

    name = 'AZSpider'
    start_urls = []
    custom_settings = {
                        'CONCURRENT_REQUESTS': 1,
                        'DOWNLOAD_DELAY': 3
                        }

    def __init__(self, urls, path=None):
        self.start_urls = urls
        self.songs = []
        self.base_path = path
        self.__excl_str = "<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->"
        self.logger.setLevel(logging.DEBUG)
        return

    ### Parsing Methods
    def parse(self, response):
        LINK_SELECTOR = 'div.listalbum-item'
        for song in response.css(LINK_SELECTOR):
            song_page = song.css('::attr(href)').extract_first()
            yield scrapy.Request(response.urljoin(song_page), 
                                callback=self.parse_song)

    def parse_song(self, response):
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
        self.songs.append(song)
        if self.base_path:
            self.__writeFile(song)
        return

    def __writeFile(self, song):

        if not os.isdir(self.base_path):
            os.mkdirs(self.base_path)
        with open("{}/{}.txt".format(self.base_path, song['title'].replace(" ", "_")), 'w') as f:
            f.write("{}\n{}\n\n{}".format(song['artist'],
                                                 song['title'], 
                                                 "\n".join(song['lyrics'])))
        return
