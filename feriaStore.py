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
        try:
            item = self.getItem(id)
            resp.status = falcon.HTTP_200
            resp.text = json.dumps(item)
        except Exception as e:
            print(str(type(e)) + str(e))    

    def getItem(self, id):
        query = {"id": id}
        return dbClient.get_default_database().get_collection("items").find_one(query, {'_id': False})


dbClient = mongo_connector.dbClient

class ItemToStockResource:
    async def on_put(self, req: asgi.Request, resp: asgi.Response, id):
        if (not itemResource.getItem(id)):
            resp.status = falcon.HTTP_404
        else:
            n = 1 if not req.get_param_as_int("n") else req.get_param_as_int("n")
            query = {"$inc":{"stock":n, "todo":-n}}
            updatedItem = dbClient.get_default_database().get_collection("items").find_one_and_update(
                {"id":id, "todo": {"$gte":n}}, query, {'_id':False}, return_document=pymongo.ReturnDocument.AFTER)
            if(updatedItem):
                resp.status = falcon.HTTP_200
                resp.text = json.dumps(updatedItem)
            else:
                resp.status = falcon.HTTP_409




# Api
api = asgi.App()
itemsResource = ItemsResource()
itemResource = ItemResource()
itemToStockResource = ItemToStockResource()


### Endpoints ###
# GET: Devuelve lista de items
api.add_route('/items', itemsResource) 

# GET: Devuelve el item {id}
api.add_route('/items/{id:int}', itemResource) 

# PUT: Pasa al stock un item {id} que estaba por hacerse.
# Puede recibir el parámetro 'n' para especificar la cantidad
# de items que deben pasar al stock.
api.add_route('/items/{id:int}/toStock', itemToStockResource) 


# For debugging purposes only
if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)