import scrapy
import configparser
import os

from arabic_scraper.items import ArticleItem

class BinbazArticleSpider(scrapy.Spider):
    name = 'binbaz_article'
    allowed_domains = ['binbaz.org.sa']
    start_urls = ['https://binbaz.org.sa/articles']
    
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': os.path.join('data', 'spiders', 'binbaz_articles.csv'),
        'FEED_EXPORT_ENCODING': 'utf-8',
        'CSV_EXPORT_HEADERS': False,
    }
    
    
    def parse(self, response):
        print("Parsing:", response.url)  # Add this line to track parsing of articles
        
        # Extract the links to the individual article pages
        for href in response.css('article.box__body__element.article h3 a::attr(href)').getall():
            yield response.follow(href, self.parse_article)

        # Follow the link to the next page
        next_page_url = response.css('div.box__footer.text-center ul.pagination li a[rel="next"]::attr(href)').get()
        if next_page_url is not None:
            yield response.follow(next_page_url, self.parse)

    def parse_article(self, response):
        print("Parsing article:", response.url)  # Add this line to track parsing of articles
        
    # Extract the title of the article
        item = ArticleItem()

    # Extracting all text nodes within the 'div.article-content' and joining them
        content_list = response.css('div.article-content *::text').getall()
        item['content'] = ' '.join(content.strip() for content in content_list)
        item['title'] = response.css('h1.article-title.article-title--primary::text').get().strip()
        item["author"] = "Abdul-Aziz ibn Baz"
        # include the link to the article
        item["link"] = response.url
        item["filter"] = "article"

        
        yield item
