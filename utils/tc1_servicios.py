# -*- coding: utf-8 -*-
'''Puentes provistos entre Colab y las plataformas del TC1.

Python no reemplaza a MongoDB Atlas, Astra ni Aura: el estudiante diseña y ejecuta sus
consultas en esas interfaces. Este módulo solo (1) carga datos que las interfaces no pueden
importar desde un archivo, (2) vuelve a ejecutar LA MISMA consulta que el estudiante pegó,
para capturar el resultado sin transcribirlo a mano, y (3) guarda la evidencia y empaqueta.

Ninguna función imprime URIs, usuarios ni contraseñas.
'''
from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path
from urllib.parse import quote_plus

import tc1_contrato as C

EN_COLAB = "google.colab" in sys.modules


def ahora_utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def escribir_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


def leer_json(path, defecto=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return defecto


def huella_archivo(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ── Consultas pegadas: JSON, literal de Python (Export Code) o sintaxis de shell ──
_LINEAS_IGNORADAS = re.compile(r"^\s*(import |from |client\s*=|db\s*=|coll\s*=|#|//)|MongoClient\(|mongodb(\+srv)?://")


def _literal_balanceado(t):
    '''Primer [ ... ] o { ... } completo del texto, respetando cadenas entre comillas.'''
    inicio = min([i for i in (t.find("["), t.find("{")) if i >= 0], default=-1)
    if inicio < 0:
        return t
    pila, comilla, escape = [], None, False
    for i in range(inicio, len(t)):
        ch = t[i]
        if comilla:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == comilla:
                comilla = None
            continue
        if ch in "'\"":
            comilla = ch
        elif ch in "[{":
            pila.append(ch)
        elif ch in "]}":
            pila.pop()
            if not pila:
                return t[inicio:i + 1]
    return t[inicio:]


def limpiar_texto_pegado(texto):
    '''Lo que se guarda como evidencia: sin líneas de conexión (que podrían traer la URI).'''
    return "\n".join(ln for ln in str(texto or "").splitlines() if not re.search(r"MongoClient\(|mongodb(\+srv)?://", ln))


def parse_consulta(texto):
    '''Convierte lo que el estudiante pegó desde Atlas en un objeto Python.

    Acepta JSON estricto (modo Texto de Aggregations o el filtro de Documents), el código de
    Export Code → Python 3 (con o sin .aggregate(...)) o la sintaxis de shell con claves sin comillas.
    '''
    if isinstance(texto, (dict, list)):
        return texto
    t = str(texto or "").strip()
    t = re.sub(r"^```[a-zA-Z0-9]*\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    lineas = [ln for ln in t.splitlines() if not _LINEAS_IGNORADAS.search(ln)]
    t = "\n".join(lineas).strip()
    if ".aggregate(" in t:
        t = t.split(".aggregate(", 1)[1]
    t = _literal_balanceado(t).strip()
    if not t:
        raise ValueError("Está vacío: pega la consulta que ejecutaste en Atlas.")
    try:
        return json.loads(t)
    except Exception:
        pass
    try:
        return ast.literal_eval(t)
    except Exception:
        pass
    relajado = re.sub(r"([{,]\s*)(\$?[A-Za-z_][\w.$]*)\s*:", r'\1"\2":', t)
    relajado = relajado.replace("'", '"')
    relajado = re.sub(r"\bTrue\b", "true", relajado)
    relajado = re.sub(r"\bFalse\b", "false", relajado)
    try:
        return json.loads(relajado)
    except Exception as exc:
        raise ValueError("No pude leer la consulta. Cópiala completa desde Atlas (modo Texto o Export Code → "
                         "Python 3), con llaves y corchetes balanceados.") from exc


def campos_de(obj, prefijo=""):
    '''Rutas de campo que aparecen en un filtro u orden de MongoDB (sin operadores $).'''
    salida = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).startswith("$"):
                salida |= campos_de(v, prefijo)
            else:
                salida.add(str(k))
                salida |= campos_de(v, prefijo)
    elif isinstance(obj, list):
        for x in obj:
            salida |= campos_de(x, prefijo)
    return salida


# ── MongoDB Atlas ─────────────────────────────────────────────────────────────
DIAGNOSTICO_ATLAS = [
    ("authentication failed", "usuario o contraseña del usuario de base de datos (Database Access en Atlas)"),
    ("bad auth", "usuario o contraseña del usuario de base de datos (Database Access en Atlas)"),
    ("timed out", "Network Access: tu IP o 0.0.0.0/0 debe estar permitida en Atlas"),
    ("serverselection", "Network Access o conectividad; espera 1 minuto si acabas de cambiar la IP permitida"),
    ("dns", "la URI está incompleta: cópiala completa desde Connect → Drivers"),
    ("invalid uri", "la URI está mal formada: debe empezar por mongodb+srv://"),
]


def conectar_atlas(uri=None, timeout_ms=10000):
    '''Conecta con getpass (la URI nunca se muestra) y comprueba con ping.'''
    from pymongo import MongoClient
    if uri is None:
        uri = getpass("Pega la URI de Atlas (Connect → Drivers). No se mostrará: ").strip()
    if "<db_password>" in uri or "<password>" in uri:
        clave = quote_plus(getpass("Contraseña del usuario de base de datos (no se mostrará): "))
        uri = uri.replace("<db_password>", clave).replace("<password>", clave)
    try:
        cliente = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
        cliente.admin.command("ping")
        version = str(cliente.server_info().get("version", ""))
    except Exception as exc:
        mensaje = str(exc).lower()
        causa = next((c for k, c in DIAGNOSTICO_ATLAS if k in mensaje), "revisa la URI, el usuario y Network Access")
        raise RuntimeError(f"No se pudo conectar a Atlas ({type(exc).__name__}). Qué revisar: {causa}.") from None
    return cliente, version


def _duplicados(col):
    return sum(1 for _ in col.aggregate([{"$group": {"_id": "$id_proceso", "n": {"$sum": 1}}},
                                         {"$match": {"n": {"$gt": 1}}}]))


def _aplicar(col, documentos, estrategia):
    from pymongo import UpdateOne
    from pymongo.errors import BulkWriteError
    copias = [json.loads(json.dumps(d)) for d in documentos]
    try:
        if estrategia == C.ESTRATEGIAS_CARGA[0]:
            col.insert_many(copias, ordered=False)
        elif estrategia == C.ESTRATEGIAS_CARGA[1]:
            col.create_index("id_proceso", unique=True, name="id_proceso_unico")
            col.insert_many(copias, ordered=False)
        elif estrategia == C.ESTRATEGIAS_CARGA[2]:
            col.bulk_write([UpdateOne({"id_proceso": d["id_proceso"]}, {"$set": d}, upsert=True) for d in copias],
                           ordered=False)
        else:
            raise ValueError("Elige una estrategia de la lista.")
        return None
    except BulkWriteError as exc:
        return f"BulkWriteError: {len(exc.details.get('writeErrors', []))} documentos rechazados por clave duplicada"


def ensayar_estrategia(db, pareja, documentos, estrategia):
    '''Prueba la estrategia en una colección de ensayo: dos cargas seguidas y lo que pasa.'''
    col = db[C.coleccion_ensayo(pareja)]
    col.drop()
    error_1 = _aplicar(col, documentos, estrategia)
    n1 = col.count_documents({})
    error_2 = _aplicar(col, documentos, estrategia)
    n2 = col.count_documents({})
    resultado = {"estrategia": estrategia, "documentos": len(documentos), "count_after_first": n1,
                 "count_after_second": n2, "duplicates_after_second": _duplicados(col),
                 "error_primera": error_1, "error_segunda": error_2}
    col.drop()
    return resultado


def cargar_oficial(db, pareja, documentos, estrategia, server_version):
    '''Carga oficial: vacía la colección (conserva sus índices) y carga dos veces.'''
    col = db[C.coleccion_oficial(pareja)]
    col.delete_many({})
    error_1 = _aplicar(col, documentos, estrategia)
    n1 = col.count_documents({})
    error_2 = _aplicar(col, documentos, estrategia)
    n2 = col.count_documents({})
    return {"capturado_por": "pymongo", "server_version": server_version, "db": C.ATLAS_DB,
            "coleccion": C.coleccion_oficial(pareja), "estrategia": estrategia, "n_documentos": len(documentos),
            "count_after_first": n1, "count_after_second": n2, "duplicates_after_second": _duplicados(col),
            "error_primera": error_1, "error_segunda": error_2, "momento_utc": ahora_utc()}


def capturar_indices(col):
    salida = []
    for nombre, info in col.index_information().items():
        salida.append({"nombre": nombre, "clave": [[str(k), int(v) if str(v).lstrip("-").isdigit() else str(v)]
                                                    for k, v in info.get("key", [])],
                       "unico": bool(info.get("unique", False))})
    return salida


def ejecutar_consulta_a(col, filtro):
    if not isinstance(filtro, dict):
        raise ValueError("La consulta A debe ser un filtro: un objeto entre llaves { }.")
    return int(col.count_documents(filtro))


def ejecutar_consulta_b(col, filtro, orden, limite=10):
    if not isinstance(orden, dict) or not orden:
        raise ValueError("El orden debe ser un objeto como {\"campo\": -1, \"otro\": 1}.")
    cursor = col.find(filtro or {}, {"_id": 0, "id_proceso": 1, "contratos_resumen.valor_total": 1})
    cursor = cursor.sort(list(orden.items())).limit(int(limite))
    filas = list(cursor)
    return [f.get("id_proceso") for f in filas], [((f.get("contratos_resumen") or {}).get("valor_total")) for f in filas]


ETAPAS_PROHIBIDAS = {"$out", "$merge", "$function", "$accumulator", "$where"}


def _etapas(pipeline):
    return [next(iter(e)) for e in pipeline if isinstance(e, dict) and e]


def ejecutar_pipeline(col, pipeline):
    if not isinstance(pipeline, list) or not all(isinstance(e, dict) and len(e) == 1 for e in pipeline):
        raise ValueError("Un pipeline es una lista de etapas: [ {\"$match\": ...}, {\"$sort\": ...}, ... ].")
    prohibidas = ETAPAS_PROHIBIDAS & set(_etapas(pipeline))
    if prohibidas:
        raise ValueError(f"El pipeline no puede escribir ni ejecutar código: quita {sorted(prohibidas)}.")
    filas = []
    for doc in col.aggregate(pipeline, maxTimeMS=30000):
        doc.pop("_id", None) if not isinstance(doc.get("_id"), (str, int, float)) else None
        filas.append(json.loads(json.dumps(doc, default=str)))
    return filas


# ── Astra: lectura de la salida de CQL Console (cqlsh) ────────────────────────
_SEPARADOR = re.compile(r"^\s*-+(\+-+)*\s*$")
_FILAS = re.compile(r"^\s*\((\d+) rows?\)\s*$")
_ERRORES = re.compile(r"(InvalidRequest|SyntaxException|Error from server|code=\d{4}|ConfigurationException|Unauthorized)", re.I)


def parse_cqlsh(texto):
    '''Tablas e errores de una salida de cqlsh/CQL Console pegada tal cual.'''
    lineas = str(texto or "").replace("\r", "").split("\n")
    tablas, errores = [], [ln.strip() for ln in lineas if _ERRORES.search(ln)]
    i = 0
    while i < len(lineas):
        if _SEPARADOR.match(lineas[i]) and i > 0 and lineas[i - 1].strip():
            columnas = [c.strip() for c in lineas[i - 1].split("|")]
            filas, j = [], i + 1
            while j < len(lineas) and not _FILAS.match(lineas[j]):
                if lineas[j].strip() and not lineas[j].strip().lower().startswith(("warnings", "token@", "cqlsh")):
                    filas.append([c.strip() for c in lineas[j].split("|")])
                elif not lineas[j].strip() and j + 1 < len(lineas) and not _FILAS.match(lineas[j + 1]):
                    break
                j += 1
            tablas.append({"columnas": columnas, "filas": filas})
            i = j
        i += 1
    return {"tablas": tablas, "errores": errores}


def evidencia_astra(texto):
    '''COUNT y los IDs del top 10 que mostró Astra.'''
    leido = parse_cqlsh(texto)
    count, ids = None, []
    for t in leido["tablas"]:
        cols = [c.lower() for c in t["columnas"]]
        if cols and cols[0] in ("count", "system.count(*)") and t["filas"]:
            try:
                count = int(t["filas"][0][0])
            except ValueError:
                pass
        if "id_proceso" in cols:
            k = cols.index("id_proceso")
            ids = [f[k] for f in t["filas"] if len(f) > k and f[k]]
    return {"count": count, "top10_ids": ids, "errores": leido["errores"]}


# ── Neo4j Aura ────────────────────────────────────────────────────────────────
def conectar_aura(uri=None, usuario=None, clave=None):
    from neo4j import GraphDatabase
    uri = uri or getpass("URI de tu instancia Aura (neo4j+s://...). No se mostrará: ").strip()
    usuario = usuario or (getpass("Usuario de Aura (Enter = neo4j): ").strip() or "neo4j")
    clave = clave or getpass("Contraseña de Aura (no se mostrará): ")
    try:
        driver = GraphDatabase.driver(uri, auth=(usuario, clave))
        driver.verify_connectivity()
    except Exception as exc:
        raise RuntimeError(f"No se pudo conectar a Aura ({type(exc).__name__}). Revisa que la instancia esté "
                           "Running (Aura Free se pausa tras 72 h sin uso) y que la URI y la contraseña sean las "
                           "del archivo que descargaste al crearla.") from None
    return driver


_ESCRITURA = re.compile(r"\b(CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|LOAD\s+CSV|FOREACH)\b", re.I)


def es_solo_lectura(consulta):
    sin_textos = re.sub(r"'[^']*'|\"[^\"]*\"", "''", str(consulta))
    return not _ESCRITURA.search(sin_textos)


def ejecutar_lectura(driver, consulta, parametros=None):
    if "____" in str(consulta):
        raise ValueError("La consulta todavía tiene el hueco ____: complétalo antes de ejecutarla.")
    if not es_solo_lectura(consulta):
        raise ValueError("Aquí solo se vuelven a ejecutar consultas de lectura (sin CREATE, MERGE, SET ni DELETE).")
    with driver.session() as s:
        return s.execute_read(lambda tx: [r.data() for r in tx.run(consulta, parametros or {})])


def cargar_grafo(driver, filas, pareja, lote=500):
    '''Restricciones + UNWIND $filas con MERGE (patrón de S06). Repetir la carga no duplica.'''
    import tc1_secop as S
    with driver.session() as s:
        for q in S.CYPHER_RESTRICCIONES:
            try:
                s.run(q).consume()
            except Exception as exc:
                if "equivalent" not in str(exc).lower() and "already exists" not in str(exc).lower():
                    raise
        ids = [f["id_contrato"] for f in filas]
        borrados = s.run("MATCH (c:Contrato) WHERE c.pareja IS NOT NULL AND NOT c.id IN $ids "
                         "DETACH DELETE c RETURN count(*) AS n", ids=ids).single()["n"]
        datos = [{**f, "pareja": pareja} for f in filas]
        for i in range(0, len(datos), lote):
            s.execute_write(lambda tx, b=datos[i:i + lote]: tx.run(S.CYPHER_CARGA, filas=b).consume())
    return {"contratos_previos_eliminados": int(borrados), "filas_enviadas": len(filas)}


def conteos_aura(driver, ids):
    filas = ejecutar_lectura(driver, (
        "MATCH (e:Entidad)-[f:FIRMA]->(c:Contrato)-[a:ADJUDICADO_A]->(p:Proveedor) WHERE c.id IN $ids "
        "RETURN count(DISTINCT e) AS entidades, count(DISTINCT c) AS contratos, count(DISTINCT p) AS proveedores, "
        "count(DISTINCT f) AS firma, count(DISTINCT a) AS adjudicado_a"), {"ids": list(ids)})
    return {k: int(v) for k, v in filas[0].items()}


# ── Capturas de pantalla ──────────────────────────────────────────────────────
def info_imagen(contenido: bytes):
    '''(formato, ancho, alto) leyendo la cabecera; sin depender de librerías externas.'''
    if contenido[:8] == b"\x89PNG\r\n\x1a\n" and len(contenido) > 24:
        return "png", int.from_bytes(contenido[16:20], "big"), int.from_bytes(contenido[20:24], "big")
    if contenido[:3] == b"\xff\xd8\xff":
        i = 2
        while i + 9 < len(contenido):
            if contenido[i] != 0xFF:
                i += 1
                continue
            marca = contenido[i + 1]
            largo = int.from_bytes(contenido[i + 2:i + 4], "big")
            if marca in (0xC0, 0xC1, 0xC2):
                return "jpeg", int.from_bytes(contenido[i + 7:i + 9], "big"), int.from_bytes(contenido[i + 5:i + 7], "big")
            i += 2 + largo
        return "jpeg", 0, 0
    return None, 0, 0


def validar_captura(path):
    p = Path(path)
    if not p.exists():
        return False, "no existe"
    contenido = p.read_bytes()
    formato, ancho, _ = info_imagen(contenido)
    if formato != "png":
        return False, "no es una imagen PNG válida"
    if len(contenido) > C.CAPTURA_MAX_BYTES:
        return False, "pesa más de 8 MB"
    if ancho < C.CAPTURA_MIN_ANCHO:
        return False, f"mide {ancho} px de ancho; se necesitan al menos {C.CAPTURA_MIN_ANCHO} para leerla"
    return True, f"PNG de {ancho} px de ancho"


def guardar_captura(out, etapa, ruta=None):
    '''Sube (Colab) o copia (local) la captura y la guarda con el nombre exigido.'''
    nombre = C.CAPTURAS[etapa]
    if ruta:
        contenido = Path(ruta).read_bytes()
    elif EN_COLAB:
        from google.colab import files
        subido = files.upload()
        if not subido:
            raise RuntimeError("No se subió ningún archivo.")
        contenido = next(iter(subido.values()))
    else:
        raise RuntimeError("Fuera de Colab indica la ruta del archivo: guardar_captura(OUT, etapa, ruta='...').")
    formato, _, _ = info_imagen(contenido)
    if formato == "jpeg":
        from io import BytesIO
        from PIL import Image
        buffer = BytesIO()
        Image.open(BytesIO(contenido)).convert("RGB").save(buffer, "PNG")
        contenido = buffer.getvalue()
    elif formato != "png":
        raise ValueError("La captura debe ser PNG o JPG.")
    destino = Path(out) / etapa / nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(contenido)
    return destino, validar_captura(destino)


# ── Persistencia en Drive, notebook y paquete ─────────────────────────────────
def montar_drive():
    from google.colab import drive
    drive.mount("/content/drive")
    return Path("/content/drive/MyDrive")


def carpeta_drive(raiz, pareja):
    return Path(raiz) / f"TC1_BIGDATA_{pareja}"


def guardar_avance(out, pareja, raiz_drive):
    if raiz_drive is None:
        return None
    destino = carpeta_drive(raiz_drive, pareja) / "avance"
    destino.mkdir(parents=True, exist_ok=True)
    tmp = Path(shutil.make_archive(str(Path("/tmp") / f"avance_tc1_{pareja}"), "zip", root_dir=str(out)))
    final = destino / f"avance_tc1_{pareja}.zip"
    shutil.copyfile(tmp, final)
    return final


def restaurar_avance(out, pareja, raiz_drive):
    if raiz_drive is None:
        return False
    zip_avance = carpeta_drive(raiz_drive, pareja) / "avance" / f"avance_tc1_{pareja}.zip"
    if zip_avance.exists() and not (Path(out) / "E1" / "01_acquisition_manifest.json").exists():
        Path(out).mkdir(parents=True, exist_ok=True)
        shutil.unpack_archive(str(zip_avance), str(out), "zip")
        return True
    return False


def notebook_actual():
    '''El cuaderno con sus salidas, tal como lo ve Colab ahora.'''
    from google.colab import _message
    r = _message.blocking_request("get_ipynb", request="", timeout_sec=60)
    return r.get("ipynb", r) if isinstance(r, dict) else r


def prohibido(nombre):
    return any(re.search(p, nombre) for p in C.ARCHIVOS_PROHIBIDOS)


def empaquetar(out, pareja, destino_dir=None):
    out = Path(out)
    destino_dir = Path(destino_dir or out.parent)
    zip_path = destino_dir / f"TC1_{pareja}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(out.rglob("*")):
            if p.is_file() and not prohibido(p.name) and "__pycache__" not in p.parts:
                zf.write(p, arcname=p.relative_to(out).as_posix())
    return zip_path
