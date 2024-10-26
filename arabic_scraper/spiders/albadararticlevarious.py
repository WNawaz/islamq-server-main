import scrapy
import configparser
import os

from arabic_scraper.items import AlBadarArticleItem

class AlBadrArticlesSpider(scrapy.Spider):
    name = 'al_badr_articles_various'
    allowed_domains = ['al-badr.net']
    start_urls = ['https://al-badr.net/muqolats/1']

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': os.path.join('data', 'spiders', 'albadr_articles_various.csv'),
        'FEED_EXPORT_ENCODING': 'utf-8',
        'CSV_EXPORT_HEADERS': False,
    }
    
    
    def parse(self, response):
        print("Parsing:", response.url)  # Add this line to track parsing of articles
        
        # Extracting the URLs of the articles
        for article in response.css('div.post-content ul li a'):
            url = response.urljoin(article.attrib['href'])
            yield scrapy.Request(url, callback=self.parse_article)

        # Following the pagination links
        next_page_url = response.css('div.pager a::attr(href)').extract()[-2]
        if next_page_url:
            next_page_url = response.urljoin(next_page_url)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_article(self, response):
        print("Parsing article:", response.url)  # Add this line to track parsing of articles
        
        item = AlBadarArticleItem()
        item['content'] = ' '.join(response.css('div.cat-content article *::text').getall())
        item['title'] = response.css('h2.post-title-center::text').get()
        item["author"] = "Abd al-Razzaq al-Badr"
        item["link"] = response.url
        item["filter"] = "various"        
        yield item

