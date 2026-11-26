#!/usr/bin/env python3
import os

import pydgraph

import model

DGRAPH_URI = os.getenv('DGRAPH_URI', 'localhost:9080')


def print_menu():
    mm_options = {
        1: "Cargar datos de los CSV",
        2: "Buscar clientes por nombre",
        3: "Envíos con valor declarado mínimo",
        4: "Rastrear un envío por número de guía",
        5: "Envíos que pasaron por una instalación",
        6: "Incidencias ordenadas por severidad",
        7: "Número de envíos por cliente",
        8: "Ver envíos por página",
        9: "Borrar empleados por rol",
        10: "Borrar todos los datos",
        11: "Salir",
    }
    print("\n===== RED LOGÍSTICA DHL EXPRESS =====")
    for key in mm_options.keys():
        print(key, '--', mm_options[key])


# Conexión directa con el servidor Dgraph usando gRPC.
def create_client_stub():
    return pydgraph.DgraphClientStub(DGRAPH_URI)


# Crea el cliente principal de Dgraph: realizar operaciones de alto nivel como queries, mutaciones y transacciones.
def create_client(client_stub):
    return pydgraph.DgraphClient(client_stub)


def close_client_stub(client_stub):
    client_stub.close()


def pedir_numero(mensaje, tipo):
    # Pide un número y lo vuelve a pedir si el usuario escribe otra cosa
    while True:
        try:
            return tipo(input(mensaje))
        except ValueError:
            print("Escribe un número válido.")


def ejecutar_opcion(client, option):
    if option == 1:
        model.cargar_datos(client)
    elif option == 2:
        texto = input("Palabra del nombre (ej. GmbH): ")
        model.buscar_clientes_por_nombre(client, texto)
    elif option == 3:
        valor = pedir_numero("Valor mínimo en USD (ej. 1000): ", float)
        model.envios_por_valor(client, valor)
    elif option == 4:
        guia = input("Número de guía (ej. 1234567890): ")
        model.rastrear_envio(client, guia)
    elif option == 5:
        codigo = input("Código de la instalación (ej. CVG): ").upper()
        model.envios_por_instalacion(client, codigo)
    elif option == 6:
        model.incidencias_por_severidad(client)
    elif option == 7:
        model.contar_envios_por_cliente(client)
    elif option == 8:
        pagina = pedir_numero("Número de página (ej. 1): ", int)
        if pagina < 1:
            print("La página tiene que ser 1 o mayor.")
        else:
            model.envios_por_pagina(client, pagina)
    elif option == 9:
        rol = input("Rol a borrar (mensajero, piloto, operador, agente aduanal): ")
        model.borrar_empleados_por_rol(client, rol)
    elif option == 10:
        confirm = input("¿Seguro que quieres borrar todos los datos? (s/n): ")
        if confirm.lower() == "s":
            model.drop_data(client)
            print("Se borraron todos los datos. El schema se conserva.")
        else:
            print("Operación cancelada.")
    else:
        print("Opción no válida.")


def main():
    # Inicializar Client Stub y Dgraph Client
    client_stub = create_client_stub()
    client = create_client(client_stub)

    try:
        # Crear schema
        model.set_schema(client)
        print("Schema creado correctamente.")

        while True:
            print_menu()
            option = pedir_numero('Elige una opción: ', int)
            if option == 11:
                print("Hasta luego.")
                break
            try:
                ejecutar_opcion(client, option)
            except Exception as e:
                # Si Dgraph regresa un error, se muestra y se vuelve al menú
                print('Error: {}'.format(e))
    finally:
        close_client_stub(client_stub)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error: {}'.format(e))
