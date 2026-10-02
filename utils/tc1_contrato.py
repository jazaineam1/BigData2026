# -*- coding: utf-8 -*-
'''Contrato único del TC1 (S08): la fuente de verdad que leen el cuaderno, el validador
del estudiante, el validador docente, el checklist y las pruebas.

Si un requisito no está aquí, el validador no puede exigirlo. Si está aquí, el cuaderno
lo muestra en el checkpoint de su etapa. Así se evita el "contrato oculto" de la V7
(nombres que el validador exigía y el cuaderno nunca decía).

Plataformas verificadas el 2026-10-01 en su documentación vigente:
- Astra DB Serverless (plan Free): una base inactiva más de 48 h pasa a Hibernated y se
  borra tras 30 días hibernada; reanudarla tarda unos minutos.
- Neo4j AuraDB Free: se pausa tras 72 h sin actividad y se borra si sigue pausada 30 días.
- MongoDB Atlas Data Explorer: inserta documentos pegando JSON, pero no importa archivos;
  por eso la carga técnica se hace desde Colab, como en S04.
'''
from __future__ import annotations

import math

VERSION = "2026-10-02-tc1-v9"
VERSION_VISIBLE = "V9 · 2026-10-02"
E1_SCHEMA = "2026-10-02-tc1-e1-v9"

FECHA_LIMITE = "17 de octubre de 2026 · 11:59 p. m. · hora de Bogotá"
FECHA_LIMITE_ISO = "2026-10-17T23:59:59-05:00"
CORREO_DOCENTE = "jzaineam@ucentral.edu.co"
CHECKLIST_URL = "https://jazaineam1.github.io/BigData2026/assets/tutoriales/s08-secoppipeline.html"
COLAB_URL = "https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/Taller_Control_1.ipynb"

# ── Identidad y ventanas ──────────────────────────────────────────────────────
# Tabla explícita (no un hash): dos parejas nunca comparten datos y "p03" no cambia la
# ventana. P01, P02, P04, P05 y P06 conservan la ventana que les asignó la V7; P03 se
# movió a mar-abr porque la V7 la hacía coincidir con P02. P07–P12 cubren grupos de una
# persona. Cada snapshot toma los primeros registros desde el inicio de su ventana, así
# que los cortes que empiezan el día 1 de meses distintos no comparten datos.
VENTANAS = {
    "P01": ("2025-07-01T00:00:00.000", "2025-09-01T00:00:00.000"),
    "P02": ("2025-11-01T00:00:00.000", "2026-01-01T00:00:00.000"),
    "P03": ("2025-03-01T00:00:00.000", "2025-05-01T00:00:00.000"),
    "P04": ("2025-01-01T00:00:00.000", "2025-03-01T00:00:00.000"),
    "P05": ("2025-09-01T00:00:00.000", "2025-11-01T00:00:00.000"),
    "P06": ("2025-05-01T00:00:00.000", "2025-07-01T00:00:00.000"),
    "P07": ("2025-02-01T00:00:00.000", "2025-04-01T00:00:00.000"),
    "P08": ("2025-04-01T00:00:00.000", "2025-06-01T00:00:00.000"),
    "P09": ("2025-06-01T00:00:00.000", "2025-08-01T00:00:00.000"),
    "P10": ("2025-08-01T00:00:00.000", "2025-10-01T00:00:00.000"),
    "P11": ("2025-10-01T00:00:00.000", "2025-12-01T00:00:00.000"),
    "P12": ("2025-12-01T00:00:00.000", "2026-02-01T00:00:00.000"),
}
PAREJAS = list(VENTANAS)
SIN_SELECCION = "— selecciona —"

# ── Fuentes y contrato de datos (E1) ──────────────────────────────────────────
BASE_SOCRATA = "https://www.datos.gov.co/resource"
ENDPOINTS = {"procesos": "p6dx-8zbt", "contratos": "jbjy-vk9h"}

