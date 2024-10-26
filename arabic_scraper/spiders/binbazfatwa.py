import scrapy
import configparser
import os

from arabic_scraper.items import FatwaItem

class BinbazFatwaSpider(scrapy.Spider):
    name = 'binbaz_fatwa'
    allowed_domains = ['binbaz.org.sa']
    start_urls = ['https://binbaz.org.sa/fatwas/kind/1']

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': os.path.join('data', 'spiders', 'binbaz_fatwa.csv'),
        'FEED_EXPORT_ENCODING': 'utf-8',
        'CSV_EXPORT_HEADERS': False,
    }
    
    
    def parse(self, response):
        print("Parsing:", response.url)  # Add this line to track parsing of articles
        
        for href in response.css('article.box__body__element.fatwa h1 a::attr(href)').getall():
            yield response.follow(href, self.parse_fatwa)

        next_page_url = response.css('ul.pagination li a[rel="next"]::attr(href)').get()
        if next_page_url is not None:
            yield response.follow(next_page_url, self.parse)

    def parse_fatwa(self, response):
        print("Parsing article:", response.url)  # Add this line to track parsing of articles
        
        item = FatwaItem()
        question = " ".join(response.css('h2.article-title__question div::text').getall()).strip()
        answer = " ".join(response.css('div.article-content *::text').getall()).strip()
        item['content'] = f"Question: {question}\nAnswer: {answer}"
        item['title'] = response.css('h1.article-title.article-title--primary::text').get().strip()
        item["author"] = "Abdul-Aziz ibn Baz"

        # include the link to the article
        item["link"] = response.url
        item["filter"] = "fatwa"
        
        yield item