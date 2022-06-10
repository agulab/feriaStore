import pymongo
import falcon
import falcon.asgi as asgi
from items import ItemsResource
import mongo_connector
import bcrypt
import items
import sales
import json

dbClient = mongo_connector.dbClient

class UsersResource:
    auth = {
        'exempt_methods': ['POST']
    }

    #Crea un usuario
    async def on_post(self, req: asgi.Request, resp: asgi.Response):
        userData = User(await req.get_media())
        try:
            createUser(userData)
            resp.status = falcon.HTTP_201
            resp.text = "Hola " + userData["name"] + "!"
        except pymongo.errors.DuplicateKeyError as e:
            resp.status = falcon.HTTP_409
            resp.text = "Ya existe un usuario con ese email"

    #Elimina un usuario
    async def on_delete(self, req: asgi.Request, resp: asgi.Response):
        userId = req.context.auth["user"]["id"]

        result = deleteUser(userId)
        resp.status = falcon.HTTP_200
        resp.text = json.dumps(result)

    
class User(dict):
    def __init__(self, sale):
        # Atributos requeridos
        self["email"] = str(sale["email"])
        self["password"] = str(sale["password"])
        self["name"] = str(sale["name"])

        # Atributos opcionales
        self["role"] = sale.get("role") if sale.get("role") else "admin"


def userLoader(attributes, payload):
    return {"id": payload["sub"]}


def createUser(userData):
    hashedP = bcrypt.hashpw(userData["password"].encode("utf-8"), bcrypt.gensalt())
    
    user = {
        "email": userData["email"],
        "name": userData["name"],
        "role": userData["role"],
        "password": hashedP.decode("utf-8")
    }

    counters = dbClient.get_default_database().get_collection("counters").find_one_and_update(
            {},{"$inc":{"users":1}}, return_document=pymongo.ReturnDocument.AFTER)
    user["id"] = counters["users"]
    dbClient.get_default_database().get_collection("users").insert_one(user)


def deleteUser(userId):
    invId = int(userId)
    #Eliminar items
    deletedItems = items.deleteInvItems(invId)
    #Eliminar sales
    deletedSales = sales.deleteInvSales(invId)
    #Eliminar user
    deletedUser = dbClient.get_default_database().get_collection("users").delete_one({"id":userId})

    return {"deletedItems": deletedItems, "deletedSales": deletedSales, "deletedUsers": deletedUser.deleted_count}

usersResource = UsersResource()