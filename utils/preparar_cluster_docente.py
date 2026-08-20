# -*- coding: utf-8 -*-
"""
utils/preparar_cluster_docente.py
=================================
Carga el clúster M0 del docente para que sirva de red de seguridad.

Para qué existe
---------------
En la sesión 4 cada pareja se conecta a SU propio Atlas. Pero con 0/10 de
experiencia previa en nube, algunas cuentas van a fallar: contraseña con
símbolos, acceso de red mal configurado, cluster todavía aprovisionando.
Ese estudiante NO puede quedarse sin laboratorio.

Este script deja el clúster del docente listo: una base por pareja, con los
datos ya cargados, para entregar usuario y contraseña en pantalla y seguir.

Qué hace exactamente
--------------------
- Crea una base por pareja: `equipo_01` ... `equipo_06`.
- En cada una carga la colección `noticias` con las 987 noticias del curso.
- Es idempotente: se puede volver a correr sin duplicar nada.
- NO crea usuarios: los usuarios de base de datos se crean en la consola de
  Atlas, a mano, porque la API de administración exige claves de API de
  organización que no vale la pena aprovisionar para esto.

Antes de correrlo
-----------------
1. Crea el clúster M0 (ver `.local-docente/Runbook_cluster_docente.md`).
2. Crea los seis usuarios en Database Access, cada uno con permiso
   `readWrite` SOLO sobre su base. El runbook trae la tabla.
3. Abre Network Access a `0.0.0.0/0`.
4. Exporta la cadena de conexión de administrador:

       set MONGODB_ADMIN_URI=mongodb+srv://admin:CLAVE@cluster0.xxxx.mongodb.net

Uso
---
    python utils/preparar_cluster_docente.py --equipos 6

Verificación
------------
Al terminar imprime, por cada base, cuántos documentos quedaron. Los seis
números deben ser iguales.
"""

import argparse
import json
import os
import sys
import urllib.request

DATOS = (
    "https://raw.githubusercontent.com/jazaineam1/BigData2026/main/"
    "Datos/noticias_contratacion_2026.json"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--equipos", type=int, default=6, help="cuantas bases crear")
    ap.add_argument("--uri", default=os.environ.get("MONGODB_ADMIN_URI"),
                    help="cadena de conexion de administrador del cluster docente")
    args = ap.parse_args()

    if not args.uri:
        print("Falta la cadena de conexion.")
        print("Pasa --uri o define la variable de entorno MONGODB_ADMIN_URI.")
        return 1

    try:
        from pymongo import MongoClient
    except ImportError:
        print("Falta pymongo. Instala con:  pip install pymongo")
        return 1

    print("1/3 Descargando las noticias del curso...")
    with urllib.request.urlopen(DATOS, timeout=120) as r:
        noticias = json.loads(r.read().decode("utf-8"))
    print(f"    {len(noticias)} documentos")

    print("2/3 Conectando al cluster docente...")
    client = MongoClient(args.uri, serverSelectionTimeoutMS=15000)
    client.admin.command("ping")
    print("    Version del servidor:", client.server_info()["version"])

    print(f"3/3 Cargando {args.equipos} bases de equipo...")
    resultados = []
    for i in range(1, args.equipos + 1):
        nombre = f"equipo_{i:02d}"
        col = client[nombre]["noticias"]
        col.delete_many({})            # idempotente
        col.insert_many(noticias)
        n = col.count_documents({})
        resultados.append((nombre, n))
        print(f"    {nombre}: {n} documentos")

    print()
    print("=" * 60)
    iguales = len({n for _, n in resultados}) == 1
    print("LISTO." if iguales else "REVISAR: las bases no quedaron iguales.")
    print(f"Cada equipo se conecta a su base: {resultados[0][0]} ... {resultados[-1][0]}")
    print()
    print("Recuerda: el plan M0 estrangula a las 100 operaciones por segundo.")
    print("Si seis parejas escriben a la vez, avisales que carguen por lotes")
    print("con insert_many y no en un bucle de insert_one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
