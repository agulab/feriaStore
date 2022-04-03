import falcon.asgi as asgi
import uvicorn
import items
import sales
import users
import properties
from falcon_auth2 import AuthMiddleware
from falcon_auth2.backends import JWTAuthBackend

claims_options = {
    "sub": {
        "essential": True
    },
    "rol": {
        "essential": True
    },
    "inv": {
        "essential": True
    }
}
auth_backend = JWTAuthBackend(users.userLoader, users.jwtKey, claims_options=claims_options)
auth_middleware = AuthMiddleware(auth_backend)
# Api
api = asgi.App(middleware=[auth_middleware], cors_enable=True)


api.add_route('/items', items.itemsResource) 

api.add_route('/items/{id:int}', items.itemResource) 

api.add_route('/items/{id:int}/toStock', items.itemToStockResource) 


api.add_route('/sales', sales.salesResource)

api.add_route('/sales/{id:int}', sales.saleResource)


api.add_route('/users', users.usersResource)


api.add_route('/properties', properties.propertiesResource)


# For debugging purposes only
if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)