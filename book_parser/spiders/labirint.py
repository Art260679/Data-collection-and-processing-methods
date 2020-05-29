# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from book_parser.items import BookparserItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']

    def __init__(self, subject):
        self.start_urls = [
            f'https://www.labirint.ru/search/{subject}/']

    def parse(self, response: HtmlResponse):
        button_next = response.css("a[title=Следующая] ").extract_first()
        links = response.xpath("//a[@class='cover']/@href").extract()
        for i in links:
            yield response.follow(i, callback=self.book_parse)
        yield response.follow(button_next, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        link = response.url
        cost = response.xpath("//div[@class = 'buying-priceold-val']/span/text()").extract_first()
        authors = response.xpath("//a[@data-event-label='author']/text()").extract_first()
        if not cost:
            price = response.xpath("//div[@class='buying-price-val']/span/text()").extract_first()
        else:
            price = response.xpath("//div[@class='buying-pricenew-val']/span/text()").extract_first()
        rating = response.xpath("//div[@id='rate']/text()").extract_first()
        currency = response.xpath("//span[@class='buying-pricenew-val-currency']/text()").extract_first()
        yield BookparserItem(name=name, link=link, price=price,
                             authors=authors, no_discounts=cost,
                             rating=rating, currency=currency)
