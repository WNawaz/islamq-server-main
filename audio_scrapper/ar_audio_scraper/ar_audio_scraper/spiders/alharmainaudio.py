import configparser
import scrapy
from ar_audio_scraper.items import AlharmainAudio

class AlharamainAudioSpider(scrapy.Spider):
    name = 'alharamain_audio'
    allowed_domains = ['alharamain.gov.sa']
    start_urls = [
        'https://www.alharamain.gov.sa/index.cfm?do=cms.SubjectsList&audiotype=lectures&browseby=subject'
    ]

    config = configparser.ConfigParser()
    config.read('config.py')

    # feed_uri = config['SPIDER']['audio_scraper_arabic_output_dir']
    # feed_uri = '/Users/abdurrehmansubhani/uni-of-madinah-server/data/arabic/audio'

    feed_uri = '/home/grayhat/development/uni-of-madinah-server/data/arabic/audio'

    custom_settings = {
        'FEED_FORMAT': 'csv',  # Specify the output format to be CSV
        'FEED_URI': f'{feed_uri}/alharamain_audio.csv'  # Name and location of the output file
    }

    def parse(self, response):
        # Extract lesson headings and URLs to detailed pages
        for lesson in response.css('div.audiolist ul li.green'):
            item = AlharmainAudio()
            item['title'] = lesson.css('a::attr(title)').get()
            details_url = lesson.css('a::attr(href)').get()
            request = scrapy.Request(response.urljoin(details_url), callback=self.parse_details)
            request.meta['item'] = item
            yield request
        
        # Pagination: Find all available page links, then determine the next one
        current_page_number = int(response.css('div.pageing span.p_act a::text').get())
        next_page_number = current_page_number + 1
        next_page_link = response.css(f'div.pageing a[href*="page={next_page_number}"]::attr(href)').get()

        # If a next page link is found, follow it
        if next_page_link:
            next_page_url = response.urljoin(next_page_link)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_details(self, response):
        item = response.meta['item']
        item['audio_links'] = response.css('audio source::attr(src)').extract()

        # add the link to the audio page
        item['link'] = response.url
        
        yield item

