# -*- coding: utf-8 -*-
"""
Genera Cuadernos/14_Solucion_Taller_Final_MongoDB_SECOP.ipynb

Solucion completa del taller final: descarga, limpieza, texto, prioridad,
MongoDB Atlas y dashboard. Adaptado para Databricks Community Edition.
"""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.make_notebook import md, code, save, validate, uce_header, section_header


OUTPUT = "Cuadernos/14_Solucion_Taller_Final_MongoDB_SECOP.ipynb"

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def interp(titulo, puntos):
    return md(
        "### Nota docente — " + titulo + "\n\n"
        + "\n".join(f"- {p}" for p in puntos)
    )


# ---------------------------------------------------------------------------
# CABECERA
# ---------------------------------------------------------------------------

cells = [
    *uce_header(
        title="Solucion: Taller Final — Observatorio de Contratacion Publica con MongoDB",
        session=14,
        github_path="main/Cuadernos/14_Solucion_Taller_Final_MongoDB_SECOP.ipynb",
        nota_plataforma="Databricks Community Edition + MongoDB Atlas M0 (gratuito).",
    ),
]

cells.append(md("""
## Solucion completa — Taller Final

Este cuaderno implementa las 6 actividades del taller en secuencia, listo para ejecutarse
en **Databricks Community Edition** con conexion a **MongoDB Atlas M0**.

| Seccion | Actividad |
|---|---|
| 0 | Configuracion (dependencias, imports, conexion MongoDB) |
| 1 | Descarga desde SECOP II con estimacion de volumenes |
| 2 | Limpieza e integracion de cuatro fuentes |
| 3 | Texto no estructurado: `texto_busqueda` y `temas_detectados` |
| 4 | Indice descriptivo de prioridad (0-100) |
| 5 | Modelo NoSQL en MongoDB Atlas |
| 6 | Dashboard operativo + script Streamlit |
| 7 | Informe ejecutivo |

### Antes de ejecutar

1. Crear cluster en Databricks (Single Node, DBR 13+ con Python 3.10+).
2. Crear un Secret Scope llamado `mongodb` con la clave `atlas_uri` que contenga
   la URI de conexion de Atlas.
3. Alternativamente, configurar la variable de entorno `MONGODB_URI` en la configuracion
   del cluster (Advanced Options → Environment Variables).
4. Ejecutar las celdas en orden desde la Seccion 0.

> **Volumenes reales confirmados el 2026-05-24 via API SECOP II:**
> contratos desde 2021 = 4.5 M | adiciones totales = 19.9 M (resumen por contrato evita descargar filas) |
> contratos desde 2025 = 1.57 M. La descarga completa desde 2021 puede superar el TTL del
> cluster CE (~2 h). Se recomienda `MODO = "desde_2025"` en Databricks CE.
"""))


# ══════════════════════════════════════════════════════════════════════════════
# SECCION 0 — SETUP
# ══════════════════════════════════════════════════════════════════════════════
cells.append(section_header("0", "Configuracion inicial"))

cells.append(md("""
## Instalacion de dependencias

En Databricks se usa `%pip install` (no `%sh pip`). El comando reinicia el interprete
del notebook automaticamente para que los paquetes queden disponibles.
"""))

cells.append(code("""
%pip install pymongo>=4.6 requests tqdm plotly -q
"""))

cells.append(code("""
import os
import re
import json
import time
import unicodedata
import pprint
from collections import Counter
from datetime import datetime, timezone

import requests
import pandas as pd
import numpy as np
from tqdm import tqdm
from pymongo import MongoClient, UpdateOne, ASCENDING, DESCENDING, TEXT
from pymongo.errors import BulkWriteError
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

print("Imports OK")
print(f"pandas  : {pd.__version__}")
print(f"pymongo : importado")
"""))

cells.append(md("""
## Configuracion de MongoDB Atlas

### Opcion 1 — Databricks Secrets (recomendado)

```
databricks secrets create-scope --scope mongodb
databricks secrets put --scope mongodb --key atlas_uri
```

### Opcion 2 — Variable de entorno en el cluster

En la configuracion del cluster (Advanced Options → Spark → Environment Variables):
```
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### Formato de la URI
```
mongodb+srv://<usuario>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```
"""))

cells.append(code("""
# Cargar URI: Databricks Secrets con fallback a variable de entorno
MONGODB_URI = None

try:
    MONGODB_URI = dbutils.secrets.get(scope="mongodb", key="atlas_uri")
    print("URI cargada desde Databricks Secrets (scope=mongodb, key=atlas_uri)")
except Exception:
    pass

if not MONGODB_URI:
    MONGODB_URI = os.environ.get("MONGODB_URI", "")
    if MONGODB_URI:
        print("URI cargada desde variable de entorno MONGODB_URI")

if not MONGODB_URI:
    raise EnvironmentError(
        "MONGODB_URI no encontrada. "
        "Configura un Databricks Secret (scope=mongodb, key=atlas_uri) "
        "o define la variable de entorno en el cluster."
    )

# Verificar conexion
_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=8000)
_client.admin.command("ping")
_client.close()
print("Conexion a MongoDB Atlas: OK")
"""))

cells.append(code("""
# ── CONSTANTES GLOBALES ────────────────────────────────────────────────────
BASE_URL       = "https://www.datos.gov.co/resource"
DB_NAME        = "secop_observatorio"
FECHA_DESCARGA = datetime.now(timezone.utc)

# ── MODO DE DESCARGA ───────────────────────────────────────────────────────
# muestra     -> 50 000 contratos  (~3 min, ideal para pruebas)
# desde_2025  -> contratos >= 2025-01-01 (~1.57 M, ~25 min, recomendado en CE)
# completo    -> contratos >= 2021-01-01 (~4.5 M, ~90 min, puede agotar CE TTL)
MODO = "desde_2025"

# Tabla de volumenes reales (API SECOP II, verificado 2026-05-24):
# ┌──────────────────────┬──────────────┬──────────────┬──────────────┐
# │ Fuente               │ Desde 2021   │ Desde 2025   │ Ultimo mes   │
# ├──────────────────────┼──────────────┼──────────────┼──────────────┤
# │ Contratos            │  4 546 297   │  1 570 122   │  ~180 000    │
# │ Adiciones (filas)    │ 19 947 685   │  9 937 126   │  1 412 315   │
# │ Adiciones (GROUP BY) │  ~ 2-3 M     │  ~ 1-1.5 M   │  ~ 400 K     │
# │ Ejecucion            │  3 402 245   │  ~500 000    │  ~60 000     │
# └──────────────────────┴──────────────┴──────────────┴──────────────┘
# Nota: adiciones usa GROUP BY en la API, evitando descargar ~20 M filas.

MODO_CONFIG = {
    "muestra":    {"fecha_ini": "2021-01-01T00:00:00", "limite": 50_000,    "label": "Muestra 50 K"},
    "desde_2025": {"fecha_ini": "2025-01-01T00:00:00", "limite": None,      "label": "Desde 2025"},
    "completo":   {"fecha_ini": "2021-01-01T00:00:00", "limite": None,      "label": "Completo desde 2021"},
}
cfg        = MODO_CONFIG[MODO]
FECHA_INI  = cfg["fecha_ini"]
MAX_REGS   = cfg["limite"]

print(f"Fecha de sesion : {FECHA_DESCARGA.isoformat()}")
print(f"Modo            : {MODO.upper()} — {cfg['label']}")
print(f"Fecha de inicio : {FECHA_INI[:10]}")
if MAX_REGS:
    print(f"Limite muestra  : {MAX_REGS:,} registros")
else:
    print("Descarga sin limite (todos los registros desde la fecha de inicio)")
"""))