SELECT_PROCESOS = [
    "id_del_proceso", "id_del_portafolio", "entidad", "nit_entidad", "departamento_entidad",
    "ciudad_entidad", "fecha_de_publicacion_del", "precio_base", "modalidad_de_contratacion",
    "respuestas_al_procedimiento", "estado_del_procedimiento", "adjudicado",
    "nombre_del_proveedor", "nit_del_proveedor_adjudicado", "urlproceso",
]
SELECT_CONTRATOS = [
    "proceso_de_compra", "id_contrato", "estado_contrato", "tipo_de_contrato",
    "modalidad_de_contratacion", "fecha_de_firma", "nombre_entidad", "nit_entidad",
    "proveedor_adjudicado", "documento_proveedor", "tipodocproveedor", "es_grupo",
    "valor_del_contrato",
]
# Decisión de contrato de datos (verificada en las 12 ventanas): el 94 % de los contratos
# son con personas naturales, que contratan con una sola entidad y no forman red. Los
# consorcios y uniones temporales se crean para un solo proceso. Por eso el snapshot de
# contratos se limita a personas jurídicas que no son consorcio.
FILTRO_CONTRATOS = "tipodocproveedor = 'NIT' AND es_grupo = 'No'"
ORDER_PROCESOS = ("fecha_de_publicacion_del ASC,id_del_proceso ASC,"
                  "nit_del_proveedor_adjudicado ASC,nombre_del_proveedor ASC,:id ASC")
ORDER_CONTRATOS = "fecha_de_firma ASC,id_contrato ASC,:id ASC"
JOIN = {"procesos.id_del_portafolio": "contratos.proceso_de_compra"}

PAGE_SIZE = 250
TARGET_PROCESOS = 3000
TARGET_CONTRATOS = 4000
WORKERS_MIN, WORKERS_MAX = 2, 6
MIN_MATCHED_PROCESSES = 30
MIN_PARTICION_E4 = 10
MIN_COMPARTIDOS_ANCLA = 2
MIN_OTRAS_ENTIDADES = 2


def where_procesos(pareja: str) -> str:
    ini, fin = VENTANAS[pareja]
    return f"fecha_de_publicacion_del >= '{ini}' AND fecha_de_publicacion_del < '{fin}'"


def where_contratos(pareja: str) -> str:
    ini, fin = VENTANAS[pareja]
    return f"fecha_de_firma >= '{ini}' AND fecha_de_firma < '{fin}' AND {FILTRO_CONTRATOS}"


def contrato_de_datos(pareja: str) -> dict:
    '''Lo que E1 escribe en 00_dataset_contract.json y E1.1 compara.'''
    ini, fin = VENTANAS[pareja]
    return {
        "version": VERSION,
        "pareja": pareja,
        "ventana": {"inicio": ini, "fin": fin},
        "procesos": {"id": ENDPOINTS["procesos"], "grano": "fila de proceso de contratación",
                     "select": SELECT_PROCESOS, "where": where_procesos(pareja),
                     "order": ORDER_PROCESOS, "objetivo": TARGET_PROCESOS},
        "contratos": {"id": ENDPOINTS["contratos"], "grano": "contrato electrónico con persona jurídica",
                      "select": SELECT_CONTRATOS, "where": where_contratos(pareja),
                      "order": ORDER_CONTRATOS, "objetivo": TARGET_CONTRATOS},
        "join": JOIN,
        "page_size": PAGE_SIZE,
    }


# ── Modelo documental (E2) ────────────────────────────────────────────────────
GRANOS = [
    "Un documento por fila de la API (tal como llega)",
    "Un documento por proceso (id_del_proceso único)",
    "Un documento por contrato",
]
GRANO_CORRECTO = GRANOS[1]

ESTRATEGIAS_CARGA = [
    "insert_many (insertar todo otra vez)",
    "insert_many con índice único en id_proceso",
    "upsert por id_proceso (UpdateOne + upsert=True)",
]
ESTRATEGIA_CORRECTA = ESTRATEGIAS_CARGA[2]

