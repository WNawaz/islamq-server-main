import scrapy
import configparser
import os

class AlBadrSpiderSpeech(scrapy.Spider):
    name = 'al_badr_articles_speech'
    allowed_domains = ['al-badr.net']
    start_urls = ['https://al-badr.net/muqolats/7']
    
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': os.path.join('data', 'spiders', 'albadr_data_speech.csv'),
        'FEED_EXPORT_ENCODING': 'utf-8',
        'CSV_EXPORT_HEADERS': False,
    }
    
    
    def parse(self, response):
        print("Parsing:", response.url)  # Add this line to track parsing of articles
        
        # Extract article titles and URLs
        articles = response.css('div.post-content ul li a')
        for article in articles:
            url = response.urljoin(article.attrib['href'])
            yield scrapy.Request(url, callback=self.parse_article)

        # Pagination: Extract the next page link and follow it
        next_page = response.css('div.pager a::attr(href)').getall()
        next_page_url = response.urljoin(next_page[-2])  # Adjust index if needed
        yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_article(self, response):
        print("Parsing article:", response.url)  # Add this line to track parsing of articles
        
        # Extract data using CSS selectors
        title = response.css('h2.post-title-center::text').get()
        content_paragraphs = response.css('div.cat-content p::text').getall()
        content = ' '.join(content_paragraphs).strip()  # Join paragraphs and strip whitespace
        yield {
            'content': content,
            'title': title,
            "author": "Abd al-Razzaq al-Badr",
            # include the link to the article
            "link": response.url,
            "filter": "speech",
        }