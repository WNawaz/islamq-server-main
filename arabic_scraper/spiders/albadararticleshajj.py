import scrapy
import configparser
import os

from arabic_scraper.items import AlBadarArticleItemHajj

class AlbadarHajjArticlesSpider(scrapy.Spider):
    name = 'al_badr_articles_hajj'
    allowed_domains = ['al-badr.net']
    start_urls = ['https://al-badr.net/muqolats/3']

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': os.path.join('data', 'spiders', 'albadr_data_hajj.csv'),
        'FEED_EXPORT_ENCODING': 'utf-8',
        'CSV_EXPORT_HEADERS': False,
    }
    
    
    def parse(self, response):
        print("Parsing:", response.url)  # Add this line to track parsing of articles
        
        # Extracting the URLs of the articles
        for article in response.css('div.post-content ul li a'):
            url = response.urljoin(article.attrib['href'])
            yield scrapy.Request(url, callback=self.parse_article)


    def parse_article(self, response):
        print("Parsing article:", response.url)  # Add this line to track parsing of articles
        
        # Extracting the title and content of the article
        item = AlBadarArticleItemHajj()
        item['content'] = ' '.join(response.css('div.cat-content article *::text').getall())
        item['title'] = response.css('h2.post-title-center::text').get()
        item["author"] = "Abd al-Razzaq al-Badr"
        item["link"] = response.url
        item["filter"] = "hajj"
        
        yield item