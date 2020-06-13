from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['instadb']
collection = db.instagram

for user in collection.find({'$and': [{'name': 'go_chatbot', 'status': 'follow_id'}]}):
    pprint(user)

for user in collection.find({'$and': [{'name': 'go_chatbot', 'status': 'follower_id'}]}):
    pprint(user)
