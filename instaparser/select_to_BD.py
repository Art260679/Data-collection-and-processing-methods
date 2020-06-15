from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['instadb']
collection = db.kristina010393

for user in collection.find({'type_user': 'subscriptions'}):
    pprint(user)

for user in collection.find({'type_user': 'subscribers'}):
    pprint(user)