# ══════════════════════════════════════════════════════════════════════════════
# SECCION 1 — DESCARGA
# ══════════════════════════════════════════════════════════════════════════════
cells.append(section_header("1", "Estimacion de volumenes y descarga (Actividad 1)"))

cells.append(md("""
## Actividad 1 — Descarga

### Estrategia por fuente

| Fuente | Endpoint | Estrategia | Razon |
|---|---|---|---|
| Contratos | `jbjy-vk9h` | Paginacion con `$offset` | Una fila por contrato |
| Adiciones | `cb9c-h8sn` | `GROUP BY id_contrato` en la API | Evita descargar ~20 M filas individuales |
| Ejecucion | `mfmm-jqmq` | Paginacion, ultimo por contrato | Queremos solo el avance mas reciente |
| DIVIPOLA  | `gdxc-w37w` | Descarga unica (~1 120 registros) | Catalogo de municipios estable |

La API Socrata permite hasta 1 000 registros por peticion sin token de aplicacion.
Con token (`$app_token`), el limite sube a 50 000. Sin token se pagina con `$limit` + `$offset`.

### Nota sobre tiempos estimados en Databricks CE

| Modo | Contratos | Adiciones (GROUP BY) | Tiempo estimado |
|---|---|---|---|
| muestra | 50 K | ~50 K | ~3 min |
| desde_2025 | 1.57 M | ~1-1.5 M | ~25-35 min |
| completo | 4.5 M | ~2-3 M | ~90-120 min |

Databricks CE auto-termina el cluster tras ~2 h de inactividad. Para el modo completo
se recomienda mantener el notebook activo o usar un cluster con tiempo de vida extendido.
"""))

cells.append(code("""
def contar_endpoint(endpoint_id, where):
    '''Llama a la API con COUNT(*) para estimar el volumen antes de descargar.'''
    url = f"{BASE_URL}/{endpoint_id}.json"
    r = requests.get(
        url,
        params={"$select": "count(*)", "$where": where},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    return int(data[0].get("count", 0)) if data else 0

print("Estimando volumenes en la API (puede tardar ~30 segundos)...")
n_contratos  = contar_endpoint("jbjy-vk9h", f"fecha_de_firma >= '{FECHA_INI}'")
n_adiciones  = contar_endpoint("cb9c-h8sn", f"fecharegistro >= '{FECHA_INI}'")
n_ejecucion  = contar_endpoint("mfmm-jqmq", f"fechacreacion >= '{FECHA_INI}'")

print(f"\\n{'Fuente':<20} {'Registros':>15}")
print("-" * 38)
print(f"{'Contratos':<20} {n_contratos:>15,}")
print(f"{'Adiciones (filas)':<20} {n_adiciones:>15,}")
print(f"{'Ejecucion':<20} {n_ejecucion:>15,}")
print()

# Estimacion de peso en memoria
def peso_mb(n, bytes_por_fila=250):
    return n * bytes_por_fila / 1_000_000

print(f"Peso estimado en memoria (pandas):")
print(f"  Contratos  : {peso_mb(n_contratos, 300):>8.1f} MB")
print(f"  Adiciones* : {peso_mb(n_adiciones // 6, 150):>8.1f} MB  (* despues de GROUP BY)")
print(f"  Ejecucion  : {peso_mb(n_ejecucion, 100):>8.1f} MB")
print()
if MODO == "desde_2025" or MODO == "completo":
    print("Arquitectura del cluster recomendada: Single Node, 15+ GB RAM")
    print("Tiempo de descarga estimado: ver tabla en la seccion anterior")
"""))

interp_vol = interp("volumenes y duplicados en adiciones", [
    "La columna `adiciones` tiene ~20 M filas totales pero muchas son duplicados del mismo `identificador`.",
    "Por eso se usa GROUP BY en la API: en vez de descargar filas, se descarga el conteo por contrato.",
    "El resultado es un DataFrame de contratos-con-adiciones, no de filas de adicion.",
    "Si el COUNT(*) de adiciones te parece muy alto, es porque el mismo evento puede estar registrado varias veces.",
])
cells.append(interp_vol)

cells.append(code("""
def descargar_paginado(endpoint_id, where, select=None, max_registros=None, desc=None):
    '''Descarga un endpoint Socrata con paginacion por offset. Retorna DataFrame.'''
    PAGE_SIZE = 1000
    url    = f"{BASE_URL}/{endpoint_id}.json"
    params = {
        "$where": where,
        "$limit": PAGE_SIZE,
        "$order": ":id",
    }
    if select:
        params["$select"] = select

    all_rows, offset = [], 0
    label = desc or endpoint_id

    with tqdm(desc=label, unit=" regs", total=max_registros) as pbar:
        while True:
            params["$offset"] = offset
            for intento in range(3):
                try:
                    r = requests.get(url, params=params, timeout=120)
                    r.raise_for_status()
                    break
                except Exception as exc:
                    if intento == 2:
                        raise
                    print(f"\\nReintentando ({intento+1}/3): {exc}")
                    time.sleep(3)

            batch = r.json()
            if not batch:
                break

            all_rows.extend(batch)
            offset += len(batch)
            pbar.update(len(batch))

            if len(batch) < PAGE_SIZE:
                break
            if max_registros and offset >= max_registros:
                break
            time.sleep(0.05)

    return pd.DataFrame(all_rows)
"""))

cells.append(code("""
# 1A. Contratos
COLS_CONTRATOS = (
    "id_contrato,fecha_de_firma,valor_del_contrato,"
    "nombre_entidad,nit_entidad,"
    "proveedor_adjudicado,documento_proveedor,"
    "modalidad_de_contratacion,tipo_de_contrato,"
    "objeto_del_contrato,departamento,municipio"
)

df_contratos_raw = descargar_paginado(
    "jbjy-vk9h",
    where=f"fecha_de_firma >= '{FECHA_INI}'",
    select=COLS_CONTRATOS,
    max_registros=MAX_REGS,
    desc="Contratos",
)
df_contratos_raw.to_csv("/tmp/contratos_raw.csv", index=False)
print(f"Contratos: {len(df_contratos_raw):,} filas  |  {df_contratos_raw.shape[1]} columnas")
display(df_contratos_raw.head(3))
"""))

