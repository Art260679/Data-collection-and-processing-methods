from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['instadb']
collection = db.instagram

for user in collection.find({'$and': [{'name': 'go_chatbot', 'status': 'followers'}]}):
    pprint(user)

for user in collection.find({'$and': [{'name': 'go_chatbot', 'status': 'followed_by'}]}):
    pprint(user)
