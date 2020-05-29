from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from book_parser import settings
from book_parser.spiders.book24 import Book24Spider
from book_parser.spiders.labirint import LabirintSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    search = input('Введите название тематики: ')

    process.crawl(Book24Spider, subject=search)
    process.crawl(LabirintSpider, subject=search)
    process.start()
