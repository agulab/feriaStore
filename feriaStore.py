import falcon.asgi as asgi
import uvicorn
import items
import sales

# Api
api = asgi.App(cors_enable=False)

### Endpoints ###
# GET: Devuelve lista de items
api.add_route('/items', items.itemsResource) 

# GET: Devuelve el item {id}
api.add_route('/items/{id:int}', items.itemResource) 

# PUT: Pasa al stock un item {id} que estaba por hacerse.
# Puede recibir el parámetro 'n' para especificar la cantidad
# de items que deben pasar al stock.
api.add_route('/items/{id:int}/toStock', items.itemToStockResource) 


api.add_route('/sales', sales.salesResource)

api.add_route('/sales/{id:int}', sales.saleResource)

# For debugging purposes only
if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)