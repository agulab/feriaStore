import pymongo
import falcon
import json
import falcon.asgi as asgi
import mongo_connector

dbClient = mongo_connector.dbClient

class SalesResource:
    async def on_get(self, req: asgi.Request, resp: asgi.Response):
        limit = req.get_param_as_int("limit") if req.get_param_as_int("limit") else 10
        toPage = (req.get_param_as_int("page")-1) * limit if req.get_param_as_int("page") else 0
        sort = req.get_param("sort") if req.get_param("sort") else "date"
        asc = pymongo.ASCENDING if req.get_param_as_bool("asc") else pymongo.DESCENDING

        cursor = dbClient.get_default_database().get_collection("sales").find({}, {'_id': False}).sort(sort, asc).skip(toPage).limit(limit)
        sales = []
        for sale in cursor:
            sales.append(sale)

        resp.status = falcon.HTTP_200
        resp.text = json.dumps(sales)


class SaleResource:
    async def on_get(self, req: asgi.Request, resp: asgi.Response, id):
        sale = self.getSale(id)
        if not sale:
            resp.status = falcon.HTTP_404
        else:
            resp.status = falcon.HTTP_200
            resp.text = json.dumps(sale)

    async def on_delete(self, req: asgi.Request, resp: asgi.Response, id):
        result = pymongo.results.DeleteResult
        result = dbClient.get_default_database().get_collection("sales").delete_one({"id":id})
        if(result.deleted_count < 1):
            resp.status = falcon.HTTP_404
                
    def getSale(self, id):
        query = {"id": id}
        return dbClient.get_default_database().get_collection("sales").find_one(query, {'_id': False})


salesResource = SalesResource()
saleResource = SaleResource()