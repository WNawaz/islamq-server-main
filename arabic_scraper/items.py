# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArabicScrapperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class FatwaItem(scrapy.Item):
    content = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    link = scrapy.Field()
    filter = scrapy.Field()


class ArticleItem(scrapy.Item):
    content = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    link = scrapy.Field()
    filter = scrapy.Field()

class DiscussionItem(scrapy.Item):
    content = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    link = scrapy.Field()
    filter = scrapy.Field()

class AlBadarArticleItem(scrapy.Item):
    content = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    link = scrapy.Field()
    filter = scrapy.Field()

class AlBadarArticleItemRamadan(scrapy.Item):
    content = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    link = scrapy.Field()
    filter = scrapy.Field()

class AlBadarArticleItemHajj(scrapy.Item):
    content = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    link = scrapy.Field()
    filter = scrapy.Field()

class AlBadarArticleItemTrace(scrapy.Item):
    content = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    link = scrapy.Field()
    filter = scrapy.Field()

class AlBadarArticleItemBrief(scrapy.Item):
    content = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    link = scrapy.Field()
    filter = scrapy.Field()