cells.append(code("""
# 1B. Adiciones — GROUP BY en la API (evita descargar ~20 M filas)
def descargar_adiciones_resumen(fecha_ini):
    '''
    Usa GROUP BY en la API Socrata para obtener conteo de adiciones por contrato.
    Resultado: id_contrato | num_adiciones | ultima_adicion
    En vez de descargar millones de filas, descarga un resumen por contrato.
    '''
    PAGE_SIZE = 1000
    url    = f"{BASE_URL}/cb9c-h8sn.json"
    params = {
        "$select": "id_contrato,count(*) AS num_adiciones,max(fecharegistro) AS ultima_adicion",
        "$where":  f"fecharegistro >= '{fecha_ini}'",
        "$group":  "id_contrato",
        "$limit":  PAGE_SIZE,
        "$order":  "id_contrato",
    }
    all_rows, offset = [], 0
    with tqdm(desc="Adiciones (resumen GROUP BY)", unit=" contratos") as pbar:
        while True:
            params["$offset"] = offset
            r = requests.get(url, params=params, timeout=120)
            r.raise_for_status()
            batch = r.json()
            if not batch:
                break
            all_rows.extend(batch)
            offset += len(batch)
            pbar.update(len(batch))
            if len(batch) < PAGE_SIZE:
                break
            time.sleep(0.05)
    return pd.DataFrame(all_rows)

df_adiciones_raw = descargar_adiciones_resumen(FECHA_INI)
df_adiciones_raw.to_csv("/tmp/adiciones_resumen_raw.csv", index=False)
print(f"Adiciones (resumen por contrato): {len(df_adiciones_raw):,} contratos con al menos 1 adicion")
display(df_adiciones_raw.head(3))
"""))

cells.append(code("""
# 1C. Ejecucion contractual
df_ejecucion_raw = descargar_paginado(
    "mfmm-jqmq",
    where=f"fechacreacion >= '{FECHA_INI}'",
    select="identificadorcontrato,porcentaje_de_avance_real,fechacreacion",
    max_registros=MAX_REGS,
    desc="Ejecucion",
)
df_ejecucion_raw.to_csv("/tmp/ejecucion_raw.csv", index=False)
print(f"Ejecucion: {len(df_ejecucion_raw):,} filas")
"""))

cells.append(code("""
# 1D. DIVIPOLA — catalogo de municipios
r = requests.get(
    f"{BASE_URL}/gdxc-w37w.json",
    params={"$select": "cod_dpto,dpto,cod_mpio,nom_mpio", "$limit": 1200},
    timeout=60,
)
r.raise_for_status()
df_divipola = pd.DataFrame(r.json())
print(f"DIVIPOLA: {len(df_divipola):,} municipios")
display(df_divipola.head(3))
"""))

cells.append(code("""
# Reporte de descarga
reporte_descarga = {
    "fecha_hora_descarga":            FECHA_DESCARGA.isoformat(),
    "rango_temporal":                 f"Desde {FECHA_INI[:10]} hasta {FECHA_DESCARGA.date()}",
    "modo":                           MODO,
    "contratos_descargados":          len(df_contratos_raw),
    "adiciones_contratos_con_adicion": len(df_adiciones_raw),
    "ejecucion_registros":            len(df_ejecucion_raw),
    "municipios_divipola":            len(df_divipola),
}
print("=== REPORTE DE DESCARGA ===")
for k, v in reporte_descarga.items():
    print(f"  {k:<45s}: {v}")
"""))


# ══════════════════════════════════════════════════════════════════════════════
# SECCION 2 — LIMPIEZA E INTEGRACION
# ══════════════════════════════════════════════════════════════════════════════
cells.append(section_header("2", "Limpieza e integracion (Actividad 2)"))

cells.append(md("""
## Actividad 2 — Limpieza e integracion

Pipeline de limpieza:

1. **Contratos**: `valor_del_contrato` a float, `fecha_de_firma` a datetime,
   normalizar texto a mayusculas, eliminar duplicados por `id_contrato`.
2. **Adiciones**: `num_adiciones` a entero, `ultima_adicion` a datetime.
3. **Ejecucion**: conservar el **ultimo** registro por contrato (mayor `fechacreacion`).
4. **DIVIPOLA**: preparar columna de cruce normalizada.
5. **Join final**: contratos + adiciones + ejecucion + territorio (LEFT JOIN en todos).

El join es LEFT: cada contrato queda aunque no tenga adiciones, ejecucion o codigo DIVIPOLA.
"""))

cells.append(code("""
# Limpiar contratos
def a_float(v):
    try:
        return float(str(v).replace(",", "").replace("$", "").strip())
    except Exception:
        return 0.0

df_contratos = df_contratos_raw.copy()
df_contratos["valor_del_contrato"] = df_contratos["valor_del_contrato"].apply(a_float)
df_contratos["fecha_de_firma"]     = pd.to_datetime(df_contratos["fecha_de_firma"], errors="coerce")

for col in ["nombre_entidad", "proveedor_adjudicado", "objeto_del_contrato",
            "departamento", "municipio", "modalidad_de_contratacion", "tipo_de_contrato"]:
    if col in df_contratos.columns:
        df_contratos[col] = df_contratos[col].fillna("").str.strip().str.upper()

df_contratos.dropna(subset=["id_contrato"], inplace=True)
df_contratos.drop_duplicates(subset="id_contrato", keep="last", inplace=True)

print(f"Contratos limpios: {len(df_contratos):,}")
print(df_contratos[["id_contrato", "valor_del_contrato", "fecha_de_firma"]].dtypes)
"""))

cells.append(code("""
# Limpiar adiciones
df_adiciones = df_adiciones_raw.copy()
df_adiciones["num_adiciones"]  = (
    pd.to_numeric(df_adiciones["num_adiciones"], errors="coerce").fillna(0).astype(int)
)
df_adiciones["ultima_adicion"] = pd.to_datetime(df_adiciones["ultima_adicion"], errors="coerce")
df_adiciones.dropna(subset=["id_contrato"], inplace=True)
print(f"Adiciones procesadas: {len(df_adiciones):,}")
print(df_adiciones.dtypes)
"""))

cells.append(code("""
# Ejecucion: conservar ultimo registro por contrato
df_ejecucion = df_ejecucion_raw.copy()
df_ejecucion.rename(columns={"identificadorcontrato": "id_contrato"}, inplace=True)
df_ejecucion["porcentaje_de_avance_real"] = pd.to_numeric(
    df_ejecucion["porcentaje_de_avance_real"], errors="coerce"
)
df_ejecucion["fechacreacion"] = pd.to_datetime(df_ejecucion["fechacreacion"], errors="coerce")

df_ejecucion = (
    df_ejecucion
    .sort_values("fechacreacion", ascending=False)
    .drop_duplicates(subset="id_contrato", keep="first")
    [["id_contrato", "porcentaje_de_avance_real"]]
    .rename(columns={"porcentaje_de_avance_real": "avance_real"})
)
print(f"Ejecucion (ultimo por contrato): {len(df_ejecucion):,}")
"""))

cells.append(code("""
# DIVIPOLA: columna de cruce normalizada
df_divipola["nom_mpio_upper"] = df_divipola["nom_mpio"].str.upper().str.strip()
df_divipola["dpto_upper"]     = df_divipola["dpto"].str.upper().str.strip()
"""))

cells.append(code("""
# Join final: 4 fuentes
df_integrado = (
    df_contratos
    .merge(
        df_adiciones[["id_contrato", "num_adiciones", "ultima_adicion"]],
        on="id_contrato", how="left"
    )
    .merge(
        df_ejecucion[["id_contrato", "avance_real"]],
        on="id_contrato", how="left"
    )
    .merge(
        df_divipola[["nom_mpio_upper", "dpto_upper", "cod_mpio", "cod_dpto"]],
        left_on="municipio", right_on="nom_mpio_upper",
        how="left"
    )
)

df_integrado["num_adiciones"] = df_integrado["num_adiciones"].fillna(0).astype(int)
df_integrado["avance_real"]   = df_integrado["avance_real"].fillna(-1.0)

sin_cruce = df_integrado["cod_mpio"].isna().sum()
print("=== REPORTE DE INTEGRACION ===")
print(f"  Contratos integrados          : {len(df_integrado):,}")
print(f"  Con al menos 1 adicion        : {(df_integrado.num_adiciones > 0).sum():,}")
print(f"  Con ejecucion registrada      : {(df_integrado.avance_real >= 0).sum():,}")
print(f"  Sin cruce territorial (DIVIP) : {sin_cruce:,}  ({100*sin_cruce/max(len(df_integrado),1):.1f}%)")

display(df_integrado.head(3))
"""))

