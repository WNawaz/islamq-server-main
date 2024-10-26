import scrapy
import configparser
import os

from arabic_scraper.items import DiscussionItem

class BinbazDiscussionSpider(scrapy.Spider):
    name = 'binbaz_encounters'
    allowed_domains = ['binbaz.org.sa']
    start_urls = ['https://binbaz.org.sa/discussions']
    
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': os.path.join('data', 'spiders', 'binbaz_discussions.csv'),
        'FEED_EXPORT_ENCODING': 'utf-8',
        'CSV_EXPORT_HEADERS': False,
    }
    
    
    def parse(self, response):
        print("Parsing:", response.url)  # Add this line to track parsing of articles
        
        # Extract the links to the individual discussion pages
        for href in response.css('article.box__body__element.discussion h3 a::attr(href)').extract():
            yield response.follow(href, self.parse_discussion)

        # Pagination
        next_page_url = response.css('div.box__footer.text-center ul.pagination li a[rel="next"]::attr(href)').get()
        if next_page_url:
            yield response.follow(next_page_url, self.parse)

    def parse_discussion(self, response):
        print("Parsing article:", response.url)  # Add this line to track parsing of articles
        
        # Extract the title and content of the discussion
        item = DiscussionItem()

        # Extracting all text nodes within the 'div.article-content' and joining them
        content_list = response.css('div.article-content *::text').extract()
        item['content'] = ' '.join(content.strip() for content in content_list)
        item['title'] = response.css('h1.article-title.article-title--primary::text').get().strip()
        item["author"] = "Abdul-Aziz ibn Baz"


        # include the link to the article
        item["link"] = response.url
        item["filter"] = "encounters"
        
        yield item