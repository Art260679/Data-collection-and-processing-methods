# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from book_parser.items import BookparserItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']

    def __init__(self, subject):
        self.start_urls = [f'https://book24.ru/search/?q={subject}']

    def parse(self, response:HtmlResponse):
        button_next = response.xpath("//a[@class='catalog-pagination__item _text js-pagination-catalog-item']").extract_first()
        links = response.xpath("//picture/ancestor::a/@href").extract()
        for i in links:
            yield response.follow(i, callback=self.book_parse)
        yield response.follow(button_next, callback=self.parse)


    def book_parse(self, response:HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        link = response.url
        cost = response.xpath("//div[@class = 'item-actions__price-old']/text()").extract_first()
        authors = response.xpath("//a[@class = 'item-tab__chars-link js-data-link']/text()").extract()
        price = response.xpath("//div[@class='item-actions__price']/b/text()").extract_first()
        rating = response.xpath("//span[@class = 'rating__rate-value']/text()").extract_first()
        currency = response.xpath("//div[@class='item-actions__price']/text()").extract_first()
        yield BookparserItem(name=name, link=link, price=price,
                             authors=authors, no_discounts=cost,
                             rating=rating, currency=currency)