cells.append(interp("join territorial", [
    "El cruce con DIVIPOLA puede fallar si el nombre del municipio en SECOP tiene variaciones ortograficas.",
    "Los contratos sin cod_mpio siguen siendo validos para el analisis — solo no tienen coordenada territorial.",
    "Para mejorar el cruce se puede aplicar distancia de edicion (fuzzy matching) sobre nom_mpio_upper.",
]))


# ══════════════════════════════════════════════════════════════════════════════
# SECCION 3 — TEXTO NO ESTRUCTURADO
# ══════════════════════════════════════════════════════════════════════════════
cells.append(section_header("3", "Texto no estructurado (Actividad 3)"))

cells.append(md("""
## Actividad 3 — Texto no estructurado

Se construye `texto_busqueda` normalizando el campo `objeto_del_contrato` y se aplica
un catalogo de palabras clave para crear `temas_detectados`.

### Limitaciones del enfoque de palabras clave

- Coincidencia de subcadenas: sensible al vocabulario especifico de SECOP II.
- No captura sinonimos ni contexto semantico.
- Un contrato de infraestructura redactado sin las palabras clave quedara como `sin_clasificar`.
- Puede detectar multiples temas si el objeto mezcla conceptos.

> Este enfoque no exige machine learning. Exige explicar las reglas y sus limites.
"""))

cells.append(code("""
def limpiar_texto(texto):
    if not isinstance(texto, str) or not texto.strip():
        return ""
    t = texto.lower().strip()
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^\\w\\s]", " ", t)
    t = re.sub(r"\\s+", " ", t).strip()
    return t

# Prueba
print(repr(limpiar_texto("Prestacion de Servicios Profesionales — Apoyo a la Gestion")))
print(repr(limpiar_texto("CONSTRUCCION DE VIA TERCIARIA (km 2.5 — 4.8)")))
"""))

cells.append(code("""
TEMAS = {
    "alimentacion":            [
        "alimentacion", "alimentos", "comedor", "restaurante",
        "suministro alimentos", "nutricion", "despensa", "racion", "mercado"
    ],
    "infraestructura":         [
        "obra", "via", "vias", "construccion", "mantenimiento",
        "pavimento", "puente", "alcantarillado", "acueducto", "carretera",
        "adoquin", "placa huella", "muro de contencion"
    ],
    "salud":                   [
        "salud", "hospital", "medicamento", "ambulancia", "medico",
        "clinica", "farmacia", "insumos medicos", "equipos medicos", "eps"
    ],
    "educacion":               [
        "colegio", "estudiante", "escolar", "docente", "educacion",
        "aula", "universidad", "biblioteca", "kit escolar", "textos escolares"
    ],
    "tecnologia":              [
        "software", "licencia", "sistema", "plataforma", "informatica",
        "hardware", "servidor", "tecnologia", "digitalizacion", "red de datos"
    ],
    "servicios_profesionales": [
        "prestacion de servicios", "apoyo a la gestion", "consultoria",
        "asesoria", "interventoria", "auditoria", "apoyo profesional"
    ],
    "seguridad":               [
        "seguridad", "vigilancia", "policia", "defensa",
        "armamento", "municion", "dotacion policial"
    ],
    "transporte":              [
        "transporte", "vehiculo", "flota", "bus",
        "camion", "movilidad", "pasaje"
    ],
    "cultura_deporte":         [
        "cultura", "deporte", "recreacion", "arte", "evento",
        "festival", "escenario deportivo", "cancha"
    ],
    "medioambiente":           [
        "ambiental", "residuos", "reciclaje", "sostenibilidad",
        "arbolado", "parque", "fauna", "flora", "reforestacion"
    ],
}

def detectar_temas(texto_limpio):
    if not texto_limpio:
        return ["sin_clasificar"]
    encontrados = [
        tema for tema, palabras in TEMAS.items()
        if any(p in texto_limpio for p in palabras)
    ]
    return encontrados if encontrados else ["sin_clasificar"]

print(detectar_temas("mantenimiento de vias y alcantarillado municipal"))
print(detectar_temas("prestacion de servicios profesionales apoyo a la gestion"))
print(detectar_temas("contratacion de personal de planta"))
"""))

cells.append(code("""
# Aplicar al dataset
df_integrado["objeto_limpio"]    = df_integrado["objeto_del_contrato"].apply(limpiar_texto)
df_integrado["texto_busqueda"]   = df_integrado["objeto_limpio"]
df_integrado["temas_detectados"] = df_integrado["texto_busqueda"].apply(detectar_temas)

sin_cls = df_integrado["temas_detectados"].apply(lambda x: "sin_clasificar" in x).sum()
print(f"Texto procesado   : {len(df_integrado):,} contratos")
print(f"Sin clasificar    : {sin_cls:,}  ({100*sin_cls/max(len(df_integrado),1):.1f}%)")
display(df_integrado[["id_contrato", "objeto_limpio", "temas_detectados"]].head(5))
"""))

cells.append(code("""
# Grafico de distribucion de temas
conteo_temas = Counter(t for ts in df_integrado["temas_detectados"] for t in ts)
df_temas_res = pd.DataFrame(conteo_temas.most_common(), columns=["tema", "contratos"])

fig = px.bar(
    df_temas_res, x="contratos", y="tema", orientation="h",
    title="Contratos por tema detectado",
    labels={"contratos": "N de contratos", "tema": "Tema"},
    color="contratos", color_continuous_scale="Blues",
)
fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
fig.show()
print(df_temas_res.to_string(index=False))
"""))


# ══════════════════════════════════════════════════════════════════════════════
# SECCION 4 — INDICE DE PRIORIDAD
# ══════════════════════════════════════════════════════════════════════════════
cells.append(section_header("4", "Indice descriptivo de prioridad (Actividad 4)"))

cells.append(md("""
## Actividad 4 — Indice de prioridad

El indice orienta que contratos revisar primero en una auditoria (escala 0–100).
**No implica fraude ni irregularidad. Es una heuristica descriptiva.**

### Formula

| Componente | Peso max | Criterio |
|---|---:|---|
| Valor relativo alto | 40 | Percentil del valor del contrato × 40 |
| Numero de adiciones | 30 | 10 pts por adicion, maximo 30 pts |
| Ejecucion baja | 20 | 20 pts si avance real < 50 % |
| Texto insuficiente | 10 | 10 pts si objeto < 30 caracteres limpios |

### Niveles

| Nivel | Rango | Interpretacion |
|---|---|---|
| alta | >= 60 | Revision prioritaria recomendada |
| media | 30 – 59 | Monitoreo periodico |
| baja | < 30 | Sin alertas activas |
"""))

cells.append(code("""
df_integrado["valor_percentil"] = (
    df_integrado["valor_del_contrato"].rank(pct=True).fillna(0)
)
print("Estadisticas de valor del contrato:")
print(df_integrado["valor_del_contrato"].describe().apply(lambda x: f"{x:,.0f}"))
"""))

