from pymongo import MongoClient

def mongodb_connector():
    # Connect to local MongoDB
    client = MongoClient('localhost', 27017)
    mongodb = client['academicworld']
    return mongodb