# Rutas declaradas: las consultas de Atlas, el validador y la hoja de trucos usan estas.
CAMPO = {
    "id": "id_proceso",
    "precio_base": "proceso.precio_base",
    "anio": "proceso.anio",
    "departamento": "entidad.departamento",
    "cantidad": "contratos_resumen.cantidad",
    "valor": "contratos_resumen.valor_total",
}
CAMPOS_INDICE_ALINEADOS = {
    "contratos_resumen.valor_total": "orden de la consulta B y de la bandeja E3",
    "contratos_resumen.cantidad": "filtro de la consulta A y de la bandeja E3",
    "proceso.precio_base": "filtro de la consulta A y de la bandeja E3",
}
EJEMPLO_DOCUMENTO = {
    "id_proceso": "CO1.REQ.0000000",
    "entidad": {"nit": "899999034", "nombre": "ENTIDAD EJEMPLO", "departamento": "Antioquia", "ciudad": "Medellín"},
    "proceso": {"fecha_publicacion": "2025-03-01", "anio": 2025, "precio_base": 120000000.0,
                "modalidad": "Contratación directa", "estado": "Adjudicado"},
    "proveedor_adjudicado": {"nit": "900000000", "nombre": "PROVEEDOR EJEMPLO S.A.S."},
    "contratos_resumen": {"cantidad": 1, "valor_total": 118500000.0, "estados": ["En ejecución"]},
    "metadata_ingesta": {"pareja": "P03", "version": VERSION, "fuentes": ["p6dx-8zbt", "jbjy-vk9h"]},
}

ATLAS_DB = "tc1_bigdata"


def coleccion_oficial(pareja: str) -> str:
    return f"tc1_{pareja.lower()}"


def coleccion_ensayo(pareja: str) -> str:
    return f"tc1_{pareja.lower()}_ensayo"


def nombre_pipeline(pareja: str) -> str:
    return f"tc1-bandeja-{pareja.lower()}"


BANDEJA_MAX = 100
COLUMNAS_BANDEJA = ["id_proceso", "anio", "departamento", "entidad", "valor_contratos"]

# ── Cassandra query-first (E4) ────────────────────────────────────────────────
KEYSPACE_DEFECTO = "compras_claras"


def tabla_cassandra(pareja: str) -> str:
    return f"tc1_{pareja.lower()}_prioridades"


OPCIONES_PARTICION = {
    "(anio, departamento)": ["anio", "departamento"],
    "(departamento)": ["departamento"],
    "(id_proceso)": ["id_proceso"],
}
OPCIONES_CLUSTERING = {
    "valor_contratos DESC, id_proceso ASC": [("valor_contratos", "DESC"), ("id_proceso", "ASC")],
    "valor_contratos DESC": [("valor_contratos", "DESC")],
    "id_proceso ASC, valor_contratos DESC": [("id_proceso", "ASC"), ("valor_contratos", "DESC")],
}
OPCIONES_TIPO_VALOR = ["decimal", "double", "text"]
TIPOS_VALOR_NUMERICOS = {"decimal", "double", "bigint", "varint", "float"}
DISENO_CORRECTO = {
    "particion": "(anio, departamento)",
    "clustering": "valor_contratos DESC, id_proceso ASC",
}

# ── Grafo (E5) ────────────────────────────────────────────────────────────────
# Mismo vocabulario que S06 (MERGE, UNWIND $filas, ADJUDICADO_A), con el contrato como nodo.
GRAFO_ETIQUETAS = ["Entidad", "Contrato", "Proveedor"]
GRAFO_RELACIONES = ["FIRMA", "ADJUDICADO_A"]
PARAMETRO_ANCLA = "$nit_ancla"
PARAMETRO_FILAS = "$filas"

# ── Capturas (exactamente tres) ───────────────────────────────────────────────
CAPTURAS = {"E2": "E2_atlas.png", "E4": "E4_astra.png", "E5": "E5_neo4j.png"}
CAPTURA_MAX_BYTES = 8 * 1024 * 1024
CAPTURA_MIN_ANCHO = 600

