# Dgraph Lab 2 - Pydgraph

Aplicación en Python con pydgraph para el modelo de grafo de la red logística de DHL Express que diseñé en el Dgraph Lab 1. Tiene seis tipos de nodo (Cliente, Envio, Instalacion, Vehiculo, Empleado e Incidencia) y los datos se cargan desde archivos CSV.

Abimael Gutierrez Millan (759614)

## Archivos

`main.py` es el cliente: se conecta a Dgraph, crea el schema al iniciar y muestra el menú.

`model.py` tiene el schema, la carga de los CSV, las consultas y los borrados.

`csv/` tiene un archivo por cada tipo de nodo (instalaciones, clientes, empleados, vehiculos, envios e incidencias) y uno por cada relación (conecta_con, trabaja_en, opera, envia, dirigido_a, pasa_por, transportado_en, entrega, tiene_incidencia y ocurre_en). En los CSV de relaciones, `origen` y `destino` son las llaves de los nodos y las demás columnas son los facets de la arista.

## Cómo ejecutarlo

1. Levantar Dgraph y Ratel con Docker:

```
docker run --name dgraph -d -p 8080:8080 -p 9080:9080 dgraph/standalone:latest
docker run --name ratel -d -p 8000:8000 dgraph/ratel:latest
```

2. Crear el entorno virtual e instalar pydgraph (macOS o Linux):

```
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

En Windows el entorno se activa con `.\venv\Scripts\Activate.ps1`.

3. Correr el cliente desde la carpeta del proyecto:

```
python3 main.py
```

Por defecto se conecta a `localhost:9080`. Para usar otra dirección se cambia la variable de entorno `DGRAPH_URI`.

## Menú

```
1 -- Cargar datos de los CSV
2 -- Buscar clientes por nombre                (índice de texto term en nombre)
3 -- Envíos con valor declarado mínimo         (índice numérico float en valor_declarado_usd)
4 -- Rastrear un envío por número de guía      (varios tipos de nodo)
5 -- Envíos que pasaron por una instalación    (relación en reversa ~pasa_por)
6 -- Incidencias ordenadas por severidad       (orderdesc)
7 -- Número de envíos por cliente              (count)
8 -- Ver envíos por página                     (first y offset)
9 -- Borrar empleados por rol                  (borrado con condición)
10 -- Borrar todos los datos                   (conserva el schema)
11 -- Salir
```

La opción 1 revisa primero si ya hay datos, para no duplicar los nodos. Para volver a cargar hay que usar antes la opción 10.
