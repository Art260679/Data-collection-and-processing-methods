from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroymerlin import settings
from leroymerlin.spiders.lerua import LeruaSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    search = input('Введите название тематики: ')

    process.crawl(LeruaSpider, subject=search)

    process.start()