# ── Artefactos por etapa (estructura del ZIP) ─────────────────────────────────
ARTEFACTOS = {
    "E1": ["00_dataset_contract.json", "01_acquisition_manifest.json", "01_benchmark_threads.json",
           "01_quality_report.json", "raw/procesos.parquet", "raw/contratos.parquet"],
    "E2": ["02_secop_integrado.parquet", "02_modelo_documental.json", "02_atlas_evidence.json",
           CAPTURAS["E2"]],
    "E3": ["03_pipeline_bandeja.json", "03_resultado_atlas.json", "03_bandeja_historica.csv"],
    "E4": ["04_datos_cassandra.csv", "04_modelo_cassandra.cql", "04_cassandra_evidence.json",
           CAPTURAS["E4"]],
    "E5": ["05_relaciones_grafo.csv", "05_neo4j_consultas.cypher", "05_resultado_relacional.csv",
           "05_neo4j_evidence.json", CAPTURAS["E5"]],
    "E6": ["06_decision_log.json", "06_informe_tecnico.md", "06_microdefensa_grupal.json"],
}
MANIFEST = "manifest_tc1.json"


def rutas(out):
    '''Estructura de la carpeta de trabajo = estructura del ZIP que recibe el docente.'''
    from pathlib import Path
    out = Path(out)
    raw = out / "E1" / "raw"
    return {
        "identidad": out / "identidad.json", "manifest": out / MANIFEST,
        "E1": out / "E1", "raw": raw,
        "pag_seq": raw / "pages" / "procesos" / "secuencial",
        "pag_thr": raw / "pages" / "procesos" / "concurrente",
        "pag_con": raw / "pages" / "contratos" / "oficial",
        "E2": out / "E2", "E3": out / "E3", "E4": out / "E4", "E5": out / "E5", "E6": out / "E6",
    }

# ── Rúbrica: 25/25/10/15/15/10 ────────────────────────────────────────────────
# visual = puntos que dependen de que el docente confirme la captura (niveles en NIVELES_VISUALES).
RUBRICA = [
    ("E1.1", "E1", 4, "Contrato de datos y consulta SoQL de tu pareja", "auto"),
    ("E1.2", "E1", 4, "Descarga secuencial completa y verificable", "auto"),
    ("E1.3", "E1", 8, "Descarga concurrente equivalente: mismos offsets, filas y hash", "auto"),
    ("E1.4", "E1", 9, "Trazabilidad: cache íntegro, RAW consolidado y cruce ≥30 procesos", "auto"),
    ("E2.1", "E2", 5, "Modelo documental: un documento por proceso", "auto"),
    ("E2.2", "E2", 7, "Carga en Atlas idempotente (dos cargas, cero duplicados)", "auto"),
    ("E2.3", "E2", 4, "Índices en Atlas: único en id_proceso + uno alineado con una consulta", "auto"),
    ("E2.4", "E2", 3, "Consulta A en Atlas: conteo correcto", "auto"),
    ("E2.5", "E2", 3, "Consulta B en Atlas: top 10 correcto y en orden", "auto"),
    ("E2.6", "E2", 3, "Evidencia Atlas completa + captura E2_atlas.png", "visual"),
    ("E3.1", "E3", 7, "Pipeline de Aggregations: estructura y resultado en orden", "auto"),
    ("E3.2", "E3", 3, "CSV de la bandeja: columnas, ≤100 filas y mismo orden", "auto"),
    ("E4.1", "E4", 5, "Datos cargados en Astra: COUNT de la partición correcto", "auto"),
    ("E4.2", "E4", 6, "Modelo query-first: PRIMARY KEY, clustering y tipo correctos", "auto"),
    ("E4.3", "E4", 4, "Ejecución real en Astra: top 10 correcto + captura E4_astra.png", "visual"),
    ("E5.1", "E5", 4, "Grafo cargado en Aura y entidad ancla correcta", "auto"),
    ("E5.2", "E5", 4, "Métrica relacional de Aura igual a la referencia", "auto"),
    ("E5.3", "E5", 5, "Archivo Cypher: carga, contexto, compartidos y ranking", "auto"),
    ("E5.4", "E5", 2, "Ejecución real en Aura: resultado + captura E5_neo4j.png", "visual"),
    ("E6.1", "E6", 5, "Tres decisiones ancladas a tus resultados + informe", "auto"),
    ("E6.2", "E6", 3, "Microdefensa: cobertura y límites de la red", "auto"),
    ("E6.3", "E6", 2, "Paquete completo y sin secretos", "auto"),
]
STAGE_MAX = {"E1": 25, "E2": 25, "E3": 10, "E4": 15, "E5": 15, "E6": 10}
STAGE_NOMBRE = {
    "E1": "Adquisición SECOP", "E2": "Modelo documental + MongoDB Atlas", "E3": "Producto analítico",
    "E4": "Cassandra query-first", "E5": "Neo4j / contexto relacional", "E6": "Decisiones y entrega",
}
# Niveles observables de los ítems con captura: (resultado correcto y captura válida,
# resultado correcto sin captura válida, resultado incorrecto).
NIVELES_VISUALES = {"E2.6": (3, 1, 0), "E4.3": (4, 2, 0), "E5.4": (2, 1, 0)}
CAPTURA_DE_ITEM = {"E2.6": "E2", "E4.3": "E4", "E5.4": "E5"}

