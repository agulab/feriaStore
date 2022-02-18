import falcon
import falcon.asgi as asgi
import mongo_connector
import uvicorn
import pymongo
import json

class ItemsResource:
    async def on_get(self, req: asgi.Request, resp: asgi.Response):
        """Handles GET requests"""
        toPage = (req.get_param_as_int("page")-1) * limit if req.get_param_as_int("page") else 0
        limit = req.get_param_as_int("limit") if req.get_param_as_int("limit") else 10
        sort = req.get_param("sort") if req.get_param("sort") else None
        if sort:
            cursor = dbClient.get_default_database().get_collection("items").find({}, {'_id': False}).sort(sort).skip(toPage).limit(limit)
        else:
            cursor = dbClient.get_default_database().get_collection("items").find({}, {'_id': False}).skip(toPage).limit(limit)

        resp.status = falcon.HTTP_200
        items = []
        for item in cursor:
            items.append(item)

        resp.text = json.dumps(items)

class ItemResource:
    async def on_get(self, req: asgi.Request, resp: asgi.Response, id):
        query = {"id": id}
        print(query)
        try:
            item = dbClient.get_default_database().get_collection("items").find_one(query, {'_id': False})
            print(item)
            resp.status = falcon.HTTP_200
            resp.text = json.dumps(item)
        except Exception as e:
            print(str(type(e)) + str(e))    
        
dbClient = mongo_connector.dbClient

# Api
api = asgi.App()
items = ItemsResource()
item = ItemResource()

# Endpoints
api.add_route('/items', items)
api.add_route('/items/{id:int}', item)


# For debugging purposes only
if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)