import scrapy
import os
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, task

from arabic_scraper.spiders.albadararticlebrief import AlBadrSpiderBrief
from arabic_scraper.spiders.albadararticleqatuf import AlBadrSpiderQatuf
from arabic_scraper.spiders.albadararticleramadan import AlBadrArticlesSpiderRamadan
from arabic_scraper.spiders.albadararticleshajj import AlbadarHajjArticlesSpider
from arabic_scraper.spiders.albadararticlespeech import AlBadrSpiderSpeech
from arabic_scraper.spiders.albadararticlevarious import AlBadrArticlesSpider
from arabic_scraper.spiders.albadararticletrace import AlbadarArticlesSpiderTrace
from arabic_scraper.spiders.binbazarticle import BinbazArticleSpider
from arabic_scraper.spiders.binbazencounters import BinbazDiscussionSpider
from arabic_scraper.spiders.binbazfatwa import BinbazFatwaSpider

def crawl_job():
    """
    Job to start spiders.
    Return Deferred, which will execute after crawl has completed.
    """
    runner = CrawlerRunner(get_project_settings())
    runner.crawl(AlBadrSpiderBrief)
    # runner.crawl(AlBadrSpiderQatuf)
    # runner.crawl(AlBadrArticlesSpiderRamadan)
    # runner.crawl(AlbadarHajjArticlesSpider)
    # runner.crawl(AlBadrSpiderSpeech)
    # runner.crawl(AlBadrArticlesSpider)
    # runner.crawl(AlbadarArticlesSpiderTrace)
    # runner.crawl(BinbazArticleSpider)
    # runner.crawl(BinbazDiscussionSpider)
    # runner.crawl(BinbazFatwaSpider)
    
    return runner.join()

def schedule_next_crawl(null, sleep_time):
    """
    Schedule the next crawl
    """
    print("Scheduling next crawl in", sleep_time, "seconds")  # Add this line to track scheduling
    reactor.callLater(sleep_time, crawl)

def crawl():
    """
    A "recursive" function that schedules a crawl 60 seconds after
    each successful crawl.
    """
    print("Starting crawl")  # Add this line to track starting crawl
    # crawl_job() returns a Deferred
    d = crawl_job()
    # call schedule_next_crawl(<scrapy response>, n) after crawl job is complete
    d.addCallback(schedule_next_crawl, 60)  # Schedule next crawl after 60 seconds
    d.addErrback(catch_error)

def catch_error(failure):
    print("Error occurred:", failure.value)  # Add this line to track errors


def run_crawl_and_reactor():
    crawl()
    reactor.run()


if __name__ == "__main__":
    run_crawl_and_reactor()