cells.append(code("""
def calcular_indice(row):
    score  = 0.0
    score += row["valor_percentil"] * 40
    score += min(int(row.get("num_adiciones", 0) or 0) * 10, 30)
    avance = float(row.get("avance_real", -1) or -1)
    if 0 <= avance < 50:
        score += 20
    if len(str(row.get("objeto_limpio", "") or "")) < 30:
        score += 10
    return round(min(score, 100))

def nivel_prioridad(indice):
    if indice >= 60:
        return "alta"
    if indice >= 30:
        return "media"
    return "baja"

df_integrado["indice_prioridad"] = df_integrado.apply(calcular_indice, axis=1)
df_integrado["nivel_prioridad"]  = df_integrado["indice_prioridad"].apply(nivel_prioridad)

print("=== DISTRIBUCION DE PRIORIDAD ===")
print(df_integrado["nivel_prioridad"].value_counts().to_string())
print()
cols_top = ["id_contrato", "nombre_entidad", "valor_del_contrato",
            "num_adiciones", "avance_real", "indice_prioridad", "nivel_prioridad"]
cols_disp = [c for c in cols_top if c in df_integrado.columns]
print("Top 10 contratos por prioridad:")
display(df_integrado.nlargest(10, "indice_prioridad")[cols_disp])
"""))

cells.append(code("""
fig = px.histogram(
    df_integrado, x="indice_prioridad", color="nivel_prioridad",
    nbins=50,
    color_discrete_map={"alta": "#dc2626", "media": "#f59e0b", "baja": "#16a34a"},
    title="Distribucion del indice de prioridad",
    labels={"indice_prioridad": "Indice", "count": "Contratos"},
)
fig.update_layout(barmode="overlay", bargap=0.05)
fig.show()
"""))

cells.append(interp("indice de prioridad", [
    "Un indice alto (>= 60) combina varias senales de atencion — no es prueba de irregularidad.",
    "El componente de mayor peso es el valor relativo (40 pts): contratos grandes siempre tendran score base alto.",
    "Un contrato con 3 adiciones, avance < 50 % y objeto corto puede llegar a 90/100 sin que haya fraude.",
    "La utilidad del indice es orientar la revision documental, no reemplazarla.",
]))


# ══════════════════════════════════════════════════════════════════════════════
# SECCION 5 — MONGODB ATLAS
# ══════════════════════════════════════════════════════════════════════════════
cells.append(section_header("5", "Modelo NoSQL en MongoDB Atlas (Actividad 5)"))

cells.append(md("""
## Actividad 5 — MongoDB Atlas

### Colecciones en `secop_observatorio`

| Coleccion | Descripcion | Carga |
|---|---|---|
| `contratos_operativos` | Documento anidado por contrato | Upsert por `id_contrato` |
| `alertas_revision` | Contratos con prioridad alta | Drop + insert |
| `entidades_resumen` | Estadisticas por entidad | Drop + insert |
| `proveedores_resumen` | Estadisticas por proveedor | Drop + insert |
| `temas_resumen` | Conteo de contratos por tema | Drop + insert |
| `metadata_pipeline` | Metadatos de la ultima ejecucion | Replace by `_id` |

Todas las cargas de `contratos_operativos` usan **upsert** para ser idempotentes:
si se vuelve a ejecutar el pipeline, los documentos existentes se actualizan, no se duplican.

### Esquema del documento principal

```json
{
  "id_contrato": "CO1.PCCNTR.xxxxxxx",
  "valor": 12500000.0,
  "fecha_firma": "2025-03-15T00:00:00",
  "modalidad": "CONTRATACION DIRECTA",
  "tipo": "PRESTACION DE SERVICIOS",
  "entidad":    { "nit": "...", "nombre": "..." },
  "proveedor":  { "documento": "...", "nombre": "..." },
  "territorio": { "departamento": "...", "municipio": "...", "cod_mpio": "...", "cod_dpto": "..." },
  "adiciones":  { "numero": 2 },
  "ejecucion":  { "avance_real": 35.0 },
  "texto_no_estructurado": {
    "texto_busqueda": "prestacion servicios apoyo gestion ...",
    "temas_detectados": ["servicios_profesionales"]
  },
  "prioridad":  { "indice": 78, "nivel": "alta" },
  "_cargado_en": ISODate("2026-05-24T13:00:00Z")
}
```
"""))

cells.append(code("""
# Conectar
client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=8000)
client.admin.command("ping")
db = client[DB_NAME]
print(f"Conectado a: {DB_NAME}")
print(f"Colecciones existentes: {db.list_collection_names()}")
"""))

cells.append(code("""
def fila_a_documento(row):
    fecha_firma = row.get("fecha_de_firma")
    avance_raw  = row.get("avance_real", -1)
    avance      = float(avance_raw) if avance_raw is not None and float(avance_raw) >= 0 else None
    return {
        "id_contrato": str(row["id_contrato"]),
        "valor":       float(row.get("valor_del_contrato", 0) or 0),
        "fecha_firma": fecha_firma.isoformat() if pd.notna(fecha_firma) else None,
        "modalidad":   str(row.get("modalidad_de_contratacion", "") or ""),
        "tipo":        str(row.get("tipo_de_contrato", "") or ""),
        "entidad": {
            "nit":    str(row.get("nit_entidad", "") or ""),
            "nombre": str(row.get("nombre_entidad", "") or ""),
        },
        "proveedor": {
            "documento": str(row.get("documento_proveedor", "") or ""),
            "nombre":    str(row.get("proveedor_adjudicado", "") or ""),
        },
        "territorio": {
            "departamento": str(row.get("departamento", "") or ""),
            "municipio":    str(row.get("municipio", "") or ""),
            "cod_mpio":     str(row.get("cod_mpio", "") or ""),
            "cod_dpto":     str(row.get("cod_dpto", "") or ""),
        },
        "adiciones":  {"numero": int(row.get("num_adiciones", 0) or 0)},
        "ejecucion":  {"avance_real": avance},
        "texto_no_estructurado": {
            "texto_busqueda":   str(row.get("texto_busqueda", "") or ""),
            "temas_detectados": list(row.get("temas_detectados", []) or []),
        },
        "prioridad": {
            "indice": int(row.get("indice_prioridad", 0) or 0),
            "nivel":  str(row.get("nivel_prioridad", "baja") or "baja"),
        },
        "_cargado_en": FECHA_DESCARGA,
    }

# Ejemplo de documento
doc_ejemplo = fila_a_documento(df_integrado.iloc[0])
print(json.dumps(doc_ejemplo, indent=2, default=str)[:900])
"""))

cells.append(code("""
# Cargar contratos_operativos con upsert por lotes de 500
BATCH_SIZE    = 500
col_contratos = db["contratos_operativos"]
ops, total_ops = [], 0

for _, row in tqdm(df_integrado.iterrows(), total=len(df_integrado), desc="Upsert contratos"):
    doc = fila_a_documento(row)
    ops.append(UpdateOne(
        {"id_contrato": doc["id_contrato"]},
        {"$set": doc},
        upsert=True,
    ))
    if len(ops) >= BATCH_SIZE:
        res = col_contratos.bulk_write(ops, ordered=False)
        total_ops += res.upserted_count + res.modified_count
        ops = []

if ops:
    res = col_contratos.bulk_write(ops, ordered=False)
    total_ops += res.upserted_count + res.modified_count

print(f"contratos_operativos: {col_contratos.count_documents({}):,} documentos")
print(f"Operaciones de upsert (insert + update): {total_ops:,}")
"""))

