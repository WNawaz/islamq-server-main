import scrapy
import configparser
import os

from arabic_scraper.items import AlBadarArticleItemTrace

class AlbadarArticlesSpiderTrace(scrapy.Spider):
    name = 'al_badr_articles_trace'
    allowed_domains = ['al-badr.net']
    start_urls = ['https://al-badr.net/muqolats/4']
    
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': os.path.join('data', 'spiders', 'albadr_data_trace.csv'),
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
        next_pages_urls = response.css('div.pager a::attr(href)').extract()
        for page_url in next_pages_urls:
            yield response.follow(page_url, self.parse)

    def parse_article(self, response):
        print("Parsing article:", response.url)  # Add this line to track parsing of articles
        
        item = AlBadarArticleItemTrace()
        paragraphs = response.xpath('//div[@class="cat-content"]//article[@class="post-content"]//p//text()').getall()
        item['content'] = ' '.join([para.strip() for para in paragraphs if para.strip()])
        item['title'] = response.css('h2.post-title-center::text').get(default='').strip()
        item["author"] = "Abd al-Razzaq al-Badr"
        item["link"] = response.url
        item["filter"] = "trace"

        yield item

