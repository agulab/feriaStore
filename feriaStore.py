import falcon.asgi as asgi
import uvicorn
import items
import sales
import users
import customProperties
from falcon_auth2 import AuthMiddleware
from falcon_auth2.backends import BasicAuthBackend

auth_backend = BasicAuthBackend(users.userLoader)
auth_middleware = AuthMiddleware(auth_backend)
# Api
api = asgi.App(middleware=[auth_middleware], cors_enable=True)


api.add_route('/items', items.itemsResource) 

api.add_route('/items/{id:int}', items.itemResource) 

api.add_route('/items/{id:int}/toStock', items.itemToStockResource) 


api.add_route('/sales', sales.salesResource)

api.add_route('/sales/{id:int}', sales.saleResource)


api.add_route('/users', users.usersResource)


api.add_route('/custom', customProperties.customPropertiesResource)


# For debugging purposes only
if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)