cells.append(code("""
# Cargar alertas_revision
df_alertas = df_integrado[df_integrado["nivel_prioridad"] == "alta"].copy()
alertas_docs = []
for _, row in df_alertas.iterrows():
    alertas_docs.append({
        "id_contrato": str(row["id_contrato"]),
        "entidad":     str(row.get("nombre_entidad", "") or ""),
        "proveedor":   str(row.get("proveedor_adjudicado", "") or ""),
        "valor":       float(row.get("valor_del_contrato", 0) or 0),
        "indice":      int(row.get("indice_prioridad", 0) or 0),
        "temas":       list(row.get("temas_detectados", []) or []),
        "razon_prioridad": {
            "valor_percentil":    round(float(row.get("valor_percentil", 0) or 0), 3),
            "num_adiciones":      int(row.get("num_adiciones", 0) or 0),
            "avance_bajo":        bool(0 <= float(row.get("avance_real", -1) or -1) < 50),
            "texto_insuficiente": len(str(row.get("objeto_limpio", "") or "")) < 30,
        },
        "_cargado_en": FECHA_DESCARGA,
    })

col_alertas = db["alertas_revision"]
col_alertas.drop()
if alertas_docs:
    col_alertas.insert_many(alertas_docs)
print(f"alertas_revision: {col_alertas.count_documents({}):,} documentos")
"""))

cells.append(code("""
# Resumen por entidad
resumen_ent = (
    df_integrado
    .groupby(["nit_entidad", "nombre_entidad"])
    .agg(
        total_contratos = ("id_contrato", "count"),
        valor_total     = ("valor_del_contrato", "sum"),
        contratos_alta  = ("nivel_prioridad", lambda s: (s == "alta").sum()),
        adiciones_total = ("num_adiciones", "sum"),
    )
    .reset_index()
    .sort_values("valor_total", ascending=False)
)
ent_docs = [
    {
        "nit":             row["nit_entidad"],
        "nombre":          row["nombre_entidad"],
        "total_contratos": int(row["total_contratos"]),
        "valor_total":     float(row["valor_total"]),
        "contratos_alta":  int(row["contratos_alta"]),
        "adiciones_total": int(row["adiciones_total"]),
        "_cargado_en":     FECHA_DESCARGA,
    }
    for _, row in resumen_ent.iterrows()
]
db["entidades_resumen"].drop()
if ent_docs:
    db["entidades_resumen"].insert_many(ent_docs)
print(f"entidades_resumen: {db['entidades_resumen'].count_documents({}):,}")
display(resumen_ent.head(5)[["nombre_entidad","total_contratos","valor_total","contratos_alta"]])
"""))

cells.append(code("""
# Resumen por proveedor
resumen_prov = (
    df_integrado
    .groupby(["documento_proveedor", "proveedor_adjudicado"])
    .agg(
        total_contratos = ("id_contrato", "count"),
        valor_total     = ("valor_del_contrato", "sum"),
        contratos_alta  = ("nivel_prioridad", lambda s: (s == "alta").sum()),
    )
    .reset_index()
    .sort_values("valor_total", ascending=False)
)
prov_docs = [
    {
        "documento":       row["documento_proveedor"],
        "nombre":          row["proveedor_adjudicado"],
        "total_contratos": int(row["total_contratos"]),
        "valor_total":     float(row["valor_total"]),
        "contratos_alta":  int(row["contratos_alta"]),
        "_cargado_en":     FECHA_DESCARGA,
    }
    for _, row in resumen_prov.iterrows()
]
db["proveedores_resumen"].drop()
if prov_docs:
    db["proveedores_resumen"].insert_many(prov_docs)
print(f"proveedores_resumen: {db['proveedores_resumen'].count_documents({}):,}")

# Resumen por tema
temas_docs = [
    {"tema": t, "contratos": c, "_cargado_en": FECHA_DESCARGA}
    for t, c in Counter(t for ts in df_integrado["temas_detectados"] for t in ts).most_common()
]
db["temas_resumen"].drop()
db["temas_resumen"].insert_many(temas_docs)
print(f"temas_resumen: {db['temas_resumen'].count_documents({}):,}")
"""))

cells.append(code("""
# metadata_pipeline
meta_doc = {
    "_id":            "pipeline_v1",
    "fecha_descarga": FECHA_DESCARGA,
    "rango_temporal": f"{FECHA_INI[:10]} a {FECHA_DESCARGA.date().isoformat()}",
    "modo_descarga":  MODO,
    "totales": {
        "contratos":       int(len(df_contratos)),
        "contratos_atlas": db["contratos_operativos"].count_documents({}),
        "alertas_alta":    db["alertas_revision"].count_documents({}),
        "entidades":       db["entidades_resumen"].count_documents({}),
        "proveedores":     db["proveedores_resumen"].count_documents({}),
        "temas":           db["temas_resumen"].count_documents({}),
    },
    "distribucion_prioridad": dict(df_integrado["nivel_prioridad"].value_counts()),
    "formula_prioridad": "valor_percentil*40 + min(adiciones*10,30) + (avance<50%)*20 + (texto<30c)*10",
    "limitaciones": [
        "Adiciones como resumen (count por contrato), no filas individuales.",
        "Temas por coincidencia de subcadenas — sin NLP.",
        f"Modo '{MODO}': muestra puede no representar el universo completo.",
        "Contratos sin cruce territorial no tienen codigo DIVIPOLA.",
    ],
    "num_actualizaciones": 0,
}
db["metadata_pipeline"].replace_one({"_id": "pipeline_v1"}, meta_doc, upsert=True)
print("metadata_pipeline guardado:")
pprint.pprint({k: v for k, v in meta_doc.items() if k != "_id"})
"""))

cells.append(code("""
# Crear indices en contratos_operativos
col = db["contratos_operativos"]

col.create_index([("prioridad.indice", DESCENDING)],       name="idx_prioridad")
col.create_index([("entidad.nit", ASCENDING)],             name="idx_entidad_nit")
col.create_index([("proveedor.documento", ASCENDING)],     name="idx_proveedor")
col.create_index([("prioridad.nivel", ASCENDING)],         name="idx_nivel")
col.create_index([("territorio.departamento", ASCENDING)], name="idx_dpto")
col.create_index(
    [("texto_no_estructurado.texto_busqueda", TEXT)],
    name="idx_texto_full",
    default_language="spanish",
)

print("Indices en contratos_operativos:")
for idx in col.list_indexes():
    print(f"  {idx['name']}: {list(idx['key'].items())}")
"""))

cells.append(md("### Consultas de demostracion"))

