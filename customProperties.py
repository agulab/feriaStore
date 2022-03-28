import json
import falcon
import falcon.asgi as asgi
import mongo_connector

dbClient = mongo_connector.dbClient

class CustomProperties:
    async def on_get(self, req: asgi.Request, resp: asgi.Response):
        invId = req.context.auth["user"]["id"]
        customProperties = dbClient.get_default_database().get_collection("items").aggregate([
            {"$match": {"inv":invId}},
            {"$project":{"propiedades":{"$objectToArray":"$custom"}}},
            {"$unwind":"$propiedades"},
            {"$group":{"_id":None,"allkeys":{"$addToSet":"$propiedades.k"}}}
        ])

        resultados = []
        for prop in customProperties:
            resultados = prop["allkeys"]
        resultados.sort(key=lambda v: v.upper())
        resp.status = falcon.HTTP_200
        resp.text = json.dumps(resultados)



customPropertiesResource = CustomProperties()