# -*- coding: utf-8 -*-
"""
utils/patch_12_tabla_funciones.py
==================================
Inserta una tabla de referencia rapida de funciones en la Seccion 14
del cuaderno 12_MongoDB_Atlas_NoSQL_Moderno.ipynb, justo despues de
la celda de introduccion "Por que estos tres patrones" (id: f3f1e8ca).

Uso:
    python utils/patch_12_tabla_funciones.py
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTEBOOK_PATH = os.path.join(ROOT, "Cuadernos", "12_MongoDB_Atlas_NoSQL_Moderno.ipynb")

TABLA_SOURCE = [
    "## Funciones y metodos de esta seccion — referencia rapida\n",
    "\n",
    "La siguiente tabla agrupa todas las funciones y metodos que se usan en los tres patrones.\n",
    "Cada **Mini ficha** al final del patron correspondiente entra en el detalle de parametros,\n",
    "retorno e interpretacion de la salida.\n",
    "\n",
    "| Funcion / Metodo | Origen | Para que sirve en esta seccion |\n",
    "|---|---|---|\n",
    "| `UpdateOne(filtro, cambio, upsert=True)` | `pymongo` | Construye una instruccion de upsert-o-actualizacion para pasar a `bulk_write`; no ejecuta nada en el servidor hasta ese momento. |\n",
    "| `bulk_write(ops, ordered=False)` | `pymongo.Collection` | Envia una lista de instrucciones al servidor en el minimo numero de viajes de red; devuelve contadores de insertados, actualizados y modificados. |\n",
    "| `create_index([(campo, TEXT)], default_language=...)` | `pymongo.Collection` | Crea un indice invertido de texto con tokenizacion y filtrado de stopwords por idioma; obligatorio antes de usar `$text`. |\n",
    "| `find({\"$text\": {\"$search\": \"palabras\"}})` | `pymongo.Collection` | Busca en todos los campos del indice TEXT a la vez; OR implicito entre palabras; `+palabra` para AND, `-palabra` para excluir. |\n",
    "| `{\"$meta\": \"textScore\"}` | MQL (proyeccion) | Campo virtual con el puntaje de relevancia textual; no se almacena en el documento, solo existe dentro de la proyeccion o el pipeline. |\n",
    "| `drop_index(nombre)` | `pymongo.Collection` | Elimina un indice por nombre; necesario antes de recrear el indice TEXT con una definicion diferente (solo puede haber uno por coleccion). |\n",
    "| `df.iterrows()` | `pandas.DataFrame` | Itera el DataFrame fila a fila devolviendo `(indice, Series)`; util cuando la funcion de transformacion tiene logica condicional por campo. |\n",
    "| `df.to_dict(\"records\")` | `pandas.DataFrame` | Convierte todo el DataFrame a una lista de dicts en una sola operacion; mas rapido que `iterrows()` cuando no hay logica de transformacion por campo. |\n",
    "| `df.iloc[inicio:fin]` | `pandas.DataFrame` | Selecciona un rango de filas por posicion entera para dividir el DataFrame en lotes sin copiar datos innecesariamente. |\n",
    "| `pd.notna(valor)` | `pandas` | Devuelve `True` si el valor no es `NaN`, `NaT` ni `None`; evita guardar `float('nan')` en MongoDB. |\n",
    "| `timestamp.to_pydatetime()` | `pandas.Timestamp` | Convierte un `Timestamp` de pandas a `datetime` nativo de Python, compatible con BSON `ISODate`. |\n",
    "| `math.ceil(n / tamano_lote)` | `math` | Calcula el numero de lotes necesarios para procesar `n` documentos en bloques de `tamano_lote`. |",
]

NUEVA_CELDA = {
    "cell_type": "markdown",
    "id": "tabla-funciones-s14",
    "metadata": {},
    "source": TABLA_SOURCE,
}

# ---------- Modificar el notebook ----------
with open(NOTEBOOK_PATH, encoding="utf-8") as f:
    nb = json.load(f)

# Encontrar la posicion de la celda f3f1e8ca (introduccion de la Seccion 14)
ANCHOR_ID = "f3f1e8ca"
pos = None
for i, cell in enumerate(nb["cells"]):
    if cell.get("id") == ANCHOR_ID:
        pos = i
        break

if pos is None:
    sys.exit(f"[ERROR] No se encontro la celda con id '{ANCHOR_ID}'")

# Insertar la nueva celda DESPUES de la celda anchor
nb["cells"].insert(pos + 1, NUEVA_CELDA)

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

size_kb = os.path.getsize(NOTEBOOK_PATH) / 1024
print(f"[OK] Tabla insertada en posicion {pos + 1} (despues de celda '{ANCHOR_ID}')")
print(f"     Total celdas: {len(nb['cells'])}  |  {size_kb:.1f} KB")
