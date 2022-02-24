import falcon.asgi as asgi
import uvicorn
import items
import sales

# Api
api = asgi.App(cors_enable=True)


api.add_route('/items', items.itemsResource) 

api.add_route('/items/{id:int}', items.itemResource) 

api.add_route('/items/{id:int}/toStock', items.itemToStockResource) 


api.add_route('/sales', sales.salesResource)

api.add_route('/sales/{id:int}', sales.saleResource)

# For debugging purposes only
if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)