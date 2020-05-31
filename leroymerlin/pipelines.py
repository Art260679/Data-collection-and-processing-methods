# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import hashlib


class LeroymerlinPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.LeroymerlinBD

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.update({'_id': item['_id']}, item, True)
        return item


class LeroymerlinPhotoPipelines(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photo']:
            for img in item['photo']:
                try:  # try_except чтобы не рушился scrapy при неудачном скачивании фотографий
                    yield scrapy.Request(img, meta=item)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        """  if item=True then take second element from the tuple (results [1]) """
        if results:
            item['photo'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None):
        name_dir = request.meta['name']
        image_guid = hashlib.sha1(request.url.encode('utf-8')).hexdigest()
        return f'{name_dir}/{image_guid}.jpg'

    def thumb_path(self, request, thumb_id, response=None, info=None):
        name_dir = request.meta['name']
        thumb_guid = hashlib.sha1(request.url.encode('utf-8')).hexdigest()
        return f'{name_dir}/{thumb_id}/{thumb_guid}.jpg'
