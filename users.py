import pymongo
import falcon
import json
import falcon.asgi as asgi
import mongo_connector
import bcrypt
from os import environ
from time import time
from authlib.jose import jwt

dbClient = mongo_connector.dbClient
jwtTTL = 60 * 60 # 1 hora

class UsersResource:
    auth = {
        "exempt_methods": ["POST", "GET"]
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
        body = await req.get_media()
        if not body.get("email") or not body.get("password"):
            resp.status = falcon.HTTP_400
            resp.text = "El body debe contener los campos 'email' y 'password'"
        else:
            dbUser = dbClient.get_default_database().get_collection("users").find_one({"email":body["email"]}, {"_id":False})
            if dbUser and bcrypt.checkpw(body["password"].encode("utf-8"), dbUser["password"].encode("utf-8")):
                del dbUser["password"]
                dbUser["jwt"] = createJWLToken(dbUser["id"], dbUser["role"], dbUser["id"])
                resp.status = falcon.HTTP_200
                resp.text = json.dumps(dbUser)
            elif dbUser:
                resp.status = falcon.HTTP_403
                resp.text = "El password es incorrecto"
            else:
                resp.status = falcon.HTTP_404
                resp.text = "El email " + body["email"] + " no está registrado"
        

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


def createJWLToken(id, role, inv):
    payload = {
        "sub": id,
        "rol": role,
        "inv": inv,
        "exp": int(time()) + jwtTTL
    }
    return jwt.encode({"alg": "HS256"}, payload, jwtKey).decode("utf-8")

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

usersResource = UsersResource()
jwtKey = environ.get("FERIA_APP_JWT_KEY")