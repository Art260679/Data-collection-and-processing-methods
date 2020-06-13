from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instaparser.spiders.instagram import InstagramSpider
from instaparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)

    #users = ['2s.yshanka', 'kristina010393', 'savkohalyna']
    users = ['kristina010393']
    process.crawl(InstagramSpider, users=users)

    process.start()