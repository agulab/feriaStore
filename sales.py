import pymongo
import falcon
import json
import falcon.asgi as asgi
import mongo_connector
import re

dbClient = mongo_connector.dbClient

class SalesResource:
    async def on_get(self, req: asgi.Request, resp: asgi.Response):
        limit = req.get_param_as_int("limit") if req.get_param_as_int("limit") else 10
        toPage = (req.get_param_as_int("page")-1) * limit if req.get_param_as_int("page") else 0
        sort = req.get_param("sort") if req.get_param("sort") else "date"
        asc = pymongo.ASCENDING if req.get_param_as_bool("asc") else pymongo.DESCENDING
        if sort in ["name","size"]:
            sort = "item." + sort

        cursor = dbClient.get_default_database().get_collection("sales").aggregate([
            {'$lookup':{'from': 'items', 'localField': 'itemId', 'foreignField': 'id', 'as': 'item'}},
            {'$sort': {sort:asc, "_id":asc}},
            {'$skip':toPage},
            {'$limit':limit}])
        sales = []
        for sale in cursor:
            sale["name"] = sale["item"][0]["name"]
            sale["size"] = sale["item"][0]["size"]
            del sale["item"]
            del sale["_id"]
            sales.append(sale)

        resp.status = falcon.HTTP_200
        resp.text = json.dumps(sales)

    async def on_post(self, req: asgi.Request, resp: asgi.Response):
        try:
            saleReq = await req.get_media()
            item = dbClient.get_default_database().get_collection("items").find_one({"id": int(saleReq["itemId"])})
            if not item:
                resp.status = falcon.HTTP_404
                resp.text = "No se encontró el item con id " + str(saleReq.get("itemId"))
            elif item["stock"] < 1:
                resp.status = falcon.HTTP_400
                resp.text = "Imposible crear venta de item sin stock"
            else:
                try:
                    sale = Sale(saleReq)
                    dbClient.get_default_database().get_collection("sales").insert_one(sale)
                    dbClient.get_default_database().get_collection("items").find_one_and_update({"id":item["id"]},{"$inc":{"stock":-1}})
                    
                    del sale["_id"]
                    resp.status = falcon.HTTP_201
                    resp.text = json.dumps(sale)
                except ValueError as e:
                    resp.status = falcon.HTTP_400
                    resp.text = "El valor de un atributo es de tipo incorrecto: " + str(e)

        except KeyError as e:
            resp.status = falcon.HTTP_400
            resp.text = "Falta el atributo requerido " + str(e)


class SaleResource:
    async def on_get(self, req: asgi.Request, resp: asgi.Response, id):
        sale = self.getSale(id)
        if not sale:
            resp.status = falcon.HTTP_404
        else:
            resp.status = falcon.HTTP_200
            resp.text = json.dumps(sale)

    async def on_delete(self, req: asgi.Request, resp: asgi.Response, id):
        sale = dbClient.get_default_database().get_collection("sales").find_one({"id":id})
        result = pymongo.results.DeleteResult
        result = dbClient.get_default_database().get_collection("sales").delete_one({"id":id})
        dbClient.get_default_database().get_collection("items").update_one({"id":sale["itemId"]}, {"$inc":{"stock":1}})
        if(result.deleted_count < 1):
            resp.status = falcon.HTTP_404
                
    def getSale(self, id):
        query = {"id": id}
        return dbClient.get_default_database().get_collection("sales").find_one(query, {'_id': False})

            
class Sale(dict):
    def __init__(self, sale):
        checkDate = re.compile("\d{4}-\d{2}-\d{2}")
        
        # Atributos requeridos
        self["price"] = int(sale["price"])
        self["itemId"] = int(sale["itemId"])
        if checkDate.match(sale["date"]):
            self["date"] = sale["date"]
        else:
            raise ValueError("El formato de le fecha debe ser 'YYYY-MM-DD'")
            

        counters = dbClient.get_default_database().get_collection("counters").find_one_and_update(
            {},{"$inc":{"sales":1}}, return_document=pymongo.ReturnDocument.AFTER)
        self["id"] = counters["sales"]


salesResource = SalesResource()
saleResource = SaleResource()