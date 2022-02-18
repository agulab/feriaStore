import falcon
import falcon.asgi as asgi
import mongo_connector
import uvicorn
import pymongo

class ItemsResource:
    async def on_get(self, req: asgi.Request, resp: asgi.Response):
        """Handles GET requests"""
        page = req.get_param_as_int("page") if req.get_param_as_int("page") else 1
        limit = req.get_param_as_int("limit") if req.get_param_as_int("limit") else 5

        cursor = dbClient.get_default_database().get_collection("items").find()
        resp.status = falcon.HTTP_200
        resp.body = cursor[(page-1) * limit : page * limit]

class ItemResource:
    async def on_get(self, req: asgi.Request, resp: asgi.Response):
        id = req.get_param_as_int("id", True)
        query = {"id": id}
        print(query)
        try:
            item = dbClient.get_default_database().get_collection("items").find_one(query)
            print(item)
            resp.status = falcon.HTTP_200
            resp.text = item
        except Exception as e:
            print(str(type(e)) + str(e))    
        
dbClient = mongo_connector.dbClient

# Api
api = asgi.App()
items = ItemsResource()
item = ItemResource()

# Endpoints
api.add_route('/items', items)
api.add_route('/item', item)


# For debugging purposes only
if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)