from pymongo import MongoClient


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instadb

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.collection]
        collection.update({'_id': item['_id']}, item, True)
        return item
