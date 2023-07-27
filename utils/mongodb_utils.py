from pymongo import MongoClient
import pandas as pd

def mongodb_connector():
    # Connect to local MongoDB
    client = MongoClient('localhost', 27017)
    mongodb = client['academicworld']
    return mongodb

def mongodb_query_result(mongodb):
    # Fetch data from MongoDB and convert to DataFrame
    collection = mongodb['faculty']
    pipeline = [
        {'$unwind': '$keywords'},
        {'$sort': {'keywords.score': -1}},
        {'$group': {
            '_id': '$_id',
            'name': {'$first': '$name'},
            'position': {'$first': '$position'},
            'email': {'$first': '$email'},
            'phone': {'$first': '$phone'},
            'affiliation': {'$first': '$affiliation.name'},
            'photoUrl': {'$first': '$photoUrl'},
            'Top Keyword': {'$first': '$keywords.name'},
            #'Keyword Score': {'$first': '$keywords.score'}
        }},
        {'$project': {'_id': 0, 'name': 1, 'position': 1, 'email': 1, 'phone': 1, 'affiliation': 1, 'photoUrl': 1, 'Top Keyword': 1}} #'Keyword Score': 1
    ]
    data_from_mongo = list(collection.aggregate(pipeline))
    mongodb_df = pd.DataFrame(data_from_mongo)
    return data_from_mongo, mongodb_df