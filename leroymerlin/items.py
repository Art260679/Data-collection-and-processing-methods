# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.loader.processors import MapCompose, TakeFirst, Compose
import scrapy
from lxml import html
import re

def id_int(value):
    return int(value)


def price_int(value):
    return int(value.replace(" ", ""))


def specifications_dict(values):
    key = html.fromstring(values).xpath('//dt/text()')[0]
    value = html.fromstring(values).xpath('//dd/text()')[0][1:-30]
    value = value.replace("  ", "")
    value = value.replace("\n", "")
    specifications_to_dict = {key: value}
    return specifications_to_dict


class LeroymerlinItem(scrapy.Item):
    _id = scrapy.Field(input_processor=MapCompose(id_int), output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(price_int), output_processor=TakeFirst())
    link = scrapy.Field()
    specifications = scrapy.Field(input_processor=MapCompose(specifications_dict))
    photo = scrapy.Field()
