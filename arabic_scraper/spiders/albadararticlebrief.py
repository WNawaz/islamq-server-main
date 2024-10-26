import scrapy
import os

class AlBadrSpiderBrief(scrapy.Spider):
    name = 'al_badr_articles_brief'
    allowed_domains = ['al-badr.net']
    start_urls = ['https://al-badr.net/muqolats/5']


    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': os.path.join('data', 'spiders', 'albadr_data_brief.csv'),
        'FEED_EXPORT_ENCODING': 'utf-8',
        'CSV_EXPORT_HEADERS': False,
    }
            
    def parse(self, response):
        print("Parsing:", response.url)  # Add this line to track parsing
        
        # Extract article titles and URLs
        for article in response.css('div.post-content ul li a::attr(href)'):
            url = response.urljoin(article.extract())
            yield scrapy.Request(url, callback=self.parse_article)

        # Extract the link for the next page
        next_page = response.css('div.pager a:contains(">")::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_article(self, response):
        print("Parsing article:", response.url)  # Add this line to track parsing of articles
        
        # Extract the title
        title = response.css('h2.post-title-center::text').get().strip()

    # Extract the content paragraphs
        paragraphs = response.css(
            'div.cat-content article.post-content p::text').getall()
    # Combine the paragraph texts into one string
        content = ' '.join([para.strip() for para in paragraphs])
        

        yield {
            'content': content,
            'title': title,
            "author": "Abd al-Razzaq al-Badr",
            "link": response.url,
            "filter": "brief",
        }
