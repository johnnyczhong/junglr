# filename: mongo_helper.py
# author: johnny zhong
# date: 10/7/16
# purpose: create connections for mongodb

import config
import pymongo

class Connection():
    def __init__(self):
        self.connection = pymongo.MongoClient(config.localhost, config.port)
        self.db = self.connection.junglr

    def insert(self, collection, obj_hash):
        db_collection = self.db[collection]
        if type(obj_hash) == dict:
            result = db_collection.insert_one(obj_hash)
        elif type(obj_hash) == list:
            result = db_collection.insert_many(obj_hash)
        return result

    def find(self, collection, filt):
        db_collection = self.db[collection]
        if type(filt) == dict:
            result = db_collection.find_one(filt)
        elif type(filt) == list:
            result = db_collection.find_many(filt)
        return result

    def update(self, collection, filt, obj_hash, force = False):
        db_collection = self.db[collection]
        if type(obj_hash) == dict:
            result = db_collection.update_one(filt, {'$set': obj_hash}, upsert = force)
        elif type(obj_hash) == list:
            result = db_collection.update_many(filt, {'$set': obj_hash}, upsert = force)
        return result

    def delete(self, collection, filt):
        db_collection = self.db[collection]
        if type(filt) == dict:
            result = db_collection.delete_one(filt)
        elif type(filt) == list:
            result = db_collection.delete_many(filt)
        return result

    def close(self):
        self.connection.close()