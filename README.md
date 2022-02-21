## GET: '/items'
Devuelve lista de items
## GET: '/items/{id}'
Devuelve el item {id}
## DELETE: '/items/{id}'
Elimina el item {id}
## PUT: '/items/{id}/toStock'
Pasa al stock un item {id} que estaba por hacerse.
Puede recibir el parámetro 'n' para especificar la cantidad
de items que deben pasar al stock.