# Lo que el estudiante ve cuando un control falla: qué revisar, sin regalar la respuesta.
FEEDBACK = {
    "E1.1": "Ejecuta E1 con tu PAREJA_ID de la lista: las páginas deben venir de la consulta oficial de tu ventana (no edites el plan de consulta).",
    "E1.2": "Repite la descarga secuencial hasta que el caché tenga todas las páginas y el número de filas sea el objetivo.",
    "E1.3": "Compara en igualdad de condiciones: mismos offsets, mismas filas y mismo hash; usa entre 2 y 6 workers. El speedup no se califica.",
    "E1.4": "Descarga los contratos, consolida el RAW y verifica que ningún .part ni chunk extra quede en el caché y que crucen ≥30 procesos.",
    "E2.1": "Elige el grano que deja un documento por id_del_proceso y vuelve a generar el modelo documental.",
    "E2.2": "Carga con una estrategia que no duplique al repetirse (la segunda carga no puede cambiar el conteo ni fallar).",
    "E2.3": "En Atlas → Indexes crea el índice único en id_proceso y un índice cuyo primer campo use una consulta del taller; luego vuelve a capturar.",
    "E2.4": "Escribe en Atlas el filtro con proceso.precio_base > 0 y contratos_resumen.cantidad > 0 y pega exactamente ese filtro.",
    "E2.5": "Ordena por contratos_resumen.valor_total descendente y desempata por id_proceso ascendente; limita a 10.",
    "E2.6": "Completa la evidencia de Atlas y sube E2_atlas.png (interfaz de Atlas, pipeline guardado y resultado, sin credenciales).",
    "E3.1": "El pipeline necesita $match con los dos filtros, $sort valor DESC e id_proceso ASC, $limit ≤ 100, y guardarse con el nombre pedido.",
    "E3.2": "Genera el CSV desde el resultado de Atlas: columnas pedidas, máximo 100 filas, mismo orden.",
    "E4.1": "Carga en Astra todas las filas del script y pega la salida del COUNT de la partición de prueba.",
    "E4.2": "La tabla debe nacer de la consulta: partición por los campos que filtras con igualdad y orden por valor dentro de la partición, sin ALLOW FILTERING.",
    "E4.3": "Pega la salida del SELECT que ejecutaste en Astra y sube E4_astra.png con la consulta y su resultado.",
    "E5.1": "Carga el grafo desde Colab, ejecuta en Aura la consulta de la ancla y captura los conteos.",
    "E5.2": "Completa el hueco de la consulta de ranking: cuenta entidades distintas, no filas.",
    "E5.3": "El archivo Cypher necesita la carga con UNWIND $filas y MERGE, el contexto, los compartidos (otra entidad distinta de la ancla) y el ranking.",
    "E5.4": "Ejecuta el ranking en Aura Query y sube E5_neo4j.png con la consulta y el resultado.",
    "E6.1": "Responde las tres decisiones mirando TUS salidas: segundos de tu descarga, el índice que creaste y el valor de la posición elegida.",
    "E6.2": "Ubica tu cobertura en su rango real y escoge el límite que tus datos sostienen.",
    "E6.3": "Faltan artefactos o hay un posible secreto: completa y vuelve a validar.",
}