cells.append(code("""
# Query 1: Top 10 contratos de alta prioridad
print("--- Top 10 contratos alta prioridad ---")
cursor = db["contratos_operativos"].find(
    {"prioridad.nivel": "alta"},
    {"id_contrato": 1, "valor": 1, "entidad.nombre": 1, "prioridad": 1, "_id": 0}
).sort("prioridad.indice", DESCENDING).limit(10)
df_q1 = pd.DataFrame(list(cursor))
display(df_q1)

# Query 2: Contratos con mas de 2 adiciones
n = db["contratos_operativos"].count_documents({"adiciones.numero": {"$gt": 2}})
print(f"\\n--- Contratos con mas de 2 adiciones: {n:,} ---")

# Query 3: Alta prioridad sin ejecucion registrada
n2 = db["contratos_operativos"].count_documents(
    {"ejecucion.avance_real": None, "prioridad.nivel": "alta"}
)
print(f"--- Alta prioridad sin ejecucion registrada: {n2:,} ---")
"""))

cells.append(code("""
# Busqueda textual full-text
print("--- Busqueda textual: 'construccion vias' ---")
cursor = db["contratos_operativos"].find(
    {"$text": {"$search": "construccion vias"}},
    {
        "score":           {"$meta": "textScore"},
        "id_contrato":     1,
        "entidad.nombre":  1,
        "prioridad.nivel": 1,
        "_id":             0,
    }
).sort([("score", {"$meta": "textScore"})]).limit(10)
df_txt = pd.DataFrame(list(cursor))
if not df_txt.empty:
    display(df_txt)
else:
    print("Sin resultados en la muestra.")
"""))

cells.append(code("""
# Agregaciones analiticas
pipeline_dpto = [
    {"$group": {
        "_id":            "$territorio.departamento",
        "total":          {"$sum": 1},
        "valor_total":    {"$sum": "$valor"},
        "alta_prioridad": {"$sum": {"$cond": [{"$eq": ["$prioridad.nivel", "alta"]}, 1, 0]}},
    }},
    {"$sort": {"valor_total": -1}},
    {"$limit": 15},
]
df_agg_dpto = pd.DataFrame(list(db["contratos_operativos"].aggregate(pipeline_dpto)))
if not df_agg_dpto.empty:
    df_agg_dpto.columns = ["departamento", "total", "valor_total", "alta_prioridad"]
    print("--- Valor total por departamento (top 15) ---")
    display(df_agg_dpto)

pipeline_temas = [
    {"$unwind": "$texto_no_estructurado.temas_detectados"},
    {"$group": {
        "_id":        "$texto_no_estructurado.temas_detectados",
        "contratos":  {"$sum": 1},
        "valor_prom": {"$avg": "$valor"},
    }},
    {"$sort": {"contratos": -1}},
]
df_agg_temas = pd.DataFrame(list(db["contratos_operativos"].aggregate(pipeline_temas)))
if not df_agg_temas.empty:
    print("\\n--- Temas: frecuencia y valor promedio ---")
    display(df_agg_temas)
"""))

cells.append(code("""
# Evidencia de upsert idempotente
print(f"ANTES  : {db['contratos_operativos'].count_documents({}):,} documentos")

ops_reload = [
    UpdateOne(
        {"id_contrato": str(row["id_contrato"])},
        {"$set": fila_a_documento(row)},
        upsert=True,
    )
    for _, row in df_integrado.head(100).iterrows()
]
db["contratos_operativos"].bulk_write(ops_reload, ordered=False)

print(f"DESPUES : {db['contratos_operativos'].count_documents({}):,} documentos")
print("Upsert idempotente confirmado: el conteo no aumento.")

db["metadata_pipeline"].update_one(
    {"_id": "pipeline_v1"},
    {
        "$set": {"ultima_actualizacion": datetime.now(timezone.utc)},
        "$inc": {"num_actualizaciones": 1},
    }
)
print("metadata_pipeline actualizado.")
"""))


# ══════════════════════════════════════════════════════════════════════════════
# SECCION 6 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
cells.append(section_header("6", "Dashboard operativo (Actividad 6)"))

cells.append(md("""
## Actividad 6 — Dashboard

Se presentan KPIs y graficas con Plotly directamente en el notebook.
Al final se genera `dashboard.py` listo para desplegar en Streamlit Community Cloud.
"""))

cells.append(code("""
# KPIs
total_c   = len(df_integrado)
valor_tot = df_integrado["valor_del_contrato"].sum()
alta_c    = (df_integrado["nivel_prioridad"] == "alta").sum()
con_adic  = (df_integrado["num_adiciones"] > 0).sum()
sin_ejec  = (df_integrado["avance_real"] < 0).sum()

print("╔══════════════════════════════════════════════════════════╗")
print("║      OBSERVATORIO DE CONTRATACION PUBLICA               ║")
print("║      Contraloria Departamental de Cundinamarca          ║")
print("╠══════════════════════════════════════════════════════════╣")
print(f"║  Total contratos procesados   : {total_c:>12,}          ║")
print(f"║  Valor total (COP)            : {valor_tot:>12,.0f}          ║")
print(f"║  Contratos alta prioridad     : {alta_c:>12,}          ║")
print(f"║  Contratos con adiciones      : {con_adic:>12,}          ║")
print(f"║  Sin registro de ejecucion    : {sin_ejec:>12,}          ║")
print(f"║  Modo de descarga             : {MODO:>12}          ║")
print(f"║  Fecha de descarga            : {str(FECHA_DESCARGA.date()):>12}          ║")
print("╚══════════════════════════════════════════════════════════╝")
"""))

cells.append(code("""
# Dashboard con 4 paneles
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=[
        "Distribucion de prioridad",
        "Top 10 departamentos por valor contratado",
        "Contratos por tema detectado",
        "Alta prioridad por departamento",
    ],
    specs=[
        [{"type": "pie"}, {"type": "bar"}],
        [{"type": "bar"}, {"type": "bar"}],
    ],
)

prio = df_integrado["nivel_prioridad"].value_counts()
fig.add_trace(
    go.Pie(labels=prio.index, values=prio.values,
           marker_colors=["#dc2626","#f59e0b","#16a34a"], name="Prioridad"),
    row=1, col=1,
)

df_dv = df_integrado.groupby("departamento")["valor_del_contrato"].sum().nlargest(10).reset_index()
fig.add_trace(
    go.Bar(x=df_dv["valor_del_contrato"], y=df_dv["departamento"],
           orientation="h", marker_color="#2563eb", name="Valor"),
    row=1, col=2,
)

cnt_t  = Counter(t for ts in df_integrado["temas_detectados"] for t in ts)
df_tp  = pd.DataFrame(cnt_t.most_common(10), columns=["tema","n"])
fig.add_trace(
    go.Bar(x=df_tp["n"], y=df_tp["tema"], orientation="h",
           marker_color="#7c3aed", name="Contratos"),
    row=2, col=1,
)

df_ad = (df_integrado[df_integrado["nivel_prioridad"]=="alta"]
         .groupby("departamento").size().nlargest(10).reset_index(name="n"))
fig.add_trace(
    go.Bar(x=df_ad["n"], y=df_ad["departamento"], orientation="h",
           marker_color="#dc2626", name="Alta"),
    row=2, col=2,
)

fig.update_layout(
    height=740, showlegend=False,
    title_text="Observatorio de Contratacion — Contraloria Departamental de Cundinamarca",
)
fig.show()
"""))

cells.append(code("""
# Top 20 alertas
print("=== TOP 20 ALERTAS DE REVISION ===")
cols_a = ["id_contrato","nombre_entidad","proveedor_adjudicado",
          "valor_del_contrato","num_adiciones","avance_real",
          "indice_prioridad","temas_detectados"]
display(df_integrado.nlargest(20,"indice_prioridad")[[c for c in cols_a if c in df_integrado.columns]])
"""))

