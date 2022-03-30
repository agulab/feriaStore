import pymongo
import falcon
import json
import falcon.asgi as asgi
import mongo_connector

dbClient = mongo_connector.dbClient

class ItemsResource:
    async def on_get(self, req: asgi.Request, resp: asgi.Response):
        invId = req.context.auth["user"]["id"]
        limit = req.get_param_as_int("limit") if req.get_param_as_int("limit") else 10
        toPage = (req.get_param_as_int("page")-1) * limit if req.get_param_as_int("page") else 0
        sort = req.get_param("sort") if req.get_param("sort") else "date"
        direction = pymongo.ASCENDING if req.has_param("asc") else pymongo.DESCENDING
        text = req.get_param("text")

        query = {'inv': invId}
        if text:
            wordsList = ""
            for word in text.split():
                wordsList += "(?=.*\\b" + word + ")"
            regex =  "^" + wordsList + ".*$"
            query['keywords'] = {'$regex': regex, '$options': 'i'}

        cursor = dbClient.get_default_database().get_collection("items").find(query, {'_id': False}).sort([(sort, direction),("_id",direction)]).skip(toPage).limit(limit)
        print(cursor.explain())

        items = []
        for item in cursor:
            items.append(item)

        resp.status = falcon.HTTP_200
        resp.text = json.dumps(items)

    async def on_post(self, req: asgi.Request, resp: asgi.Response):
        try:
            item = Item(await req.get_media(), req.context.auth["user"]["id"])
            generateKeywords(item)
            result = dbClient.get_default_database().get_collection("items").insert_one(item)
            if not result.inserted_id:
                print("problemon")
            else:
                resp.status = falcon.HTTP_201
                del item["_id"]
                resp.text = json.dumps(item)

        except KeyError as e:
            resp.status = falcon.HTTP_400
            resp.text = "Falta el atributo requerido " + str(e)

    async def on_patch(self, req: asgi.Request, resp: asgi.Response):
        invId = req.context.auth["user"]["id"]
        items = dbClient.get_default_database().get_collection("items").find({"inv": invId, "todo":{"$gt":0}}, {"_id":False})
        for item in items:
            dbClient.get_default_database().get_collection("items").update_one({"id":item["id"]},{"$inc":{"stock":item["todo"], "todo":-item["todo"]}})
        
        resp.status = falcon.HTTP_200


class ItemResource:
    async def on_get(self, req: asgi.Request, resp: asgi.Response, id):
        try:
            item = self.getItem(id, req.context.auth["user"]["id"])
            if not item:
                resp.status = falcon.HTTP_404
            else:
                resp.status = falcon.HTTP_200
                resp.text = json.dumps(item)
        except Exception as e:
            print(str(type(e)) + str(e))    

    async def on_delete(self, req: asgi.Request, resp: asgi.Response, id):
            invId = req.context.auth["user"]["id"]
            result = pymongo.results.DeleteResult
            result = dbClient.get_default_database().get_collection("items").delete_one({"id":id, "inv": invId})
            if(result.deleted_count < 1):
                resp.status = falcon.HTTP_404
                
    async def on_patch(self, req: asgi.Request, resp: asgi.Response, id):
        item = self.getItem(id, req.context.auth["user"]["id"])
        if not item:
            resp.status = falcon.HTTP_404
        else:
            body = dict(await req.get_media())
            if body.get("todo") and int(body["todo"]) >= 0:
                item["todo"] = int(body["todo"])
            if "img" in body:
                item["img"] = str(body["img"])
            if body.get("stock") and int(body["stock"]) >= 0:
                item["stock"] = int(body["stock"])
            if "custom" in body:
                item["custom"] |= body["custom"]

            generateKeywords(item)

            dbClient.get_default_database().get_collection("items").find_one_and_update({"id":id},{ "$set": {
                "img":item["img"],
                "stock":item["stock"],
                "todo":item["todo"],
                "custom":item["custom"],
                "keywords":item["keywords"]
            }})
            resp.status = falcon.HTTP_200
            resp.text = json.dumps(item)

    def getItem(self, id, invId):
        query = {"id": id, "inv": invId}
        return dbClient.get_default_database().get_collection("items").find_one(query, {'_id': False})


class ItemToStockResource:
    async def on_put(self, req: asgi.Request, resp: asgi.Response, id):
        if (not itemResource.getItem(id, req.context.auth["user"]["id"])):
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


class Item(dict):
    def __init__(self, item: dict, invId):
        
        # Atributos requeridos
        self["name"] = str(item.pop("name"))

        # Atributos opcionales
        self["stock"] = int(item.pop("stock", 0))
        self["todo"] = int(item.pop("todo", 0))
        self["img"] = item.pop("img", "")

        self["custom"] = item.pop("custom",{})

        self["inv"] = invId

        counters = dbClient.get_default_database().get_collection("counters").find_one_and_update(
            {},{"$inc":{"items":1}}, return_document=pymongo.ReturnDocument.AFTER)
        self["id"] = counters["items"]


def generateKeywords(item):
    keywords = []
    for s in item["name"].casefold().split():
        if s not in keywords: keywords.append(s)
    if item.get("custom"):
        for v in item["custom"].values():
            for s in v.casefold().split(): 
                if s not in keywords: keywords.append(s)
        for k in item["custom"]:
            for s in k.casefold().split():
                if s not in keywords: keywords.append(s)   

    item["keywords"] = " ".join(keywords)


itemsResource = ItemsResource()
itemResource = ItemResource()
itemToStockResource = ItemToStockResource()