# Lo que el cuaderno muestra en el checkpoint de cada etapa (mismo texto que valida el código).
CHECKPOINTS = {
    "E1": ["mismos offsets, mismas filas y mismo hash entre secuencial y concurrente (E1.3)",
           "caché sin .part ni chunks extra y con la firma de tu consulta oficial (E1.1, E1.2, E1.4)",
           f"al menos {MIN_MATCHED_PROCESSES} procesos con contrato cruzado (E1.4)"],
    "E2": ["un documento por id_del_proceso (E2.1)",
           "segunda carga sin cambio de conteo, sin errores y con 0 duplicados (E2.2)",
           "índice único en id_proceso + índice alineado con una consulta (E2.3)",
           "conteo de la consulta A y top 10 de la consulta B iguales a la referencia (E2.4, E2.5)",
           "02_atlas_evidence.json completo + E2_atlas.png (E2.6)"],
    "E3": ["pipeline guardado como tc1-bandeja-<pareja> con $match, $sort, $limit ≤ 100 (E3.1)",
           "resultado de Atlas igual a la referencia y en el mismo orden (E3.1)",
           "03_bandeja_historica.csv con id_proceso, anio, departamento, entidad, valor_contratos (E3.2)"],
    "E4": ["COUNT de la partición de prueba igual al esperado (E4.1)",
           "la PRIMARY KEY nace del WHERE de la consulta, ordena por valor dentro de la partición, usa un tipo numérico y no necesita ALLOW FILTERING (E4.2)",
           "top 10 de Astra igual a la referencia + E4_astra.png (E4.3)"],
    "E5": ["conteos del grafo en Aura iguales a los esperados y ancla correcta (E5.1)",
           "ranking de Aura igual a la referencia (E5.2)",
           "05_neo4j_consultas.cypher con carga, contexto, compartidos y ranking (E5.3)",
           "proveedor puente correcto + E5_neo4j.png (E5.4)"],
    "E6": ["tres decisiones ancladas a tus resultados + informe generado (E6.1)",
           "microdefensa: rango real de tu cobertura y límite de la red (E6.2)",
           "paquete completo y sin secretos (E6.3)"],
}

# ── E6: decisiones cerradas ancladas al resultado propio ──────────────────────
E6_DECISION_429 = [
    SIN_SELECCION,
    "Reducir workers y respetar Retry-After/backoff; descarto subir workers porque el 429 indica presión sobre la API",
    "Subir workers para terminar antes; descarto reintentar porque alarga la descarga",
    "Desactivar los reintentos para ver el error rápido; descarto el backoff porque no cambia el resultado",
    "Aceptar las filas que alcanzaron a llegar; descarto comparar el hash porque la descarga ya es concurrente",
]
E6_INDICE = [
    SIN_SELECCION,
    "contratos_resumen.valor_total · orden de la consulta B y de la bandeja",
    "contratos_resumen.cantidad · filtro de la consulta A",
    "proceso.precio_base · filtro de la consulta A",
    "entidad.departamento · no lo usa ninguna consulta de Atlas del TC1",
    "Ninguno: solo existe _id_",
]
E6_INDICE_CAMPO = {
    E6_INDICE[1]: "contratos_resumen.valor_total",
    E6_INDICE[2]: "contratos_resumen.cantidad",
    E6_INDICE[3]: "proceso.precio_base",
    E6_INDICE[4]: "entidad.departamento",
    E6_INDICE[5]: None,
}
E6_DATO_FALTANTE = [
    SIN_SELECCION,
    "Un precio de referencia del mercado para el mismo objeto (estudio de mercado o contratos comparables)",
    "Más contratos de la misma entidad dentro de la bandeja",
    "Un índice adicional en Atlas sobre valor_total",
    "La captura de pantalla de Atlas con la bandeja",
]
E6_RANGOS_COBERTURA = [SIN_SELECCION, "menos de 5 %", "entre 5 % y 10 %", "entre 10 % y 20 %",
                       "entre 20 % y 40 %", "más de 40 %"]
