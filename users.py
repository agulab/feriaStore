import pymongo
import falcon
import json
import falcon.asgi as asgi
import mongo_connector
import bcrypt

dbClient = mongo_connector.dbClient

class UsersResource:
    auth = {
        "exempt_methods": ["POST"]
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

    #LOGIN: retorna el usuario de la BBDD
    async def on_get(self, req: asgi.Request, resp: asgi.Response):
        resp.status = falcon.HTTP_200
        resp.text = json.dumps(req.context.auth["user"])


class User(dict):
    def __init__(self, sale):
        # Atributos requeridos
        self["email"] = str(sale["email"])
        self["password"] = str(sale["password"])
        self["name"] = str(sale["name"])

        # Atributos opcionales
        self["role"] = sale.get("role") if sale.get("role") else "seller"


def userLoader(attributes, email, password):
    dbUser = dbClient.get_default_database().get_collection("users").find_one({"email":email}, {"_id":False})
    if dbUser and bcrypt.checkpw(password.encode("utf-8"), dbUser["password"].encode("utf-8")):
        del dbUser["password"]
        return dbUser
    else:
        return None


def createUser(userData):
    hashedP = bcrypt.hashpw(userData["password"].encode("utf-8"), bcrypt.gensalt())
    
    user = {
        "email": userData["email"],
        "name": userData["name"],
        "role": userData["role"],
        "password": hashedP.decode("utf-8")
    }

    dbClient.get_default_database().get_collection("users").insert_one(user)

usersResource = UsersResource()