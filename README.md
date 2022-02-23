# /items
### GET: retorna lista de items. 
#### Parámetros opcionales: 
- **limit=int** cantidad de resultados por página
- **page=int** número de la página requerida
- **sort=string** nombre de alguno de los atributos del item por el que ordenar
- **asc** para especificar un orden ascendente. Por defecto el orden es descendente
#### Ejemplos:
- `/items?limit=10,page=1,sort=model,asc`
- `/items?limit=5,sort=id`
### POST: crea un nuevo item y lo retorna
#### Atributos obligatorios del body:
- **model=string** el modelo del item
- **size=string** el tamaño del item
#### Atributos opcionales del body:
- **stock=int** por defecto se crea con stock 0
- **todo=int** por defecto se crea con toDo 0
- **img=string** url de una imagen

# /items/{id}
### GET: retorna el item {id}
### DELETE: elimina el item {id}

# /items/{id}/toStock
### PUT: suma al stock y resta de toDo
#### Atributos opcionales:
- **n=int** por defecto se suma y resta un elemento, pero con este parámetro puede especificarse una cantidad diferente

# /sales
#### GET: retorna lista de ventas
#### Parámetros opcionales: 
- **limit=int** cantidad de resultados por página
- **page=int** número de la página requerida
- **sort=string** nombre de alguno de los atributos de la venta por el que ordenar
- **asc** para especificar un orden ascendente. Por defecto el orden es descendente
### POST: crea una nueva venta y la retorna
#### Atributos obligatorios del body:
- **itemId=int** el id del item que se vende
- **price=int** el precio del item que se vende

# /sales/{id}
### GET: retorna la venta {id}