E6_CAUSA_COBERTURA = [
    SIN_SELECCION,
    "Mis procesos son de pocos días y casi todos de prestación de servicios con personas; mis contratos son solo con empresas y de otras fechas",
    "La descarga concurrente perdió filas de contratos",
    "El cruce debía hacerse por id_del_proceso y no por id_del_portafolio",
    "SECOP borra los contratos de los procesos recientes",
]
E6_LIMITE_RED = [
    SIN_SELECCION,
    "Que la entidad ancla actúe de forma anómala: su NIT puede agrupar varias sedes y solo veo contratos con empresas durante pocos días",
    "Nada: la red demuestra que los proveedores puente favorecen a la entidad ancla",
    "Que los proveedores puente estén coludidos entre sí",
    "Que la entidad con más proveedores compartidos sea la más irregular del país",
]
E6_CORRECTAS = {
    "decision_429": E6_DECISION_429[1],
    "dato_faltante": E6_DATO_FALTANTE[1],
    "causa_cobertura": E6_CAUSA_COBERTURA[1],
    "limite_red": E6_LIMITE_RED[1],
}


def rango_cobertura(cobertura: float) -> str:
    pct = 100.0 * float(cobertura)
    if pct < 5:
        return E6_RANGOS_COBERTURA[1]
    if pct < 10:
        return E6_RANGOS_COBERTURA[2]
    if pct < 20:
        return E6_RANGOS_COBERTURA[3]
    if pct < 40:
        return E6_RANGOS_COBERTURA[4]
    return E6_RANGOS_COBERTURA[5]


# ── Nota ──────────────────────────────────────────────────────────────────────
def nota_exacta(puntaje: float) -> float:
    return 1 + 4 * float(puntaje) / 100


def nota_registrada(puntaje: float) -> float:
    '''El PDA del repositorio registra notas en múltiplos de 0,1: redondeo al décimo, mitades hacia arriba.'''
    return math.floor(nota_exacta(puntaje) * 10 + 0.5 + 1e-9) / 10


# ── Secretos ──────────────────────────────────────────────────────────────────
# Los patrones no se encuentran a sí mismos: el validador puede escanear el cuaderno que
# los contiene sin falsos positivos.
PATRONES_SECRETOS = [
    ("URI de MongoDB con contraseña", r"mongodb(?:\+srv)?://[^\s:@/'\"]+:[^\s@/'\"<>]+@"),
    ("token de Astra", r"AstraCS:[A-Za-z0-9]{6,}:[0-9a-f]{20,}"),
    ("contraseña escrita", r"(?i)\b(?:password|passwd|pwd|contrase[ñn]a)\b\s*[:=]\s*['\"][^'\"\s<>]{6,}['\"]"),
    ("variable NEO4J_PASSWORD", r"(?i)NEO4J_PASSWORD\s*=\s*['\"]?[^\s'\"<>]{6,}"),
    ("App Token de Socrata", r"(?i)x-app-token['\"]?\s*[:=]\s*['\"][A-Za-z0-9]{8,}"),
]
ARCHIVOS_PROHIBIDOS = [r"(?i)^neo4j-.*\.txt$", r"(?i)^secure-connect.*\.zip$", r"(?i)credentials.*\.json$",
                       r"(?i)\.env$"]


def puntos_totales() -> int:
    return sum(p for _, _, p, _, _ in RUBRICA)


assert puntos_totales() == 100, "La rúbrica debe sumar 100"
assert {k: sum(p for _, e, p, _, _ in RUBRICA if e == k) for k in STAGE_MAX} == STAGE_MAX
assert len(CAPTURAS) == 3
assert len(set(VENTANAS.values())) == len(VENTANAS), "Dos parejas no pueden compartir ventana"
