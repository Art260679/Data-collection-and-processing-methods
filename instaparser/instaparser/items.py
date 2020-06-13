# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    username = scrapy.Field()
    full_name = scrapy.Field()
    is_private = scrapy.Field()
    profile_pic_url = scrapy.Field()
    type_user = scrapy.Field()