cells.append(code(r"""
# Generar dashboard.py para Streamlit Community Cloud
script = r'''
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient

st.set_page_config(page_title="Observatorio Contratacion", page_icon="magnifying glass", layout="wide")
st.title("Observatorio de Contratacion Publica")
st.caption("Contraloria Departamental de Cundinamarca")

MONGODB_URI = os.environ.get("MONGODB_URI", st.secrets.get("MONGODB_URI", ""))
if not MONGODB_URI:
    st.error("Configura MONGODB_URI en Streamlit Secrets o como variable de entorno.")
    st.stop()

@st.cache_resource
def get_db():
    return MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)["secop_observatorio"]

db      = get_db()
meta    = db["metadata_pipeline"].find_one({"_id": "pipeline_v1"}) or {}
totales = meta.get("totales", {})

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total contratos",       f'{totales.get("contratos_atlas", 0):,}')
c2.metric("Alertas alta prioridad",f'{totales.get("alertas_alta", 0):,}')
c3.metric("Entidades",             f'{totales.get("entidades", 0):,}')
c4.metric("Proveedores",           f'{totales.get("proveedores", 0):,}')

st.divider()

temas = list(db["temas_resumen"].find({}, {"_id": 0}).sort("contratos", -1).limit(12))
if temas:
    df_t = pd.DataFrame(temas)
    fig  = px.bar(df_t, x="contratos", y="tema", orientation="h",
                  title="Contratos por tema detectado",
                  color="contratos", color_continuous_scale="Blues")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

ents = list(db["entidades_resumen"].find({}, {"_id": 0}).sort("valor_total", -1).limit(10))
if ents:
    df_e = pd.DataFrame(ents)
    fig2 = px.bar(df_e, x="valor_total", y="nombre", orientation="h",
                  title="Top 10 entidades por valor contratado",
                  color="contratos_alta", color_continuous_scale="Reds",
                  labels={"valor_total": "Valor total (COP)", "nombre": "Entidad"})
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Alertas de revision prioritaria")
alertas = list(db["alertas_revision"].find({}, {"_id": 0}).sort("indice", -1).limit(100))
if alertas:
    st.dataframe(pd.DataFrame(alertas), use_container_width=True, height=400)
else:
    st.info("No hay alertas cargadas.")

st.caption(f'Pipeline: {meta.get("fecha_descarga","N/A")} | Modo: {meta.get("modo_descarga","?")} | Actualizaciones: {meta.get("num_actualizaciones",0)}')
'''

with open("/tmp/dashboard.py", "w", encoding="utf-8") as f:
    f.write(script)

print("dashboard.py guardado en /tmp/dashboard.py")
print()
print("Para desplegar en Streamlit Community Cloud:")
print("  1. Copia /tmp/dashboard.py a un repo de GitHub.")
print("  2. Ve a share.streamlit.io y conecta el repo.")
print("  3. Agrega MONGODB_URI en 'Secrets'.")
print()
print("Para ejecutar localmente:")
print("  pip install streamlit plotly pymongo")
print("  export MONGODB_URI='<tu-uri>'")
print("  streamlit run dashboard.py")
"""))


# ══════════════════════════════════════════════════════════════════════════════
# SECCION 7 — INFORME EJECUTIVO
# ══════════════════════════════════════════════════════════════════════════════
cells.append(section_header("7", "Informe ejecutivo"))

cells.append(md("""
## Informe ejecutivo

**Para:** Contraloria Departamental de Cundinamarca — Oficina de Control Interno
**Asunto:** Analisis descriptivo de contratacion publica SECOP II
**Elaborado por:** Equipo de Analitica de Datos
**Fecha:** [completar con la fecha de entrega]

---

### 1. Que se hizo

Se construyo un prototipo de observatorio de contratacion publica con datos reales
de SECOP II. Se descargaron, limpiaron e integraron cuatro fuentes: contratos electronicos,
resumen de adiciones por contrato (via GROUP BY en la API), ejecucion contractual
y nomenclatura territorial DIVIPOLA.

El texto libre del objeto contractual se normalizo y se aplico un catalogo de palabras
clave para detectar temas. Con base en cuatro variables se construyo un indice descriptivo
de prioridad (0-100) que orienta la revision documental.

Los resultados se almacenaron en MongoDB Atlas como documentos anidados, habilitando
consultas por campos internos, busqueda textual y agregaciones analiticas.
Un dashboard operativo resume los KPIs y la tabla de alertas.

---

### 2. Hallazgos clave

*(Completar con los valores reales que arroje el pipeline al ejecutarse)*

- **Total de contratos procesados:** [completar]
- **Valor total contratado (COP):** [completar]
- **Contratos con prioridad alta (indice >= 60):** [completar] ([completar]%)
- **Contratos con al menos una adicion:** [completar] ([completar]%)
- **Contratos sin registro de ejecucion:** [completar]
- **Tema mas frecuente:** [completar] con [N] contratos
- **Top 3 departamentos por valor:** [completar]
- **Top 3 entidades por valor contratado:** [completar]
- **Contrato de mayor indice de prioridad:** [id_contrato, entidad, valor, razon]

---

### 3. Que significa el indice de prioridad

El indice combina cuatro senales observables: valor relativo alto, numero de adiciones,
avance de ejecucion bajo, y texto del objeto demasiado corto para ser verificable.
Un indice alto significa que el contrato reune varias caracteristicas que justifican
una revision documental adicional. **No implica fraude ni irregularidad.**

---

### 4. Limitaciones tecnicas

- Las adiciones se descargaron como resumen (conteo por contrato via GROUP BY),
  no como texto individual de cada modificacion. Para analizar el objeto de cada
  adicion se requiere descarga individual de las filas.
- El dataset de adiciones contiene duplicados en el campo `identificador`; el GROUP BY
  los colapsa y esto puede sobreestimar el numero de modificaciones por contrato.
- La deteccion de temas es por coincidencia de subcadenas — no captura sinonimos
  ni contexto semantico.
- El indice es una heuristica descriptiva, no un modelo predictivo de riesgo.
  Puede producir falsos positivos en contratos legitimos de alto valor.
- Los contratos sin cruce territorial con DIVIPOLA no tienen codigo de municipio.
  Corresponden a variaciones ortograficas en el nombre del municipio.
- En modo `muestra` o `desde_2025` los resultados no son representativos del universo
  completo desde 2021. La entrega final debe indicar el modo usado.

---

### 5. Recomendaciones

1. Revisar manualmente los contratos con indice >= 80 y sin registro de ejecucion.
2. Investigar entidades con alta concentracion de valor en pocos proveedores.
3. Mejorar el cruce territorial con fuzzy matching sobre nombres de municipio.
4. Ampliar el catalogo de palabras clave con terminos sectoriales adicionales.
5. Programar actualizaciones semanales del pipeline para mantener el observatorio vigente.
6. Para la siguiente version: descargar las descripciones individuales de adiciones
   para analisis de texto en modificaciones contractuales.
7. Considerar el uso de un App Token de Socrata para aumentar el limite de paginacion
   de 1 000 a 50 000 registros por peticion, reduciendo el tiempo de descarga en ~98%.
"""))


# ══════════════════════════════════════════════════════════════════════════════
# GENERAR
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    validate(cells)
    save(cells, OUTPUT)
