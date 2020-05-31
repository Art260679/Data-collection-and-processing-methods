# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from leroymerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader


class LeruaSpider(scrapy.Spider):
    name = 'lerua'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, subject):
        self.start_urls = [f'https://leroymerlin.ru/search/?display=90&tab=products&q={subject}']

    def parse(self, response: HtmlResponse):
        button_next = response.xpath("//div[@class='service-panel clearfix pagination-bottom']//div//a["
                                     "@class='paginator-button next-paginator-button']/@href").extract_first()
        links = response.xpath('//div[@class="product-name"]/a/@href').extract()
        for i in links:
            yield response.follow(i, callback=self.leroymerlin)
        yield response.follow(button_next, callback=self.parse)

    def leroymerlin(self, response):
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        loader.add_xpath('_id', "//span[@slot='article']/@content")
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        loader.add_value('link', response.url)
        loader.add_css('specifications', "dl div")
        loader.add_xpath('photo', "//source[@media=' only screen and (min-width: 1024px)']/@srcset")
        yield loader.load_item()
