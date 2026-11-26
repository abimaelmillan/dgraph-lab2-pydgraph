#!/usr/bin/env python3
import csv
import json
import os

import pydgraph

# Carpeta donde están los archivos CSV
CSV_DIR = "csv"


def set_schema(client):
    schema = """
    type Cliente {
        id_cliente
        nombre
        tipo_cliente
        pais
        es_premium
        fecha_alta
        envia
    }

    type Envio {
        numero_guia
        servicio
        peso_kg
        valor_declarado_usd
        es_peligroso
        estado
        fecha_compromiso
        dirigido_a
        pasa_por
        transportado_en
        tiene_incidencia
    }

    type Instalacion {
        codigo
        tipo
        ciudad
        pais
        capacidad_diaria
        ubicacion
        conecta_con
    }

    type Vehiculo {
        matricula
        tipo
        capacidad_kg
        es_electrico
        estado
    }

    type Empleado {
        id_empleado
        nombre
        rol
        certificado_mp
        antiguedad_anios
        opera
        trabaja_en
        entrega
    }

    type Incidencia {
        id_incidencia
        tipo
        severidad
        fecha
        resuelta
        descripcion
        ocurre_en
    }

    id_cliente: string @index(exact) @upsert .
    nombre: string @index(term) .
    tipo_cliente: string @index(exact) .
    pais: string @index(exact) .
    es_premium: bool @index(bool) .
    fecha_alta: datetime .

    numero_guia: string @index(exact) @upsert .
    servicio: string @index(exact) .
    peso_kg: float .
    valor_declarado_usd: float @index(float) .
    es_peligroso: bool @index(bool) .
    estado: string @index(exact) .
    fecha_compromiso: datetime @index(hour) .

    codigo: string @index(exact) @upsert .
    tipo: string @index(exact) .
    ciudad: string @index(exact) .
    capacidad_diaria: int .
    ubicacion: geo @index(geo) .

    matricula: string @index(exact) @upsert .
    capacidad_kg: float .
    es_electrico: bool @index(bool) .

    id_empleado: string @index(exact) @upsert .
    rol: string @index(exact) .
    certificado_mp: bool @index(bool) .
    antiguedad_anios: int .

    id_incidencia: string @index(exact) @upsert .
    severidad: int @index(int) .
    fecha: datetime @index(hour) .
    resuelta: bool @index(bool) .
    descripcion: string .

    envia: [uid] @reverse .
    dirigido_a: uid @reverse .
    pasa_por: [uid] @reverse .
    conecta_con: [uid] @reverse .
    transportado_en: [uid] @reverse .
    opera: [uid] @reverse .
    trabaja_en: uid @reverse .
    entrega: [uid] @reverse .
    tiene_incidencia: [uid] @reverse .
    ocurre_en: uid @reverse .
    """
    return client.alter(pydgraph.Operation(schema=schema))


# ---------------------------------------------------------------------
# Carga de datos desde los CSV
# ---------------------------------------------------------------------

