import scrapy
import configparser  # Module for parsing config files
import os

from arabic_scraper.items import AlBadarArticleItemRamadan

class AlBadrArticlesSpiderRamadan(scrapy.Spider):
    name = 'al_badr_articles_ramadan'
    allowed_domains = ['al-badr.net']
    start_urls = ['https://al-badr.net/muqolats/2']


    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': os.path.join('data', 'spiders', 'albadr_data_ramadan.csv'),
        'FEED_EXPORT_ENCODING': 'utf-8',
        'CSV_EXPORT_HEADERS': False,
    }
    

    def parse(self, response):
        print("Parsing:", response.url)  # Add this line to track parsing of articles
        
        # Extracting the URLs of the articles
        for article in response.css('div.post-content ul li a'):
            url = response.urljoin(article.attrib['href'])
            yield scrapy.Request(url, callback=self.parse_article)

        # Handling pagination
        next_page_partial_url = response.css('div.pager a::attr(href)').re(r'(?<=page=)\d+')
        if next_page_partial_url:
            next_page_number = int(next_page_partial_url[-1])
            next_page_url = f"https://al-badr.net/muqolats/2/?q=&page={next_page_number}"
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_article(self, response):
        # Extracting the title and content of the article
        print("Parsing article:", response.url)  # Add this line to track parsing of articles
        
        item = AlBadarArticleItemRamadan()
        item['content'] = ' '.join(response.css('div.cat-content article *::text').getall())
        item['title'] = response.css('h2.post-title-center::text').get()
        item["author"] = "Abd al-Razzaq al-Badr"
        item["link"] = response.url
        item["filter"] = "ramadan"
        yield item