import falcon
import falcon.asgi as asgi
import mongo_connector
import bcrypt
import json
from authlib.jose import jwt
from time import time
from os import environ

dbClient = mongo_connector.dbClient
jwtTTL = 60 * 60 # 1 hora

class SessionsResource:
    auth = {"auth_disabled": True}

    #LOGIN: retorna el usuario de la BBDD con token JWT
    async def on_post(self, req: asgi.Request, resp: asgi.Response):
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
                resp.status = falcon.HTTP_401
                resp.text = "El password es incorrecto"
            else:
                resp.status = falcon.HTTP_404
                resp.text = "El email " + body["email"] + " no está registrado"
        

def createJWLToken(id, role, inv):
    payload = {
        "sub": id,
        "rol": role,
        "inv": inv,
        "exp": int(time()) + jwtTTL
    }
    return jwt.encode({"alg": "HS256"}, payload, jwtKey).decode("utf-8")


jwtKey = environ.get("FERIA_APP_JWT_KEY")
sessionsResource = SessionsResource()