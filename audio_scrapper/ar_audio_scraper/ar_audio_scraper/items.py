# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArAudioScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AlharmainAudio(scrapy.Item):
    title  = scrapy.Field()
    audio_links = scrapy.Field()