def leer_csv(archivo):
    with open(os.path.join(CSV_DIR, archivo), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def texto_a_bool(valor):
    # En el CSV los booleanos vienen como "true" o "false"
    return valor == "true"


def hay_datos(client):
    query = """{
        total(func: type(Instalacion)) {
            count(uid)
        }
    }"""
    res = client.txn(read_only=True).query(query)
    datos = json.loads(res.json)
    return datos["total"][0]["count"] > 0


def guardar_nodos(client, nodos):
    txn = client.txn()
    try:
        res = txn.mutate(set_obj=nodos)
        txn.commit()
        return res.uids
    finally:
        txn.discard()


def cargar_instalaciones(client):
    nodos = []
    for row in leer_csv("instalaciones.csv"):
        nodos.append({
            "uid": "_:" + row["codigo"],
            "dgraph.type": "Instalacion",
            "codigo": row["codigo"],
            "tipo": row["tipo"],
            "ciudad": row["ciudad"],
            "pais": row["pais"],
            "capacidad_diaria": int(row["capacidad_diaria"]),
            "ubicacion": {
                "type": "Point",
                "coordinates": [float(row["lon"]), float(row["lat"])],
            },
        })
    uids = guardar_nodos(client, nodos)
    print(f"Instalaciones cargadas: {len(nodos)}")
    return uids


def cargar_clientes(client):
    nodos = []
    for row in leer_csv("clientes.csv"):
        nodos.append({
            "uid": "_:" + row["id_cliente"],
            "dgraph.type": "Cliente",
            "id_cliente": row["id_cliente"],
            "nombre": row["nombre"],
            "tipo_cliente": row["tipo_cliente"],
            "pais": row["pais"],
            "es_premium": texto_a_bool(row["es_premium"]),
            "fecha_alta": row["fecha_alta"],
        })
    uids = guardar_nodos(client, nodos)
    print(f"Clientes cargados: {len(nodos)}")
    return uids


def cargar_empleados(client):
    nodos = []
    for row in leer_csv("empleados.csv"):
        nodos.append({
            "uid": "_:" + row["id_empleado"],
            "dgraph.type": "Empleado",
            "id_empleado": row["id_empleado"],
            "nombre": row["nombre"],
            "rol": row["rol"],
            "certificado_mp": texto_a_bool(row["certificado_mp"]),
            "antiguedad_anios": int(row["antiguedad_anios"]),
        })
    uids = guardar_nodos(client, nodos)
    print(f"Empleados cargados: {len(nodos)}")
    return uids


def cargar_vehiculos(client):
    nodos = []
    for row in leer_csv("vehiculos.csv"):
        nodos.append({
            "uid": "_:" + row["matricula"],
            "dgraph.type": "Vehiculo",
            "matricula": row["matricula"],
            "tipo": row["tipo"],
            "capacidad_kg": float(row["capacidad_kg"]),
            "es_electrico": texto_a_bool(row["es_electrico"]),
            "estado": row["estado"],
        })
    uids = guardar_nodos(client, nodos)
    print(f"Vehículos cargados: {len(nodos)}")
    return uids


def cargar_envios(client):
    nodos = []
    for row in leer_csv("envios.csv"):
        nodos.append({
            "uid": "_:" + row["numero_guia"],
            "dgraph.type": "Envio",
            "numero_guia": row["numero_guia"],
            "servicio": row["servicio"],
            "peso_kg": float(row["peso_kg"]),
            "valor_declarado_usd": float(row["valor_declarado_usd"]),
            "es_peligroso": texto_a_bool(row["es_peligroso"]),
            "estado": row["estado"],
            "fecha_compromiso": row["fecha_compromiso"],
        })
    uids = guardar_nodos(client, nodos)
    print(f"Envíos cargados: {len(nodos)}")
    return uids


def cargar_incidencias(client):
    nodos = []
    for row in leer_csv("incidencias.csv"):
        nodos.append({
            "uid": "_:" + row["id_incidencia"],
            "dgraph.type": "Incidencia",
            "id_incidencia": row["id_incidencia"],
            "tipo": row["tipo"],
            "severidad": int(row["severidad"]),
            "fecha": row["fecha"],
            "resuelta": texto_a_bool(row["resuelta"]),
            "descripcion": row["descripcion"],
        })
    uids = guardar_nodos(client, nodos)
    print(f"Incidencias cargadas: {len(nodos)}")
    return uids


def cargar_relacion(client, archivo, predicado, uids, facets):
    # Cada fila del CSV tiene el nodo origen, el nodo destino y los facets de la arista.
    # facets dice qué columnas son facets y con qué función se convierten.
    txn = client.txn()
    try:
        filas = leer_csv(archivo)
        for row in filas:
            arista = {"uid": uids[row["destino"]]}
            for nombre, convertir in facets.items():
                arista[predicado + "|" + nombre] = convertir(row[nombre])
            txn.mutate(set_obj={
                "uid": uids[row["origen"]],
                predicado: arista,
            })
        txn.commit()
        print(f"Relaciones {predicado}: {len(filas)}")
    finally:
        txn.discard()


def cargar_datos(client):
    if hay_datos(client):
        print("Ya hay datos cargados. Bórralos primero para no duplicar los nodos.")
        return

    # Diccionario con el uid real de cada nodo, usando su llave (código, guía, matrícula...)
    uids = {}
    uids.update(cargar_instalaciones(client))
    uids.update(cargar_clientes(client))
    uids.update(cargar_empleados(client))
    uids.update(cargar_vehiculos(client))
    uids.update(cargar_envios(client))
    uids.update(cargar_incidencias(client))

    cargar_relacion(client, "conecta_con.csv", "conecta_con", uids,
                    {"distancia_km": float, "horas_estimadas": float, "modo": str})
    cargar_relacion(client, "trabaja_en.csv", "trabaja_en", uids,
                    {"puesto": str, "desde": str})
    cargar_relacion(client, "opera.csv", "opera", uids,
                    {"turno": str, "fecha": str})
    cargar_relacion(client, "envia.csv", "envia", uids,
                    {"fecha_recoleccion": str})
    cargar_relacion(client, "dirigido_a.csv", "dirigido_a", uids,
                    {"direccion": str})
    cargar_relacion(client, "pasa_por.csv", "pasa_por", uids,
                    {"orden": int, "fecha_escaneo": str, "tipo_escaneo": str})
    cargar_relacion(client, "transportado_en.csv", "transportado_en", uids,
                    {"tramo": str, "fecha": str})
    cargar_relacion(client, "entrega.csv", "entrega", uids,
                    {"fecha_entrega": str, "con_firma": texto_a_bool})
    cargar_relacion(client, "tiene_incidencia.csv", "tiene_incidencia", uids,
                    {"detectada_en_escaneo": int})
    cargar_relacion(client, "ocurre_en.csv", "ocurre_en", uids,
                    {"hora_local": str})
    print("Datos cargados correctamente.")


# ---------------------------------------------------------------------
# Consultas
# ---------------------------------------------------------------------

def imprimir(res):
    datos = json.loads(res.json)
    print(json.dumps(datos, indent=2, ensure_ascii=False))


def buscar_clientes_por_nombre(client, texto):
    # Índice de texto: nombre tiene @index(term), por eso se puede usar anyofterms
    query = """query buscar($texto: string) {
        clientes(func: anyofterms(nombre, $texto)) @filter(type(Cliente)) {
            id_cliente
            nombre
            tipo_cliente
            pais
            es_premium
        }
    }"""
    res = client.txn(read_only=True).query(query, variables={"$texto": texto})
    print(f"\n--- CLIENTES CON '{texto}' EN EL NOMBRE ---")
    imprimir(res)


def envios_por_valor(client, valor):
    # Índice numérico: valor_declarado_usd tiene @index(float), por eso se puede usar ge
    query = """query por_valor($valor: float) {
        envios(func: ge(valor_declarado_usd, $valor)) {
            numero_guia
            servicio
            estado
            valor_declarado_usd
        }
    }"""
    res = client.txn(read_only=True).query(query, variables={"$valor": str(valor)})
    print(f"\n--- ENVÍOS CON VALOR DECLARADO DE {valor} USD O MÁS ---")
    imprimir(res)


def rastrear_envio(client, guia):
    # Recorre el grafo desde un Envío hacia Cliente, Instalación, Vehículo y Empleado
    query = """query rastrear($guia: string) {
        envio(func: eq(numero_guia, $guia)) {
            numero_guia
            servicio
            estado
            remitente: ~envia {
                nombre
                pais
            }
            destinatario: dirigido_a @facets(direccion) {
                nombre
                pais
            }
            recorrido: pasa_por @facets(orderasc: orden, tipo_escaneo) {
                codigo
                ciudad
            }
            vehiculos: transportado_en @facets(orderasc: fecha, tramo) {
                matricula
                tipo
            }
            entregado_por: ~entrega @facets(fecha_entrega) {
                nombre
                rol
            }
        }
    }"""
    res = client.txn(read_only=True).query(query, variables={"$guia": guia})
    print(f"\n--- RASTREO DE LA GUÍA {guia} ---")
    imprimir(res)


def envios_por_instalacion(client, codigo):
    # Relación en reversa: pasa_por va de Envío a Instalación, con ~pasa_por se recorre al revés
    query = """query por_instalacion($codigo: string) {
        instalacion(func: eq(codigo, $codigo)) {
            codigo
            ciudad
            pais
            ubicacion
            envios: ~pasa_por @facets(tipo_escaneo) {
                numero_guia
                servicio
                estado
            }
        }
    }"""
    res = client.txn(read_only=True).query(query, variables={"$codigo": codigo})
    print(f"\n--- ENVÍOS QUE PASARON POR {codigo} ---")
    imprimir(res)


def incidencias_por_severidad(client):
    # Ordena de la más grave a la menos grave con orderdesc
    query = """{
        incidencias(func: type(Incidencia), orderdesc: severidad) {
            id_incidencia
            tipo
            severidad
            resuelta
            descripcion
            ocurre_en {
                codigo
                ciudad
            }
        }
    }"""
    res = client.txn(read_only=True).query(query)
    print("\n--- INCIDENCIAS ORDENADAS POR SEVERIDAD ---")
    imprimir(res)


def contar_envios_por_cliente(client):
    # count() cuenta las aristas de cada cliente
    query = """{
        clientes(func: type(Cliente)) {
            nombre
            pais
            envios_enviados: count(envia)
            envios_recibidos: count(~dirigido_a)
        }
    }"""
    res = client.txn(read_only=True).query(query)
    print("\n--- NÚMERO DE ENVÍOS POR CLIENTE ---")
    imprimir(res)


def envios_por_pagina(client, pagina, por_pagina=3):
    # Paginación: first dice cuántos traer y offset cuántos saltar
    query = """query paginar($first: int, $offset: int) {
        total(func: type(Envio)) {
            count(uid)
        }
        envios(func: type(Envio), orderasc: numero_guia, first: $first, offset: $offset) {
            numero_guia
            servicio
            estado
        }
    }"""
    offset = (pagina - 1) * por_pagina
    variables = {"$first": str(por_pagina), "$offset": str(offset)}
    res = client.txn(read_only=True).query(query, variables=variables)
    print(f"\n--- ENVÍOS, PÁGINA {pagina} ({por_pagina} POR PÁGINA) ---")
    imprimir(res)


# ---------------------------------------------------------------------
# Borrado
# ---------------------------------------------------------------------

def borrar_empleados_por_rol(client, rol):
    # Primero busca los empleados que cumplen la condición y luego los borra
    query = """query buscar($rol: string) {
        empleados(func: eq(rol, $rol)) @filter(type(Empleado)) {
            uid
            nombre
        }
    }"""
    res = client.txn(read_only=True).query(query, variables={"$rol": rol})
    empleados = json.loads(res.json)["empleados"]
    if len(empleados) == 0:
        print(f"No hay empleados con el rol '{rol}'.")
        return

    txn = client.txn()
    try:
        for empleado in empleados:
            txn.mutate(del_obj={"uid": empleado["uid"]})
            print(f"Empleado borrado: {empleado['nombre']} (UID {empleado['uid']})")
        txn.commit()
        print(f"Se borraron {len(empleados)} empleados con el rol '{rol}'.")
    finally:
        txn.discard()


def drop_data(client):
    # Borra todos los datos del grafo y conserva el esquema
    return client.alter(pydgraph.Operation(drop_op="DATA"))
