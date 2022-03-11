import pymongo
import falcon
import json
import falcon.asgi as asgi
import mongo_connector

dbClient = mongo_connector.dbClient

def userLoader(attributes,username, password):
    if username == "agustin" and password == "1234":
        return {"username": username, "role":"admin"}
    else:
        return None