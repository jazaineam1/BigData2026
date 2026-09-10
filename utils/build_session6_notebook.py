#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera S6: contexto relacional del proceso priorizado por Laura.

S6 parte del producto de S5 (`s05_ancla_s06.json`). Neo4j aparece porque Laura
ya sabe qué revisar primero, pero necesita entender qué relaciones existen alrededor
del proceso antes de asignarlo a un auditor.

Cypher, driver y Aura Free contrastados con documentación vigente: 10-09-2026.
Fuentes: https://neo4j.com/docs/aura/getting-started/create-instance/
y https://neo4j.com/pricing/ (una instancia Free por cuenta; sin tarjeta).
La cuenta Aura y Colab requieren validación autenticada antes de clase.
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.make_notebook import code, md, save, validate

OUTPUT = "Cuadernos/6_Neo4j_Contexto_Relacional.ipynb"
WEB = "https://jazaineam1.github.io/BigData2026"
RAW = "https://raw.githubusercontent.com/jazaineam1/BigData2026/main"
COLAB = "https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/6_Neo4j_Contexto_Relacional.ipynb"
DATA = f"{RAW}/Datos/s06_contexto_relacional.csv"
MANIFEST = f"{RAW}/Datos/s06_contexto_relacional_manifest.json"
TUTORIAL = f"{WEB}/assets/tutoriales/neo4j-aura-s06-paso-a-paso.html"
LABORATORIO = f"{WEB}/assets/tutoriales/s06-laboratorio-guiado.html"
DIAGRAMS_DIR = ROOT / "assets" / "diagrams" / "session6"


def svg(nombre: str, alt: str) -> str:
    """Incrusta un SVG local (assets/diagrams/session6/) como data URI.

    El fuente sigue editable en esa carpeta; la copia incrustada evita que
    el estudiante vea un ícono roto si abre una versión aún no publicada.
    """
    ruta = DIAGRAMS_DIR / f"{nombre}.svg"
    if not ruta.exists():
        raise FileNotFoundError(ruta)
    uri = base64.b64encode(ruta.read_bytes()).decode("ascii")
    return f'<img src="data:image/svg+xml;base64,{uri}" alt="{alt}" style="max-width:100%;height:auto;">'

INTERACTIVITY = r'''
import base64, json, html as html_lib
from IPython.display import display, HTML

def pregunta_codificada(token):
    p = json.loads(base64.b64decode(token).decode("utf-8"))
    uid = f"s06-p{p['numero']}"
    opts = "".join(
        f'<label style="display:block;margin:8px 0"><input type="radio" name="{uid}" value="{i}"> {html_lib.escape(op)}</label>'
        for i, op in enumerate(p["opciones"])
    )
    # Escapar el atributo COMPLETO; la retroalimentación se inserta como texto.
    handler = (
        "const box=this.closest('[data-pregunta]');"
        "const e=box.querySelector('input:checked');"
        "const s=box.querySelector('[aria-live]');"
        "if(!e){s.textContent='Selecciona una opción.';return;}"
        f"const i=Number(e.value),r={json.dumps(p['retro'], ensure_ascii=False)};"
        f"const ok=i==={p['correcta']};"
        "s.textContent=(ok?'Correcto. ':'Incorrecto. ')+r[i];"
        "s.style.background=ok?'#dcfce7':'#fee2e2';"
        "s.style.color=ok?'#14532d':'#7f1d1d';"
        "s.style.padding='12px';"
    )
    handler = html_lib.escape(handler, quote=True)
    contador = str(p['numero']) + (f" de {p['total']}" if p.get('total') else '')
    box = (
        f'<div data-pregunta="{uid}" style="border:2px solid #1e40af;background:#eff6ff;color:#172554;border-radius:12px;padding:15px;margin:14px 0">'
        f'<strong>Pregunta {contador} — {html_lib.escape(p["tema"])}</strong>'
        f'<p style="background:#fef3c7;color:#713f12;padding:10px">{html_lib.escape(p.get("contexto", "Aplica lo que acabas de observar en el caso de Laura."))}</p>'
        f'<p>{html_lib.escape(p["pregunta"])}</p>{opts}'
        f'<button onclick="{handler}" '
        f'style="background:#1e40af;color:white;border:0;border-radius:7px;padding:8px 12px">Verificar respuesta</button>'
        f'<div id="r-{uid}" aria-live="polite"></div></div>'
    )
    display(HTML(box))

def tutorial(url, alto=720):
    box = f'<iframe src="{url}?embed=1" width="100%" height="{alto}" style="border:0;border-radius:10px;background:#faf7ef"></iframe>'
    box += f'<p><a href="{url}" target="_blank">Abrir tutorial en pantalla completa ↗</a></p>'
    display(HTML(box))

print("Soporte S6 listo.")
'''


def hidden(cell, title: str):
    cell["source"] = [f'#@title {title} {{ display-mode: "form" }}\n'] + cell["source"]
    cell["metadata"] = {
        "tags": ["hide-input"],
        "jupyter": {"source_hidden": True},
        "cellView": "form",
        "colab": {"formView": "both"},
    }
    return cell


def question_cell(numero, tema, pregunta, opciones, correcta, retro, contexto=None, total=None):
    payload = base64.b64encode(json.dumps({
        "numero": numero, "tema": tema, "pregunta": pregunta,
        "opciones": opciones, "correcta": correcta, "retro": retro,
        "contexto": contexto or "Aplica lo que acabas de observar en el caso de Laura.",
        "total": total,
    }, ensure_ascii=False).encode("utf-8")).decode("ascii")
    return hidden(code(f'pregunta_codificada("{payload}")'), f"Autoevaluación {numero} — {tema}")


LOAD_DATA = r'''
import json
import urllib.request
import hashlib
from pathlib import Path
import pandas as pd

DATA_URL = "https://raw.githubusercontent.com/jazaineam1/BigData2026/main/Datos/s06_contexto_relacional.csv"
MANIFEST_URL = "https://raw.githubusercontent.com/jazaineam1/BigData2026/main/Datos/s06_contexto_relacional_manifest.json"
# Se reutiliza el archivo local: también sirve si el docente lo compartió sin red.
rutas = []
for nombre, url in [("s06_contexto_relacional.csv", DATA_URL), ("s06_contexto_relacional_manifest.json", MANIFEST_URL)]:
    archivo = Path(nombre)
    if not archivo.is_file() and (Path("Datos") / nombre).is_file():
        archivo = Path("Datos") / nombre
    if not archivo.is_file():
        try:
            with urllib.request.urlopen(url, timeout=30) as respuesta:
                contenido = respuesta.read()
            archivo.write_bytes(contenido)
        except Exception as exc:
            raise RuntimeError("Carga fallida. Sube el CSV y el manifest del curso a Archivos y repite esta celda.") from exc
    rutas.append(archivo)

datos = pd.read_csv(rutas[0], dtype={"nit_entidad": str, "nit_proveedor": str, "id_proceso": str}, keep_default_na=False)
for columna in ["nit_entidad", "nit_proveedor", "id_proceso"]:
    datos[columna] = datos[columna].str.strip()
for columna in ["precio_base", "valor_adjudicado", "noticias_entidad"]:
    datos[columna] = pd.to_numeric(datos[columna], errors="coerce")
assert datos["nit_entidad"].ne("").all() and datos["id_proceso"].ne("").all(), "Falta una identidad obligatoria."
manifest = json.loads(rutas[1].read_text(encoding="utf-8-sig"))
huella_datos = hashlib.sha256(rutas[0].read_bytes()).hexdigest()
print("Filas disponibles:", len(datos))
print("Huella SHA256 del extracto:", huella_datos)
'''

SELECT_ANCHOR = r'''
ruta = input("Ruta de s05_ancla_s06.json (Enter = respaldo): ").strip()
if ruta:
    if not Path(ruta).is_file():
        raise FileNotFoundError("No encontré tu archivo. Corrige la ruta o deja Enter para elegir el respaldo explícitamente.")
    ancla_original = json.loads(Path(ruta).read_text(encoding="utf-8-sig"))
    if not isinstance(ancla_original, dict) or not ancla_original.get("nit_entidad") or not ancla_original.get("id_proceso"):
        raise ValueError("El ancla debe contener nit_entidad e id_proceso.")
    par = datos["id_proceso"].eq(str(ancla_original["id_proceso"]).strip()) & datos["nit_entidad"].eq(str(ancla_original["nit_entidad"]).strip()) & datos["tipo_registro"].eq("candidato_s05")
    if not par.any():
        raise ValueError("El proceso y su entidad no corresponden a los candidatos S5 de este extracto. Revisa el archivo.")
    origen_ancla = "archivo propio S5"
else:
    ancla_original = dict(manifest["ancla_pedagogica"])
    origen_ancla = "ancla pedagógica versionada"
print("Origen:", origen_ancla)
print(json.dumps(ancla_original, ensure_ascii=False, indent=2))
'''

PREPARE_HIST = r'''
nit_deseado = str(ancla_original["nit_entidad"]).strip()
hist = datos[datos["tipo_registro"].eq("historico_adjudicado")].copy()
assert hist["nit_proveedor"].ne("").all(), "Un registro histórico carece de NIT de proveedor."
# La identidad analítica es el NIT reportado. Los nombres se conservan como variantes.
nombres_proveedor = hist.groupby("nit_proveedor")["proveedor"].agg(lambda nombres: " / ".join(sorted(set(nombres))))
variantes = hist.groupby("nit_proveedor")["proveedor"].nunique()
print("NIT de proveedor con varios nombres:", int(variantes.gt(1).sum()))
hist_ancla = hist[hist["nit_entidad"].eq(nit_deseado)]
if hist_ancla.empty:
    print("Tu entidad no tiene historial en el extracto. El trabajo continúa con el respaldo declarado.")
    ancla_trabajo = dict(manifest["ancla_pedagogica"])
    nit_deseado = str(ancla_trabajo["nit_entidad"]).strip()
    hist_ancla = hist[hist["nit_entidad"].eq(nit_deseado)]
    uso_respaldo_s06 = True
else:
    ancla_trabajo = ancla_original
    uso_respaldo_s06 = origen_ancla != "archivo propio S5"
print("Entidad de trabajo:", ancla_trabajo["entidad"])
print("Procesos históricos:", hist_ancla["id_proceso"].nunique())
print("Proveedores distintos:", hist_ancla["nit_proveedor"].nunique())
'''

CONTRACT_PANDAS = r'''
# Ambas métricas usan NIT; el nombre es una etiqueta, no una segunda clave.
prov_ancla = hist_ancla.groupby("nit_proveedor")["id_proceso"].nunique().rename("procesos_con_entidad")
prov_global = hist.groupby("nit_proveedor")["nit_entidad"].nunique().rename("entidades_conectadas")
esperado_pd = pd.concat([prov_ancla, prov_global], axis=1).loc[prov_ancla.index].reset_index()
esperado_pd["procesos_con_entidad"] = esperado_pd["procesos_con_entidad"].astype(int)
esperado_pd["proveedor"] = esperado_pd["nit_proveedor"].map(nombres_proveedor)
esperado_pd = esperado_pd.sort_values(["entidades_conectadas", "procesos_con_entidad", "nit_proveedor"], ascending=[False, False, True]).head(10).reset_index(drop=True)
# Una entidad = un NIT también en el denominador de H2-R.
candidatas_hist = hist[hist["es_entidad_candidata_s05"]].copy()
candidatas_hist["conexiones_proveedor"] = candidatas_hist["nit_proveedor"].map(prov_global)
maximos_candidatas = candidatas_hist.groupby("nit_entidad")["conexiones_proveedor"].max()
MEDIANA_H2R = float(maximos_candidatas.median())
if "mediana_maximo_conectadas_por_nit" in manifest:
    assert MEDIANA_H2R == float(manifest["mediana_maximo_conectadas_por_nit"]), "La referencia por NIT no coincide con el extracto."
proveedor_h2r = esperado_pd.iloc[0].copy()
maximo_h2r = int(proveedor_h2r["entidades_conectadas"])
if uso_respaldo_s06:
    desenlace_h2r_pd = "no evaluable con mi ancla"
elif maximo_h2r > MEDIANA_H2R:
    desenlace_h2r_pd = "conexión más fuerte que la mediana de las candidatas de S5"
else:
    desenlace_h2r_pd = "conexión igual o menor que la mediana de las candidatas de S5"
print("Entidades de referencia:", len(maximos_candidatas))
print("Mediana de referencia (candidatas S5):", MEDIANA_H2R)
print("Proveedor que determina H2-R:", proveedor_h2r["nit_proveedor"], "| máximo:", maximo_h2r)
print("Desenlace H2-R (pandas):", desenlace_h2r_pd)
if uso_respaldo_s06:
    print("Comparación del respaldo:", maximo_h2r, ">", MEDIANA_H2R, "=", maximo_h2r > MEDIANA_H2R)
esperado_pd
'''

def build_cells():
    cells = [
        md(f'''<a href="{COLAB}" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Abrir S6 en Colab"></a>\n\n**Acceso público:** [página del curso]({WEB}/) · **Laboratorio guiado (checklist paso a paso):** [ábrelo en otra pestaña ↗]({LABORATORIO})'''),
        md("""
# Sesión 6 — De la fila priorizada al contexto relacional con Neo4j

## Universidad Central
> ### Facultad de Ingeniería y Ciencias Básicas
> ### Maestría en Analítica de Datos — BIG DATA (64491093)

**Caso conductor:** Compras Claras
**Pregunta profesional:** **Laura ya sabe qué proceso revisar primero. Antes de asignarlo a un auditor, ¿qué relaciones alrededor de ese proceso necesita ver para comprender su contexto?**

**Respuesta corta y herramienta:** Laura necesita seguir una cadena de conexiones —entidad → proceso → proveedor → otro proceso → otra entidad— sin perder el hilo en ningún salto. Eso es una pregunta sobre relaciones que se conectan entre sí, y la herramienta que la responde es una **base de datos de grafos: Neo4j**. El resto de la sesión explica por qué esa herramienta y no otra de las que ya conoces.

### Producto observable

Al terminar tendrás una **ficha relacional de revisión** con:

1. el proceso que llega desde S5;
2. el contexto de prensa heredado;
3. procesos históricos adjudicados de su entidad;
4. proveedores y otras entidades conectadas cuando el dato lo sostenga;
5. el contraste de H2-R, la hipótesis relacional de hoy (pandas ↔ Neo4j);
6. una decisión de modelado y una alternativa descartada;
7. un límite concreto;
8. `s06_contexto_procesos.jsonl`, entrada de la siguiente sesión.

**Entorno:** Google Colab, Python y Cypher; Windows necesita solo navegador.
**Autoevaluación no calificable:** falla aquí, que sale gratis. El hito se valora con la rúbrica del cuaderno.
**Objetivos:** modelar relaciones, verificar una consulta y defender una decisión con evidencia y límites.
"""),
        md(f'''
## El hilo del evaluador

{svg("01_hilo_s06", "Cadena S3 evidencia documental, S4 persistencia en Atlas, S5 bandeja priorizada con H1 refutada 0 de 77, S6 contexto relacional con la hipótesis H2-R")}

**Cómo se lee.** Cada sesión entrega el producto que abre la siguiente; aquí reconstruimos solo el contexto necesario para continuar.

**Qué nos dice.** S6 no es un tema nuevo suelto: es la siguiente pregunta sobre el mismo caso.

**Qué NO permite concluir todavía.** Que S6 continúe la cadena no significa que ya sepamos si hay algo irregular — seguimos sin esa evidencia.

**Qué error común.** Tratar cada sesión como un capítulo independiente en vez de un paso de la misma investigación.
'''),
        md("""
## Neo4j: qué es, y por qué aparece aquí

**Neo4j es una base de datos de grafos de propiedades:** representa actores como nodos y conexiones como relaciones dirigidas, ambos con propiedades. Cypher permite expresar el patrón que queremos recorrer.

La necesidad de Laura es seguir Entidad → Proceso → Proveedor → Proceso → Entidad y conservar el contexto de cada conexión.

| Modelo | Cómo representa la pregunta | Qué considerar |
|---|---|---|
| SQL / MongoDB | tablas/documentos y cruces mediante `JOIN` / `$lookup` | también pueden responderla; importan índices, planes y volumen |
| Cassandra | una tabla preparada para una consulta conocida | cambiar la pregunta puede exigir otra tabla o precomputación |
| Neo4j | nodos, relaciones y patrones de caminos | facilita expresar recorridos; el costo crece con las coincidencias y ramificaciones |

**PARA LLEVAR.** Elegimos el grafo por cómo expresa la pregunta. El contrato pandas comprobará la respuesta, no una ventaja de velocidad.

### La misma idea en otros contextos

Estos son ejemplos conceptuales de modelado; no afirmaciones sobre qué motor usa una empresa.

| Contexto | Nodo | Relación | Pregunta |
|---|---|---|---|
| Red profesional | persona, empresa | `TRABAJA_EN`, `CONOCE_A` | ¿qué contacto compartimos? |
| Rutas | intersección | `CONECTA_CON` | ¿qué caminos llegan al destino? |
| Recomendaciones | usuario, contenido | `VIO` | ¿qué contenido comparten usuarios? |
| Transferencias | cuenta | `TRANSFIRIO_A` | ¿qué cuentas están conectadas? |

**Qué error común.** Suponer que una flecha hace constante el costo de cualquier recorrido o demuestra una conducta.
"""),
        md('''
## Mapa de la sesión

| Bloque | Rol | Pregunta | Herramienta | Qué queda |
|---|---|---|---|---|
| 1. Recuperar el ancla | 🧠 ENTIENDE | ¿qué proceso llega desde S5? | Colab + JSON de S5 | proceso + entidad + prensa |
| 2. Preparar contexto | 🧠 ENTIENDE | ¿qué historial rodea esa entidad? | pandas | tabla de contraste |
| 3. Diseñar | 🧠 ENTIENDE | ¿qué es nodo y qué es relación? | papel + cuaderno | Entidad → Proceso → Proveedor |
| 4. Contrato pandas | ▶️ EJECUTA | ¿qué debe responder el grafo? | pandas | resultado esperado |
| 5. AuraDB | ▶️ EJECUTA | ¿cómo levantamos el servicio? | tutorial + Neo4j Aura | conexión real |
| 6. Cypher | ▶️ EJECUTA | ¿cómo cargamos y recorremos relaciones? | Cypher/Neo4j | grafo consultable |
| 7. Verificar | 🧠 + ▶️ | ¿Neo4j conserva la respuesta? | pandas + Neo4j | pandas = Neo4j |
| 8. Hito | ✏️ MODIFICA | ¿qué puede sostener Laura? | Colab | ficha + límite + export |

### Semáforo de código

- 🧠 **ENTIENDE:** debes poder explicarlo con tus palabras.
- ▶️ **EJECUTA:** corre la celda y verifica la salida; **no necesitas escribirla de memoria**.
- ✏️ **MODIFICA:** cambia únicamente el dato señalado y observa qué ocurre.
'''),
        hidden(code(INTERACTIVITY), "Preparar interactividad"),
        md('''
---
## 1. Recuperar el proceso que Laura abrió en S5

S5 dejó `s05_ancla_s06.json`. Súbelo al panel **Archivos** de Colab y escribe su ruta. Si lo perdiste, la clase no se bloquea: el dataset trae una **ancla pedagógica real** con historial útil.

**OJO.** El respaldo permite aprender Neo4j, pero el hito declara que no se usó el archivo propio.
'''),
        hidden(code(LOAD_DATA), "Cargar o recuperar el extracto"),
        code(SELECT_ANCHOR),
        md('''
### Cómo se lee la entrada

**Cómo se lee.** El ancla identifica un proceso que ya sobrevivió a la regla de S5. El extracto histórico añade hechos adjudicados sin cambiar por qué ese proceso fue priorizado.

**Qué nos dice.** S6 continúa una decisión ya tomada.

**Qué NO permite concluir todavía.** Tener historial contractual no significa que exista una relación problemática.

**Qué error común.** Volver a construir los 77 candidatos. Eso repetiría S5.
'''),
        md("""
### Procedencia y unidad de observación
El extracto se construye con [build_session6_graph_data.py](https://github.com/jazaineam1/BigData2026/blob/main/utils/build_session6_graph_data.py), a partir de los chunks SECOP y la bandeja S5 versionados. El estudiante descarga un archivo del curso; no hace recolección masiva contra SECOP.

**Selección:** entidades mencionadas en el corpus de prensa → contratación directa → cero respuestas (1.000 → 163 → 77). Se toman registros marcados como adjudicados con proveedor informado de esas entidades y se amplía a otras entidades que comparten esos NIT de proveedor. Se deduplican pares proceso–proveedor; se conservan los candidatos como ancla.

**Unidad:** registro candidato o par proceso–proveedor histórico. Una fila no siempre es un contrato único y no es una observación independiente de las demás.

| Campo | Significado y uso |
|---|---|
| `tipo_registro` | candidato S5 o histórico adjudicado; decide si hay relación hacia proveedor |
| `id_proceso`, `nit_entidad`, `nit_proveedor` | identidades reportadas, leídas como texto; no verifican identidad jurídica |
| `nombre_proceso`, `descripcion`, `url_secop` | texto y enlace del proceso, reutilizables en S7 |
| `fecha_publicacion` | fecha del registro; el extracto no impone precedencia respecto del candidato |
| `precio_base`, `valor_adjudicado` | presupuesto base y valor reportado de adjudicación; no son intercambiables |
| `noticias_entidad`, `nivel_menciones` | contexto de prensa de la entidad; no evidencia directa del proceso |
| `es_proceso_candidato_s05`, `es_entidad_candidata_s05` | delimitan la selección S5 y las entidades de referencia |
| `referencia`, `modalidad`, departamentos, nombres | contexto descriptivo del proceso y los actores |

**OJO.** “Histórico” significa adjudicado dentro de este archivo, no necesariamente anterior a tu candidato. No ordenamos alertas temporales ni comparamos riesgo. Un corpus seleccionado por prensa no representa todo SECOP. La fecha de extracción original no está declarada en el manifest; la huella SHA256 identifica el archivo usado, pero no reemplaza esa fecha.
"""),
        code("""
fechas = pd.to_datetime(datos["fecha_publicacion"], errors="coerce", utc=True, format="mixed")
print("Fechas de publicación válidas:", int(fechas.notna().sum()), "de", len(datos))
print("Intervalo observado:", fechas.min(), "a", fechas.max())
"""),
        md("""
**Cómo se lee.** El intervalo usa las fechas que pudieron interpretarse; no es la fecha de descarga.

**Qué nos dice.** Delimita temporalmente lo que contiene este archivo.

**Qué NO permite concluir todavía.** No establece qué sabía Laura al priorizar: falta una fecha de corte y filtrar cada relación anterior a ella.

**Qué error común.** Convertir relaciones posteriores en señales disponibles antes de la adjudicación. `to_datetime(errors="coerce", utc=True)` convierte fechas y deja inválidas como NaT; no inventa fechas.
"""),
        md('''
## H2-R: la hipótesis relacional de esta sesión

S5 cerró con una hipótesis de prensa: **H1** — ¿aparece literalmente alguno de los 77 IDs de proceso en título o subtítulo de una noticia? El resultado fue `0/77`: **H1 literal refutada**, y la prensa quedó especificada como contexto de entidad, no como evidencia directa de un proceso.

S6 abre una hipótesis distinta, ahora relacional:

> **H2-R.** El proveedor histórico más conectado de la entidad del proceso elegido en S5 está conectado con más entidades que la mediana de esa misma conexión entre los 28 NIT de entidades candidatas de S5 que sí tienen historial.

No es una prueba estadística inferencial: es una comparación empírica y falsable sobre este extracto — el resultado depende de qué proceso elegiste en S5, y varía de una persona a otra.

| Sabemos (llega de S5) | No sabemos todavía |
|---|---|
| proceso, entidad, valor, modalidad | proveedores históricos de esa entidad |
| contexto de prensa (H1 ya refutada) | otras entidades conectadas por el mismo proveedor |
| que el proceso sobrevivió la regla `1.000→163→77` | caminos relacionales entre entidades |

Lo que sigue, con nombres inventados, es exactamente H2-R en miniatura.
'''),
        md(f'''
---
## 2. El candidato y el historial cumplen funciones distintas

### Ejemplo manual pequeño (nombres inventados, para pensar antes de programar)

{svg("02_ejemplo_manual", "La Alcaldía de Ejemplo y la Gobernación de Prueba publican procesos distintos, ambos adjudicados a Constructora Ejemplo S.A.S.")}

Mirando solo este dibujo, sin ninguna tabla: **Constructora Ejemplo S.A.S. aparece conectada con dos entidades distintas** —la Alcaldía de Ejemplo y la Gobernación de Prueba— a través de dos procesos separados. El dibujo hace explícito el camino; una tabla también permite calcularlo mediante cruces. Esto ilustra la conectividad. Para completar H2-R necesitamos una referencia: si los máximos de tres entidades fueran 1, 2 y 4, la mediana sería 2; tener dos conexiones no supera esa mediana.

El proceso candidato que trae S5 puede no estar adjudicado todavía: **no le inventamos un proveedor**. El historial adjudicado —registros adjudicados de la misma entidad— es lo que sí aporta proveedores reales y conexiones observadas.
'''),
        question_cell(1, 'H2-R en miniatura', '¿Qué comparación puedes defender?', ['2 supera la mediana porque conecta más de una entidad.', '2 es igual a la mediana 2; no la supera.', '2 supera la media 7/3.', 'El dibujo demuestra irregularidad.'], 1, ['Conectar más de una entidad no basta: H2-R compara contra la mediana de máximos. Aquí vale 2.', 'Ordenar 1, 2, 4 deja 2 en el centro. Dos conexiones igualan ese umbral; no lo superan.', 'La referencia acordada es la mediana, no la media. Además 2 es menor que 7/3.', 'Las flechas describen adjudicaciones registradas. Faltan condiciones de competencia y otros hechos para evaluar conducta.'], 'Los máximos por entidad son 1, 2 y 4. El proveedor de Ejemplo conecta dos entidades.', 10),
        question_cell(1, 'Evidencia del modelo', '¿Cuándo dibujar ADJUDICADO_A?', ['Cuando el proveedor aparece en una noticia de la entidad.', 'Cuando exista un registro histórico adjudicado con identificador de proveedor.', 'Cuando el proceso tenga un presupuesto alto.', 'Asignando el proveedor más conectado de la entidad al candidato.'], 1, ['La noticia es contexto de entidad: no prueba la adjudicación de ese proceso.', 'La relación representa un hecho de la fuente. La carga debe exigir registro histórico y NIT informado.', 'El presupuesto no identifica quién recibió una adjudicación. No permite completar esa relación.', 'El historial pertenece a otros procesos. Trasladar su proveedor al candidato inventaría un hecho.'], 'El proceso de S5 es candidato; el extracto le reserva un registro sin proveedor.', 10),
        code(PREPARE_HIST),
        md('''
### Interpretación del contexto histórico

**Cómo se lee.** Los conteos corresponden al historial adjudicado disponible para la entidad de trabajo, no al proceso candidato aislado.

**Qué nos dice.** Hay material relacional suficiente para preguntar por proveedores y conexiones entre procesos.

**Qué NO permite concluir todavía.** Más procesos o proveedores no equivalen a mayor riesgo. Faltan criterios sobre competencia, temporalidad y comportamiento esperado de la entidad.

**Qué error común.** Usar el número de contratos como una puntuación de sospecha.
'''),
        question_cell(1, 'Identificadores', '¿Cómo construir el contrato comparable con el grafo?', ['Agrupar por NIT y conservar variantes del nombre.', 'Agrupar por nombre y NIT para aumentar la precisión.', 'Eliminar una adjudicación porque repite NIT.', 'Convertir cada nombre en un proveedor nuevo.'], 0, ['El grafo identifica por NIT reportado. Conservamos variantes para revisar identidad sin separar automáticamente los conteos.', 'Añadir nombre a la clave divide variantes del mismo identificador y puede romper la igualdad con Neo4j.', 'Un proveedor puede tener muchos procesos. Eliminar una adjudicación por NIT destruye hechos.', 'El nombre puede variar sin que cambie el identificador. Hay que revisar las variantes, no inventar actores.'], 'Dos filas tienen el mismo NIT de proveedor y nombres con espacios diferentes.', 10),
        md('''
---
## 3. Diseñar el grafo antes de escribir la consulta final

Antes de escribir Cypher, cinco palabras y nada más.

| Concepto | Qué es | Ejemplo (Constructora Ejemplo S.A.S.) |
|---|---|---|
| Nodo | una entidad del dominio | el proveedor mismo |
| Label | la categoría del nodo | `Proveedor` |
| Propiedad | un dato guardado en el nodo | `nit: "900123456"` |
| Relación | un hecho dirigido entre dos nodos | `ADJUDICADO_A` |
| Camino | una secuencia de nodos y relaciones | Entidad → Proceso → Proveedor |

**Los mismos 5 conceptos, en LinkedIn:** Nodo = una persona · Label = `Persona` o `Empresa` · Propiedad = `nombre: "Ana"` · Relación = `ES_CONTACTO_DE` · Camino = la cadena de contactos que te conecta con alguien que nunca has visto. Es exactamente el mismo vocabulario, sobre datos distintos.

### Cómo se lee `(e:Entidad {nit:"123"})`

- `e` — variable con la que nombras este nodo en el resto de la consulta.
- `Entidad` — el label: la categoría a la que pertenece.
- `{nit:"123"}` — una propiedad que identifica cuál Entidad exactamente.

Con eso ya puedes leer un patrón completo: `(e:Entidad)-[:PUBLICA]->(p:Proceso)` es "un nodo Entidad conectado, mediante la relación PUBLICA, a un nodo Proceso".
'''),
        md("""
## Rúbrica S06

Lee los criterios antes del laboratorio. Total: 100 puntos. **Completo = peso completo; Parcial = mitad; Sin evidencia = 0.** Para convertir a escala 0–5 divide el total entre 20. El respaldo permite entregar un avance; la evidencia de Neo4j se completa después de resolver el acceso.

| Criterio | Completo | Parcial | Sin evidencia | Peso |
|---|---|---|---|---:|
| Continuidad y traza | ID y NIT coherentes, origen/respaldo, autor, fecha y enlace al commit privado | conserva ID y origen pero falta al menos un elemento de traza | no identifica el proceso ni el origen | 15 |
| Modelo | justifica Proceso como nodo para su consulta y explica alternativa descartada | justifica solo una de las dos opciones | reproduce el patrón sin justificación | 20 |
| Ejecución | consulta propia ejecutada en Neo4j, vecindario y filtro de otras entidades correctos | resultados en pandas o solo consulta resuelta en Neo4j | sin resultados ejecutados | 20 |
| Verificación | igualdad con pandas comprobada y carga repetida con conteos iguales | resultados de ambos motores sin comparación o repetición completa | un solo motor o ninguna evidencia | 15 |
| Decisión y H2-R | separa proveedor del máximo, mediana y proveedor explorado; explica elección y entrega JSONL | falta uno o más de esos elementos, pero incluye números propios | respuesta sin números de su ejecución | 15 |
| Límite | conclusión que no puede sostener y dato concreto que falta | nombra solo la conclusión o solo el dato | afirma irregularidad por conectividad | 15 |

Guarda ficha y JSONL en `hitos/s06/` del repositorio **privado** del equipo. Pega el enlace del commit en la entrega del aula; no publiques nombres ni entregas en el repositorio del curso. Conserva también tu consulta propia en ese commit.
"""),
        md("""
### EJERCICIO S06-PATRON — un solo hueco

Completa **solo** el nombre de la relación entre un proceso histórico y el proveedor al que fue adjudicado.

**Qué debe verse si salió bien:** el patrón expresa el hecho contractual y aparece la confirmación “Patrón correcto”.
**Error probable:** dejar `____` o inventar un verbo que no representa el hecho del dato.  
**Qué significa:** el modelo aún no expresa la semántica contractual que luego recorrerá `MATCH`.

<details><summary><strong>Recuperación si te atascaste</strong></summary>
La relación se llama <code>ADJUDICADO_A</code>. Cámbiala y vuelve a ejecutar.
</details>
"""),
        code("""
RELACION_PROCESO_PROVEEDOR = "____"  # reemplaza únicamente ____
patron_estudiante = f"(p:Proceso)-[:{RELACION_PROCESO_PROVEEDOR}]->(v:Proveedor)"
print(patron_estudiante)

if RELACION_PROCESO_PROVEEDOR != "ADJUDICADO_A":
    raise ValueError("Revisa el hecho contractual que conecta Proceso con Proveedor.")
print("Patrón correcto: la relación expresa una adjudicación observada.")
"""),
        md(f'''
### Modelo mínimo que usaremos

{svg("03_modelo_minimo", "Entidad publica un Proceso, que es adjudicado a un Proveedor")}

`(e:Entidad)-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)` — así se escribe ese mismo dibujo en Cypher.

| Elemento | Identificador | Decisión |
|---|---|---|
| `Entidad` | NIT | actor que publica |
| `Proceso` | ID SECOP | nodo con texto, valor, modalidad y URL |
| `Proveedor` | NIT | actor adjudicado que puede conectar procesos |
| `PUBLICA` | relación | quién publica el proceso |
| `ADJUDICADO_A` | relación | a quién se adjudicó un proceso histórico |

### La alternativa que descartamos

| Opción | Cómo se vería | Por qué no la usamos hoy |
|---|---|---|
| **Proceso como nodo** (la que usamos) | `(e)-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v)` | `Proceso` participa en caminos propios y S7 reutiliza su texto |
| Proceso como propiedad de una relación directa | `(e:Entidad)-[:CONTRATO {{id_proceso:"...", valor:...}}]->(v:Proveedor)` | más simple, pero un proceso deja de ser algo que puedas recorrer o conectar con otra cosa por sí mismo |

`Proceso` queda como nodo porque hoy participa en caminos y la siguiente sesión reutilizará su texto.
'''),
        md("""
### Función usada: `MERGE`

- **Para qué sirve:** encuentra un nodo o relación que ya existe con esa identidad, o lo crea si no existe usando el patrón indicado. Para garantizar identidad por NIT/ID usamos restricciones únicas.
- **Por qué aparece:** el runtime de Colab se reinicia solo, y el receso pasa a mitad de sesión. Sin `MERGE`, volver a ejecutar la carga crearía un segundo `Proceso 2024-001` idéntico al primero.
- **Intuición en palabras:** es como decir “busca esta persona por su cédula; si no está, regístrala — y protege esa identidad con una restricción única”.
- **Ejemplo manual:** `MERGE (p:Proceso {id:"2024-001"})` la primera vez crea el nodo; ejecutado otra vez, lo encuentra y no crea uno nuevo.
- **Cómo se interpreta la salida:** si el número de nodos no crece al repetir la carga, `MERGE` funcionó como esperado.
- **Error frecuente:** usar `CREATE` en su lugar y terminar con varios nodos duplicados del mismo proceso.

Parámetro del patrón: el `id` estable. Las propiedades que cambian se actualizan con `SET`. Consulta la [documentación de MERGE](https://neo4j.com/docs/cypher-manual/current/clauses/merge/).
"""),
        md('''
### Cypher mínimo

| Construcción | Para qué sirve | Qué devuelve/cambia | Error frecuente |
|---|---|---|---|
| `MERGE` | encuentra o crea un patrón | nodos/relaciones persistidos | creer que siempre crea otro nodo |
| `MATCH` | busca patrones | filas con coincidencias | leerlo como un `SELECT *` sin relaciones |
| `WHERE` | filtra | menos coincidencias | filtrar antes de entender el patrón |
| `WITH` | encadena etapas | variables para la etapa siguiente | olvidar qué variables siguen vivas |
| `RETURN` | define la salida | columnas del resultado | confundir salida con persistencia |
| `ORDER BY` / `LIMIT` | ordena y acota | resultado priorizado | asumir orden si no se pidió |

**PARA LLEVAR.** La flecha es parte de la consulta: no es decoración visual.
'''),
        question_cell(1, 'Identidad e idempotencia', '¿Qué combinación protege la identidad del nodo?', ['CREATE en cada ejecución.', 'MERGE incluyendo el nombre cambiante como identidad.', 'MERGE por ID estable y restricción de unicidad; SET para propiedades.', 'LIMIT 1 después de CREATE.'], 2, ['CREATE agrega nodos; repetirlo puede duplicar el mismo proceso.', 'Si cambia una propiedad del patrón, MERGE puede buscar otro patrón. La identidad debe ser el ID estable.', 'El ID define el nodo, la restricción protege su unicidad y SET actualiza atributos sin cambiar su identidad.', 'LIMIT restringe filas de salida; no deshace los nodos creados.'], 'La carga se repite después del receso. El ID del proceso permanece estable.', 10),
        md('''
---
## 4. Contrato de resultado: primero pandas

Antes de usar Neo4j calculamos qué proveedores de la entidad ancla también aparecen en otras entidades del extracto. Luego exigiremos a Neo4j la misma respuesta.
'''),
        code(CONTRACT_PANDAS),
        md("""
### Interpretación del contrato pandas y del desenlace H2-R

**Cómo se lee.** `procesos_con_entidad` cuenta procesos adjudicados de la entidad ancla; `entidades_conectadas` cuenta entidades distintas asociadas al mismo NIT de proveedor. El desenlace H2-R compara tu máximo contra la mediana de esa misma métrica entre los 28 NIT de entidades candidatas de S5 que tienen historial — no contra el universo completo de proveedores, que es demasiado disperso para discriminar.

**Qué nos dice.** El grafo debe reproducir la tabla y el máximo. Con ancla propia se evalúa H2-R; con respaldo se muestra la comparación y se declara su origen. Los 32 pares NIT–nombre del manifest histórico representan 28 NIT; por eso recalculamos una mediana de 21 por identidad, en lugar de 22 por nombre.

**Qué NO permite concluir todavía.** Repetición o conectividad no equivale a favorecimiento, colusión ni irregularidad. Faltarían evidencia sobre competencia, temporalidad, propiedad/representación y criterios de adjudicación.

**Qué error común.** Llamar “sospechoso” al proveedor que queda primero, o llamar “aceptada”/“rechazada” al desenlace de H2-R — es una comparación descriptiva, no una prueba estadística.

**Identidad y denominador:** agrupamos por NIT reportado; conservamos los nombres como variantes. Un identificador compartido por una aseguradora y una unión temporal necesita verificación jurídica antes de interpretar que son el mismo actor. La mediana es de máximos por entidad, no de todos los proveedores.

**Funciones usadas:** `groupby` define la clave; `nunique` cuenta valores distintos; `map` agrega una etiqueta por NIT; `median` devuelve el punto central. No uses el nombre como segunda clave: separaría variantes del mismo identificador.
"""),
        question_cell(1, 'Mediana de referencia', '¿Qué representa la mediana H2-R?', ['La mediana del número de contratos de todos los proveedores.', 'El umbral que prueba riesgo.', 'El punto central de los máximos de conectividad por entidad candidata con historial.', 'El promedio de conexiones del proveedor elegido para explorar.'], 2, ['H2-R cuenta entidades conectadas, no contratos, y resume un máximo por entidad candidata.', 'Es una referencia descriptiva de una muestra seleccionada; no existe aquí un modelo de riesgo.', 'Cada NIT de entidad aporta un máximo; ordenar esos máximos permite calcular la mediana de comparación.', 'El proveedor explorado puede no ser el máximo. La referencia se construye con todas las entidades candidatas con historial.'], 'El cuaderno calcula un máximo por cada entidad candidata que tiene historial.', 10),
        md("""
### RECUPERACIÓN S06 — si Colab reinició
Si perdiste las variables, ejecuta la celda siguiente: reconstruye interactividad, datos, ancla y contrato pandas. Vuelve a indicar el archivo propio o el respaldo. Si todo sigue en memoria, continúa con Aura.

**OJO.** Después debes volver a conectar y repetir la carga; las consultas posteriores necesitan esa conexión. La reconstrucción reutiliza los archivos descargados o subidos. Si el runtime perdió también los archivos y no hay red, sube las copias que entregó el docente.
"""),
        hidden(code("# RECUPERACIÓN S06\n" + INTERACTIVITY + "\n" + LOAD_DATA + "\n" + SELECT_ANCHOR + "\n" + PREPARE_HIST + "\n" + CONTRACT_PANDAS + '\nprint("Estado S6 reconstruido desde archivos versionados o copia local.")'), "Recuperar estado S6"),
        md("""
---
## 5. Tutorial visual — AuraDB

**HAZ ESTO AHORA.** Vuelve cuando `RETURN 1 AS conexion` funcione en Query y tengas URI, usuario y contraseña.

El HTML es **instrumental**: muestra el camino de interfaz. Las pantallas dibujadas están rotuladas como representaciones; no se presentan como capturas autenticadas.

Si Aura no está disponible, elige **RESPALDO** en la celda siguiente. Continúa con el mismo proveedor, filtro, ficha y exportación en pandas. La ficha marcará Cypher, CRUD y comparación como pendientes; para completarlos vuelve a conectar y recorre los bloques desde la carga. No se necesita una cuenta de servicio ni tarjeta para el trabajo conceptual.

[Documentación de Aura](https://neo4j.com/docs/aura/) · [Driver de Python](https://neo4j.com/docs/python-manual/current/). Usa una instancia de práctica nueva o dedicada a esta versión del cuaderno: una carga anterior defectuosa puede conservar relaciones ajenas al extracto.
"""),
        hidden(code(f'tutorial({TUTORIAL!r})'), "Abrir tutorial Neo4j Aura"),
        hidden(code("""
# Elige una ruta explícita. El respaldo conserva datos y decisiones, pero no ejecuta Cypher.
modo = input("Enter = Aura; escribe RESPALDO si no puedes usar el servicio: ").strip().upper()
if modo not in ["", "RESPALDO"]:
    raise ValueError("Usa Enter o RESPALDO.")
modo_neo4j = modo != "RESPALDO"
if globals().get("driver") is not None:
    driver.close()
driver = None
if modo_neo4j:
    import sys, subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "neo4j>=6,<7"])
    from getpass import getpass
    from neo4j import GraphDatabase
    URI = input("Connection URI: ").strip()
    USER = input("User name: ").strip()
    PASSWORD = getpass("Password (no se muestra): ")
    if not URI or not USER or not PASSWORD:
        raise ValueError("URI, usuario y contraseña son obligatorios.")
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    del PASSWORD
    try:
        driver.verify_connectivity()
    except Exception:
        driver.close()
        driver = None
        raise RuntimeError("Conexión fallida. Revisa el diagnóstico del tutorial o repite esta celda y elige RESPALDO.") from None
    print("Conexión Neo4j verificada.")
else:
    print("RESPALDO pandas: Neo4j y CRUD pendientes; no se declarará equivalencia comprobada.")
"""), "Conectar Aura o activar respaldo"),
        md('''
---
## 6. Identidad y carga idempotente

Primero creamos restricciones. Después `UNWIND` recibe una lista de filas desde Python y `MERGE` reutiliza nodos ya existentes.

**Qué debe verse:** tres restricciones válidas y una carga que puede repetirse sin multiplicar el mismo NIT/ID.  
**Error probable:** autenticación o conectividad antes de ejecutar Cypher. Eso es un problema instrumental, no un problema del modelo; usa el diagnóstico del tutorial.
'''),
        code("""
if modo_neo4j:
    constraints = [
        "CREATE CONSTRAINT entidad_nit IF NOT EXISTS FOR (e:Entidad) REQUIRE e.nit IS UNIQUE",
        "CREATE CONSTRAINT proceso_id IF NOT EXISTS FOR (p:Proceso) REQUIRE p.id IS UNIQUE",
        "CREATE CONSTRAINT proveedor_nit IF NOT EXISTS FOR (v:Proveedor) REQUIRE v.nit IS UNIQUE",
    ]
    for q in constraints:
        driver.execute_query(q)
    print("Restricciones listas.")
else:
    print("Restricciones Neo4j pendientes (respaldo).")
"""),
        md("""
### Función usada: `UNWIND`

- **Para qué sirve:** convierte una lista (de filas, de diccionarios) en filas individuales que Cypher procesa una por una dentro de la misma consulta.
- **Por qué aparece:** vas a cargar miles de filas de una sola vez desde Python; sin `UNWIND` tendrías que enviar una consulta por fila.
- **Intuición en palabras:** es como decir “toma esta lista de invitados y preséntamelos uno por uno”, para hacer lo mismo con cada uno.
- **Ejemplo manual:** con `filas = [{"id":"P1"}, {"id":"P2"}, {"id":"P3"}]`, `UNWIND $filas AS fila` produce tres filas dentro de una sola consulta: una con `fila.id = "P1"`, otra con `"P2"`, otra con `"P3"`.
- **Cómo se interpreta la salida:** UNWIND produce filas; las cláusulas posteriores determinan si encuentran, crean o filtran elementos.
- **Error frecuente:** usar `filas` (la lista completa) en vez de `fila` (el elemento actual) dentro del patrón.

Parámetro: `$filas`, la lista enviada por Python. Salida: una variable `fila` por elemento. [Referencia UNWIND](https://neo4j.com/docs/cypher-manual/current/clauses/unwind/).
"""),
        question_cell(1, 'Carga sin relaciones inventadas', '¿Qué debe llegar a la carga ADJUDICADO_A?', ['Las 2.109 filas porque NaN equivale a un proveedor desconocido.', 'Solo las 2.032 históricas con NIT de proveedor informado.', 'Solo las 77 candidatas.', 'Una relación por cada entidad, sin proceso.'], 1, ['Una ausencia no es un actor. Crear un nodo compartido para ella conectaría procesos sin evidencia.', 'El tipo de registro y la presencia del NIT delimitan las adjudicaciones. UNWIND convierte esa lista en filas dentro de la consulta.', 'Los candidatos no aportan proveedor en este extracto; su función es anclar la pregunta.', 'La adjudicación se registra por proceso y proveedor. Saltarse el proceso pierde la unidad del hecho.'], 'Hay 2.109 filas: 77 candidatas sin proveedor y 2.032 históricas adjudicadas.', 10),
        code("""
cols = [
    "entidad", "nit_entidad", "departamento_entidad", "id_proceso", "referencia",
    "nombre_proceso", "descripcion", "precio_base", "modalidad", "proveedor",
    "nit_proveedor", "departamento_proveedor", "noticias_entidad", "nivel_menciones",
    "tipo_registro", "url_secop", "es_proceso_candidato_s05", "es_entidad_candidata_s05",
]
# Convertir a object permite representar ausencias numéricas como None real.
para_carga = datos[cols].copy()
para_carga["proveedor"] = para_carga["nit_proveedor"].map(nombres_proveedor)
nombres_entidad = datos.groupby("nit_entidad")["entidad"].agg(lambda nombres: " / ".join(sorted(set(nombres))))
para_carga["entidad"] = para_carga["nit_entidad"].map(nombres_entidad)
rows = para_carga.astype(object).where(pd.notna(para_carga), None).to_dict("records")
rows_proveedor = [r for r in rows if r["tipo_registro"] == "historico_adjudicado" and r["nit_proveedor"] not in [None, ""]]
assert len(rows_proveedor) == len(hist), "Las adjudicaciones deben corresponder al historial."
assert all(isinstance(r["nit_proveedor"], str) for r in rows_proveedor)
print("Carga preparada:", len(rows), "filas;", len(rows_proveedor), "adjudicaciones válidas.")

query_base = '''
UNWIND $filas AS fila
MERGE (e:Entidad {nit: toString(fila.nit_entidad)})
SET e.nombre = fila.entidad,
    e.departamento = fila.departamento_entidad,
    e.es_candidata_s05 = fila.es_entidad_candidata_s05,
    e.noticias_entidad = fila.noticias_entidad,
    e.nivel_menciones = fila.nivel_menciones
MERGE (p:Proceso {id: fila.id_proceso})
SET p.referencia = fila.referencia,
    p.nombre = fila.nombre_proceso,
    p.descripcion = fila.descripcion,
    p.valor = fila.precio_base,
    p.modalidad = fila.modalidad,
    p.url = fila.url_secop,
    p.es_candidato_s05 = fila.es_proceso_candidato_s05
MERGE (e)-[:PUBLICA]->(p)
'''
if modo_neo4j:
    driver.execute_query(query_base, filas=rows)

query_proveedor = '''
UNWIND $filas AS fila
MATCH (p:Proceso {id: fila.id_proceso})
MERGE (v:Proveedor {nit: toString(fila.nit_proveedor)})
SET v.nombre = fila.proveedor, v.departamento = fila.departamento_proveedor
MERGE (p)-[:ADJUDICADO_A]->(v)
'''
if modo_neo4j:
    driver.execute_query(query_proveedor, filas=rows_proveedor)
    print("Carga lista:", len(rows), "filas;", len(rows_proveedor), "adjudicaciones.")
else:
    print("Carga Neo4j pendiente (respaldo).")
"""),
        code("""
if modo_neo4j:
    consulta_tamano = '''
    MATCH (n) WHERE n:Entidad OR n:Proceso OR n:Proveedor
    WITH count(n) AS nodos
    MATCH ()-[r:PUBLICA|ADJUDICADO_A]->()
    RETURN nodos, count(r) AS relaciones
    '''
    antes_carga = driver.execute_query(consulta_tamano).records[0].data()
    driver.execute_query(query_base, filas=rows)
    driver.execute_query(query_proveedor, filas=rows_proveedor)
    despues_carga = driver.execute_query(consulta_tamano).records[0].data()
    carga_repetida = antes_carga == despues_carga
    assert carga_repetida, "La carga repetida alteró los conteos. Revisa IDs y restricciones."
    print("Carga repetida sin crecimiento:", carga_repetida, "|", despues_carga)
else:
    carga_repetida = None
    print("Idempotencia en Neo4j: PENDIENTE.")
"""),
        md("""
**Cómo se lee.** Comparamos nodos y relaciones antes y después de repetir exactamente la carga.

**Qué nos dice.** Si no crecen, la repetición preserva los conteos en esta instancia y ejecución.

**Qué NO permite concluir todavía.** No prueba concurrencia ni ausencia de datos antiguos; hace falta controlar qué había cargado antes.

**Qué error común.** Usar igualdad de conteos como prueba de que cada propiedad es correcta.
"""),
        md("""
**Cómo se lee.** Son 2.109 registros de entrada y 2.032 adjudicaciones históricas; varios registros pueden representar un mismo proceso.

**Qué nos dice.** Los 77 registros candidatos no generan una adjudicación sin evidencia histórica.

**Qué NO permite concluir todavía.** Preparar filas no confirma escritura en Aura; hace falta conexión y consulta al motor.

**Qué error común.** Confundir un NIT ausente con un proveedor, o filas de entrada con nodos creados. Repite la carga y verifica que los conteos del grafo se mantengan.
"""),
        md('''
### Antes de la consulta completa: qué agrega cada salto

Antes de la consulta final, mira qué cambia cuando agregas una flecha más al patrón.
'''),
        code("""
if modo_neo4j:
    r0 = driver.execute_query("MATCH (e:Entidad) RETURN e.nombre AS entidad LIMIT 5")
    print("0 relaciones -- solo nodos Entidad:")
    print(pd.DataFrame([r.data() for r in r0.records]))

    r1 = driver.execute_query("MATCH (e:Entidad)-[:PUBLICA]->(p:Proceso) RETURN e.nombre AS entidad, p.id AS proceso LIMIT 5")
    print("\\n1 relacion (PUBLICA) -- que publico cada entidad:")
    print(pd.DataFrame([r.data() for r in r1.records]))
else:
    print("Demostración Cypher pendiente en Aura (respaldo).")
"""),
        code("""
if modo_neo4j:
    r2 = driver.execute_query('''
    MATCH (e:Entidad)-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)
    RETURN e.nombre AS entidad, p.id AS proceso, v.nombre AS proveedor
    LIMIT 5
    ''')
    print("2 relaciones (PUBLICA + ADJUDICADO_A) -- a quien se adjudico:")
    pd.DataFrame([r.data() for r in r2.records])
else:
    print("Demostración Cypher pendiente en Aura (respaldo).")
"""),
        md("""
| Saltos | Qué responde | Ejemplo de pregunta |
|---|---|---|
| 0 | qué entidades existen | ¿qué entidades cargamos? |
| 1 (`PUBLICA`) | qué publicó cada entidad | ¿qué procesos abrió esta entidad? |
| 2 (`PUBLICA`+`ADJUDICADO_A`) | a quién se le adjudicó lo publicado | ¿a qué proveedor llegó este proceso? |

La consulta completa agrega **dos relaciones más**: Proveedor ← Proceso ← Entidad. El camino entre entidades tiene cuatro relaciones. El conteo incluye la entidad ancla; “otras entidades” requiere excluirla explícitamente.

**Cómo se lee.** Cada fila es una coincidencia del patrón de cero, una o dos relaciones.

**Qué nos dice.** Agregar una relación cambia la unidad de la fila.

**Qué NO permite concluir todavía.** `LIMIT 5` no da una muestra representativa ni un orden; faltan criterios de selección.

**Qué error común.** Contar filas como entidades distintas cuando una entidad publica varios procesos.
"""),
        question_cell(1, 'WITH y los cuatro saltos', '¿Por qué conservar v antes del segundo MATCH?', ['Para que el siguiente patrón use el mismo proveedor.', 'Para que WITH guarde una tabla permanente.', 'Para transformar cuatro relaciones en una sola.', 'Para excluir automáticamente la entidad ancla.'], 0, ['v conecta las dos etapas. Primero contamos procesos del ancla y después buscamos las entidades del mismo proveedor.', 'WITH transmite variables y agregados dentro de la consulta; no crea una tabla persistente.', 'El camino sigue siendo Entidad–Proceso–Proveedor–Proceso–Entidad: cuatro relaciones.', 'La exclusión necesita WHERE otra.nit <> $ancla. WITH no la agrega.'], 'La consulta conserva v y count(DISTINCT p) AS procesos_con_entidad mediante WITH.', 10),
        md('''
---
## 7. La consulta que justifica Neo4j

Ahora recorremos el patrón Entidad → Proceso → Proveedor y, desde ese proveedor, contamos entidades conectadas, incluida la entidad ancla. Más adelante escribirás el filtro para contar solo las otras.
'''),
        code("""
query_contexto = '''
MATCH (e:Entidad {nit:$nit})-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)
WITH v, count(DISTINCT p) AS procesos_con_entidad
MATCH (otra:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v)
RETURN v.nit AS nit_proveedor,
       v.nombre AS proveedor,
       procesos_con_entidad,
       count(DISTINCT otra) AS entidades_conectadas
ORDER BY entidades_conectadas DESC, procesos_con_entidad DESC, nit_proveedor ASC
LIMIT 10
'''
if modo_neo4j:
    neo = driver.execute_query(query_contexto, nit=nit_deseado)
    neo_df = pd.DataFrame([r.data() for r in neo.records], columns=["nit_proveedor", "proveedor", "procesos_con_entidad", "entidades_conectadas"])
    resultado_contexto = neo_df.copy()
else:
    neo_df = None
    resultado_contexto = esperado_pd.copy()
    print("Resultado pandas; consulta Neo4j pendiente.")
resultado_contexto
"""),
        code("""
coinciden = None
if modo_neo4j:
    cols_cmp = ["nit_proveedor", "procesos_con_entidad", "entidades_conectadas"]
    pd_cmp = esperado_pd[cols_cmp].copy()
    neo_cmp = neo_df[cols_cmp].copy()
    for tabla in [pd_cmp, neo_cmp]:
        tabla["nit_proveedor"] = tabla["nit_proveedor"].astype(str)
        for columna in cols_cmp[1:]:
            tabla[columna] = tabla[columna].astype("int64")
    coinciden = pd_cmp.reset_index(drop=True).equals(neo_cmp.reset_index(drop=True))
    print("pandas == Neo4j:", coinciden)
    assert coinciden, "Revisa NIT, extracto y datos previos en la instancia; no sigas con una comparación distinta."
else:
    print("pandas == Neo4j: PENDIENTE; solo se ejecutó pandas.")
"""),
        md("""
### Interpretación pandas ↔ Neo4j

**Cómo se lee.** Comparamos NIT y las dos métricas en el mismo orden.

**Qué nos dice.** Si aparece True, el grafo reproduce el patrón calculado previamente. En RESPALDO esa equivalencia queda pendiente.

**Qué NO permite concluir todavía.** Es una prueba de corrección, no un benchmark de velocidad ni evidencia de irregularidad.

**Qué error común.** Confundir “la consulta coincide” con “Neo4j es más rápido”.
"""),
        question_cell(1, 'Corrección y límites', '¿Qué quedó comprobado?', ['Que Neo4j es más rápido.', 'Que las entidades coordinaron adjudicaciones.', 'Que todo SECOP está representado.', 'Que ambas implementaciones producen esa respuesta en el extracto.'], 3, ['La igualdad de resultados no mide latencia. Harían falta tiempos y condiciones comparables.', 'Una estructura compartida no prueba coordinación; faltan hechos sobre decisiones y vínculos.', 'El extracto fue seleccionado por filtros. La comparación no recupera los registros excluidos.', 'Coinciden las claves y métricas del contrato. Eso verifica esa consulta sobre esos datos, no velocidad ni conducta.'], 'El resultado de Aura coincide con pandas en NIT y dos métricas.', 10),
        md("""
---
## Demostración guiada — un vecindario rico del extracto

**Demostración guiada; no es tu evidencia individual.** Antes de trabajar con tu propio resultado, vas a ver dibujado — con nodos y flechas de verdad, en Aura — un vecindario con muchos proveedores compartidos: el de la misma entidad que usa el respaldo pedagógico. Sirve para que veas, una vez, en grande, lo que hasta ahora solo viste en tablas.
"""),
        code("""
nit_ancla_demo = str(manifest["ancla_pedagogica"]["nit_entidad"]).strip()

query_demo_top = '''
MATCH (e:Entidad {nit:$nit})-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)
WITH v, count(DISTINCT p) AS procesos_con_entidad
MATCH (otra:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v)
WITH v, procesos_con_entidad, count(DISTINCT otra) AS entidades_conectadas
WHERE entidades_conectadas > 1
RETURN v.nit AS nit_proveedor, v.nombre AS proveedor, procesos_con_entidad, entidades_conectadas
ORDER BY entidades_conectadas DESC, procesos_con_entidad DESC, nit_proveedor ASC
LIMIT 5
'''
if modo_neo4j:
    demo_df = pd.DataFrame([r.data() for r in driver.execute_query(query_demo_top, nit=nit_ancla_demo).records])
else:
    demo_hist = hist[hist["nit_entidad"].eq(nit_ancla_demo)]
    demo_counts = demo_hist.groupby("nit_proveedor")["id_proceso"].nunique().rename("procesos_con_entidad")
    demo_df = pd.concat([demo_counts, prov_global], axis=1).loc[demo_counts.index].reset_index()
    demo_df["proveedor"] = demo_df["nit_proveedor"].map(nombres_proveedor)
    demo_df = demo_df[demo_df["entidades_conectadas"].gt(1)].sort_values(["entidades_conectadas", "procesos_con_entidad", "nit_proveedor"], ascending=[False, False, True]).head(5)
    print("Demostración tabular pandas; dibujo en Aura pendiente.")
demo_df
"""),
        md("""
**Cómo se lee.** Cada fila es un proveedor de la entidad elegida por cantidad de proveedores compartidos, ordenado por cuántas otras entidades también lo adjudicaron.

**Qué nos dice.** Esta demostración usa deliberadamente una entidad con muchos proveedores compartidos — por eso el grafo que verás enseguida es notorio.

**Qué NO permite concluir todavía.** Esta demostración usa la ancla pedagógica, no la tuya. Tu propio resultado (bloque anterior) puede ser más modesto y sigue siendo una respuesta válida a H2-R.

**Qué error común.** Pensar que tu propia ancla “debería” verse igual de conectada que esta demostración.
"""),
        code("""
top_demo = demo_df.iloc[0]
nit_proveedor_demo = str(top_demo["nit_proveedor"])

query_visual_demo = f'''
MATCH camino_ancla = (e:Entidad {{nit:"{nit_ancla_demo}"}})-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {{nit:"{nit_proveedor_demo}"}})
WITH v, collect(camino_ancla)[0] AS camino_ancla
MATCH camino_otras = (otra:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v)
WHERE otra.nit <> "{nit_ancla_demo}"
WITH camino_ancla, otra, collect(camino_otras)[0] AS camino_otras
RETURN camino_ancla, camino_otras
LIMIT 8
'''
print(query_visual_demo)
"""),
        md(f'''
**HAZ ESTO AHORA.** Si estás en Aura, copia la consulta que acabas de imprimir, ve a tu instancia AuraDB → pestaña **Query** (no Colab), pégala y ejecútala ahí. Aura dibuja nodos y flechas automáticamente cuando devuelves caminos (`RETURN camino`).

En RESPALDO usa el esquema conceptual siguiente y conserva la consulta para ejecutarla después. En Aura deberías ver algo con esta forma:

{svg("04_demo_vecindario", "Representación conceptual: la entidad ancla y otras entidades llegan al mismo proveedor, cada una por su propio proceso")}

**OJO.** El grafo muestra hasta 8 de las entidades conectadas con este proveedor — se acota para que se pueda leer, no porque las demás no existan.

### Antes de seguir, dos preguntas para el salón

1. En el grafo que acabas de ver, ¿cuál es el nodo puente entre las distintas entidades?
2. ¿Qué representa cada camino que dibujó Aura, y qué NO demuestra por sí solo?

**PARA LLEVAR.** Más conexiones no es lo mismo que una conexión anómala. Un proveedor muy conectado puede operar en un mercado amplio (logística, insumos, papelería…). Para saber si una conexión es inusual haría falta un denominador o un patrón esperado con el que compararla — eso todavía no lo tenemos.
'''),
        md("""
---
## 8. CRUD seguro y tu propio vecindario

Ya viste, en la demostración guiada, un grafo con muchas conexiones. Ahora repites el ejercicio con **tu propio resultado** de la sección 7 — puede ser más modesto, y eso también es una respuesta válida a H2-R.

El CRUD usa `S06-DEMO`; no modificamos un proceso real. Después eliges uno de los **5 proveedores con más entidades conectadas** de tu propio resultado (o todos los disponibles, si tu tabla tiene menos de 5) y abres su vecindario.

**Qué debe verse:** una tabla con entidades y procesos relacionados con el proveedor elegido.
**Error probable:** escoger un número fuera de las opciones mostradas. Significa que tu decisión no corresponde al resultado ejecutado.
**Recuperación:** vuelve a ejecutar y elige un número de la lista; no inventes un NIT.
"""),
        code("""
if modo_neo4j:
    driver.execute_query('''
    MERGE (e:Entidad {nit:'S06-E'}) SET e.nombre='Entidad demo'
    MERGE (p:Proceso {id:'S06-DEMO'}) SET p.nombre='Proceso demo'
    MERGE (v:Proveedor {nit:'S06-V'}) SET v.nombre='Proveedor demo'
    MERGE (e)-[:PUBLICA]->(p)
    MERGE (p)-[:ADJUDICADO_A]->(v)
    ''')
    r = driver.execute_query("MATCH (p:Proceso {id:'S06-DEMO'}) SET p.estado_revision='revisado' RETURN p.estado_revision AS estado")
    assert r.records[0]["estado"] == "revisado"
    driver.execute_query("MATCH (n) WHERE n.nit IN ['S06-E','S06-V'] OR n.id='S06-DEMO' DETACH DELETE n")
    print("CRUD demo completado y limpiado.")
else:
    print("Demostración Cypher pendiente en Aura (respaldo).")
"""),
        code("""
if resultado_contexto.empty:
    raise ValueError("No hay proveedores para elegir.")
opciones = resultado_contexto.head(5)
for i, row in opciones.iterrows():
    print(f"{i+1:>2}. {row['proveedor']} | entidades={row['entidades_conectadas']}")
sel = int(input("Número de proveedor: ").strip())
if not 1 <= sel <= len(opciones):
    raise ValueError("Número fuera de rango")
proveedor_elegido = opciones.iloc[sel-1]

if modo_neo4j:
    vec = driver.execute_query('''
    MATCH (e:Entidad)-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {nit:$nit})
    RETURN e.nit AS nit_entidad, e.nombre AS entidad, p.id AS proceso, p.nombre AS nombre_proceso, p.valor AS precio_base
    ORDER BY entidad, valor DESC
    ''', nit=str(proveedor_elegido["nit_proveedor"]))
    vecindario_df = pd.DataFrame([r.data() for r in vec.records])


else:
    vecindario_df = hist[hist["nit_proveedor"].eq(str(proveedor_elegido["nit_proveedor"]))][["nit_entidad", "entidad", "id_proceso", "nombre_proceso", "precio_base"]].drop_duplicates("id_proceso").rename(columns={"id_proceso": "proceso"})
    vecindario_df = vecindario_df.sort_values(["entidad", "precio_base"], ascending=[True, False]).reset_index(drop=True)
    print("Vecindario calculado en pandas; ejecución Neo4j pendiente.")

print("Tamaño observable de tu vecindario:")
print("  Procesos con mi entidad:", int(proveedor_elegido["procesos_con_entidad"]))
print("  Entidades conectadas:", int(proveedor_elegido["entidades_conectadas"]))
print("  Procesos visibles en el vecindario:", len(vecindario_df))
vecindario_df
"""),
        md("""
### Interpretación de tu vecindario

**Cómo se lee.** Cada fila es un proceso conectado al proveedor que elegiste; una misma entidad puede aportar varios procesos. Esta exploración corresponde al proveedor elegido. H2-R se sostiene con el proveedor del máximo, que puede ser otro; la ficha conserva ambos.

**Qué nos dice.** Puedes observar qué entidades y procesos del extracto comparten ese actor contractual y abrir casos concretos para revisión.

**Qué NO permite concluir todavía.** Compartir proveedor no demuestra coordinación, favorecimiento ni irregularidad. Faltan, como mínimo, cronología comparable, condiciones de competencia y vínculos de propiedad/representación cuando la hipótesis los requiera.

**Qué error común.** Convertir el número de conexiones en un “score de riesgo” sin modelo ni denominador.

`precio_base` es el presupuesto base reportado, no el valor adjudicado. Un proceso puede tener varios registros de adjudicación: no sumes ese presupuesto repetidamente como gasto.
"""),
        md("""
### EJERCICIO S06-EXCLUIR — modifica una condición
La columna `entidades_conectadas` incluye tu entidad. Laura quiere saber cuántas **otras** entidades están conectadas al proveedor explorado. Antes de ejecutar, calcula mentalmente: total menos una. Completa el único hueco con el operador Cypher “distinto de”.

**Qué debe verse:** “Otras entidades: N | esperado: N”; N puede ser cero.
**Error probable:** usar igualdad; contarías solo tu entidad. **Recuperación:** consulta el apoyo plegado y repite.

<details><summary>Apoyo si te atascaste</summary>El operador es <code>&lt;&gt;</code>. Si el total es 19, deben quedar 18. El conteo cero también es una respuesta válida.</details>
"""),
        code("""
OPERADOR_EXCLUSION = "____"  # sustituye por el operador distinto de de Cypher
if OPERADOR_EXCLUSION != "<>":
    raise ValueError("Necesitamos excluir la entidad ancla, no seleccionarla.")
consulta_otras = f'''
MATCH (otra:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {{nit:$proveedor}})
WHERE otra.nit {OPERADOR_EXCLUSION} $ancla
RETURN count(DISTINCT otra) AS otras_entidades
'''
if modo_neo4j:
    otras_entidades = int(driver.execute_query(consulta_otras, proveedor=str(proveedor_elegido["nit_proveedor"]), ancla=nit_deseado).records[0]["otras_entidades"])
else:
    otras_entidades = int(vecindario_df.loc[vecindario_df["nit_entidad"].ne(nit_deseado), "nit_entidad"].nunique())
esperadas_otras = int(proveedor_elegido["entidades_conectadas"]) - 1
assert otras_entidades == esperadas_otras
print("Otras entidades:", otras_entidades, "| esperado:", esperadas_otras)
razon_exploracion = input("Con tus números: ¿por qué explorar este proveedor y cuál de la lista descartaste?: ").strip()
if len(razon_exploracion) < 25:
    raise ValueError("Nombra tu elección, otra opción y un dato de tu salida.")
"""),
        md("""
**Cómo se lee.** El total inicial incluía el NIT de la entidad ancla; la nueva consulta lo excluye.

**Qué nos dice.** La resta de una coincide con el filtro por identidad, incluso si el resultado es cero.

**Qué NO permite concluir todavía.** “Otras entidades” no significa competidores; falta conocer mercados y modalidades comparables.

**Qué error común.** Restar un proceso en vez de una entidad distinta.
"""),
        question_cell(1, 'El proveedor explorado y H2-R', '¿Qué debe registrar tu ficha?', ['Que H2-R usa 19 y que hay 19 otras entidades.', 'Que el proveedor explorado prueba H2-R porque 19 > 21.', 'Máximo 39 para H2-R; 19 conexiones y 18 otras entidades para la exploración.', 'Solo el proveedor que se vea mejor en el dibujo.'], 2, ['El máximo de la entidad no cambia al explorar otro proveedor. Además otras entidades excluye el ancla.', '19 no supera 21 y ese proveedor no determina el máximo. Hay dos preguntas y dos resultados.', 'Separamos la comparación de la entidad de la decisión de exploración. La ficha conserva ambos NIT y sus métricas.', 'El tamaño del dibujo depende del límite visual. La evidencia son las consultas y sus números.'], 'H2-R usa el máximo 39 y la mediana 21. Elegiste explorar otro proveedor con 19 entidades, incluida la ancla.', 10),
        md("""
### EJERCICIO S06-CONSULTA — escribe una consulta breve
Construye una consulta que cuente los **procesos distintos de la entidad ancla adjudicados al proveedor elegido**. Usa `$ancla`, `$proveedor` y devuelve una columna `procesos`.

Escribe tu código en la celda siguiente. Puedes apoyarte en el patrón de dos relaciones ya resuelto. **Qué debe verse:** “Consulta propia: N | esperado: N”. **Error probable:** contar filas sin DISTINCT o contar todas las entidades. La comprobación compara con tu propia tabla.

<details><summary>Consulta de recuperación</summary>

```cypher
MATCH (e:Entidad {nit:$ancla})-[:PUBLICA]->(p:Proceso)-[:ADJUDICADO_A]->(v:Proveedor {nit:$proveedor})
RETURN count(DISTINCT p) AS procesos
```

En RESPALDO guarda tu consulta para ejecutarla en Aura; el número se comprueba con pandas y se declara pendiente la sintaxis Cypher.
</details>
"""),
        code("""
# Escribe tu consulta entre las comillas triples; utiliza los dos parámetros indicados.
consulta_propia = '''
'''
if not consulta_propia.strip():
    raise ValueError("Escribe tu consulta; tienes un apoyo plegado encima.")
if modo_neo4j:
    procesos_propios = int(driver.execute_query(consulta_propia, ancla=nit_deseado, proveedor=str(proveedor_elegido["nit_proveedor"])).records[0]["procesos"])
else:
    procesos_propios = int(vecindario_df.loc[vecindario_df["nit_entidad"].eq(nit_deseado), "proceso"].nunique())
    print("Consulta Cypher propia guardada pero pendiente de ejecución en Aura.")
esperados_propios = int(proveedor_elegido["procesos_con_entidad"])
assert procesos_propios == esperados_propios, "Revisa DISTINCT y los dos parámetros."
print("Consulta propia:", procesos_propios, "| esperado:", esperados_propios)
"""),
        md("""
**Cómo se lee.** N es el número de procesos distintos para ese par entidad–proveedor.

**Qué nos dice.** Tu consulta reproduce una métrica del contrato con una selección concreta.

**Qué NO permite concluir todavía.** Ese conteo no mide gasto: falta una medida de adjudicación sin duplicaciones.

**Qué error común.** Confundir consultas que producen el mismo número por casualidad; revisa también el patrón y los parámetros.
"""),
        md('''
### La evidencia no termina en el grafo

Ahora registra dos decisiones que una respuesta genérica no puede inventar por ti:

1. un límite que nombre **qué dato faltaría** antes de una afirmación de riesgo/irregularidad;
2. una alternativa de modelado que descartaste y por qué.
'''),
        question_cell(1, 'Exportación para S7', '¿Qué hace la exportación auditable y útil para búsqueda textual?', ['Guardar solo una imagen del grafo.', 'Guardar IDs, descripciones, URL, selección y motor real de ejecución.', 'Guardar la contraseña de Aura junto al resultado.', 'Guardar todo el dataset sin declarar el filtro.'], 1, ['La imagen ayuda a leer caminos, pero no conserva el texto e IDs que necesita S7.', 'El texto habilita la búsqueda, los IDs permiten rastrear procesos y la selección y el motor delimitan lo que efectivamente se hizo.', 'Las credenciales no son evidencia. La ficha debe declarar resultados y estado del motor, nunca contraseñas.', 'Sin el criterio de selección no sabemos qué casos representa el archivo ni cómo interpretar los ausentes.'], 'Vas a conservar procesos del proveedor explorado y sus descripciones.', 10),
        code("""
if modo_neo4j:
    proveedor_h2r_neo = neo_df.iloc[0]
    assert str(proveedor_h2r_neo["nit_proveedor"]) == str(proveedor_h2r["nit_proveedor"])
    assert int(proveedor_h2r_neo["entidades_conectadas"]) == maximo_h2r
    if uso_respaldo_s06:
        desenlace_h2r_neo = "no evaluable con mi ancla"
    elif int(proveedor_h2r_neo["entidades_conectadas"]) > MEDIANA_H2R:
        desenlace_h2r_neo = "conexión más fuerte que la mediana de las candidatas de S5"
    else:
        desenlace_h2r_neo = "conexión igual o menor que la mediana de las candidatas de S5"
    assert desenlace_h2r_neo == desenlace_h2r_pd
else:
    desenlace_h2r_neo = "PENDIENTE: no se ejecutó Neo4j"
print("Desenlace H2-R (Neo4j):", desenlace_h2r_neo)
print("Proveedor H2-R:", proveedor_h2r["nit_proveedor"], "| máximo:", maximo_h2r, "| mediana:", MEDIANA_H2R)
print("Proveedor explorado:", proveedor_elegido["nit_proveedor"], "| conexiones:", int(proveedor_elegido["entidades_conectadas"]))
"""),
        code("""
from pathlib import Path
from datetime import datetime, timezone
autor = input("Autor o alias de equipo (guardar solo en repositorio privado): ").strip()
decision_modelo = input("Justifica por qué Proceso debe ser nodo para tu pregunta: ").strip()
if not autor or len(decision_modelo) < 20:
    raise ValueError("Registra autor y justificación de modelado.")
fecha_ejecucion = datetime.now(timezone.utc).isoformat()
limite_estudiante = input("Límite concreto y dato faltante: ").strip()
alternativa_modelo = input("Alternativa de modelado descartada: ").strip()
razon_alternativa = input("¿Por qué la descartaste para esta pregunta?: ").strip()

if len(limite_estudiante) < 25:
    raise ValueError("Nombra la conclusión que no puedes sostener y el dato que falta.")
if len(alternativa_modelo) < 5 or len(razon_alternativa) < 15:
    raise ValueError("Nombra una alternativa real y explica por qué no sirve igual de bien para esta pregunta.")

"""),
        hidden(code("""
export = vecindario_df.merge(
    datos[["id_proceso", "descripcion", "modalidad", "url_secop"]].drop_duplicates("id_proceso"),
    left_on="proceso", right_on="id_proceso", how="left", validate="many_to_one"
)
assert export["id_proceso"].notna().all(), "Hay procesos sin correspondencia en el extracto."
export["nit_proveedor_explorado"] = str(proveedor_elegido["nit_proveedor"])
export["motor_ejecucion"] = "Neo4j" if modo_neo4j else "pandas; Neo4j pendiente"
export.to_json("s06_contexto_procesos.jsonl", orient="records", lines=True, force_ascii=False)

hito = f'''# Hito S06 — Ficha relacional de revisión

- Autor: {autor}
- Fecha UTC: {fecha_ejecucion}
- SHA256 del extracto: {huella_datos}
- Carga repetida: {carga_repetida if carga_repetida is not None else "PENDIENTE"}\n- Consulta propia: {procesos_propios} procesos; motor {"Neo4j" if modo_neo4j else "pandas; Cypher pendiente"}\n- Motor: {"Neo4j" if modo_neo4j else "pandas; Neo4j pendiente"}
- Origen del ancla: {origen_ancla}
- Proceso elegido en S5: {ancla_original.get("id_proceso", "")}
- Proceso/entidad usados para el grafo: {ancla_trabajo.get("id_proceso", "")} — {ancla_trabajo.get("entidad", "")}
- Noticias / nivel: {ancla_trabajo.get("noticias_entidad", "")} / {ancla_trabajo.get("nivel_menciones", "")}
- Respaldo pedagógico: {uso_respaldo_s06}
- H1 (S5): 0/77 → refutada literalmente
- H2-R (S6), desenlace pandas: {desenlace_h2r_pd}
- H2-R (S6), desenlace Neo4j: {desenlace_h2r_neo}
- pandas == Neo4j: {coinciden if coinciden is not None else "PENDIENTE"}
- Proveedor que determina H2-R: {proveedor_h2r["nit_proveedor"]} — {proveedor_h2r["proveedor"]}
- Máximo H2-R: {maximo_h2r}
- Mediana H2-R: {MEDIANA_H2R}
- NIT proveedor explorado: {proveedor_elegido["nit_proveedor"]}
- Otras entidades del proveedor explorado: {otras_entidades}
- Decisión de exploración: {razon_exploracion}
- Proveedor elegido: {proveedor_elegido["proveedor"]}
- Entidades conectadas: {int(proveedor_elegido["entidades_conectadas"])}
- Procesos en el vecindario: {len(vecindario_df)}

## Límite
{limite_estudiante}

## Decisión de modelado
{decision_modelo}

### Alternativa descartada
{alternativa_modelo}

Razón: {razon_alternativa}

## Consulta propia (Cypher)
```cypher
{consulta_propia.strip()}
```
'''
Path("hito_s06_ficha_relacional.md").write_text(hito, encoding="utf-8")
print(hito)

try:
    from google.colab import files
    files.download("hito_s06_ficha_relacional.md")
    files.download("s06_contexto_procesos.jsonl")
except ImportError:
    print("Archivos generados en el runtime.")
print("Exportación S7:", len(export), "procesos; ficha y JSONL guardados.")
"""), "Guardar ficha y archivo para S7"),
        md("""
### Comprueba tu entrega
La ficha debe mostrar **dos NIT diferenciados** cuando corresponda: proveedor que determina H2-R y proveedor explorado. Verifica máximo, mediana, filtro de otras entidades, decisión propia y estado real del motor. Añade el enlace al commit privado en la entrega del aula.

**Cómo se lee.** El JSONL tiene una fila por proceso del vecindario, con descripción y URL.

**Qué nos dice.** S7 puede buscar texto dentro de la selección que acabas de justificar.

**Qué NO permite concluir todavía.** No es todo SECOP; faltan los procesos excluidos por el recorte y sus fechas comparables.

**Qué error común.** Llamar gasto a `precio_base` o presentar RESPALDO como ejecución en Aura.
"""),
        md(f'''
---
## Hoja de trucos y puente

```text
UNWIND → convierte una lista en filas
MERGE  → encuentra o crea
MATCH  → busca patrón
WHERE  → filtra
WITH   → encadena
SET    → modifica una propiedad
RETURN → salida
DETACH DELETE → elimina nodo y relaciones
```

{svg("03_modelo_minimo", "Entidad publica un Proceso, que es adjudicado a un Proveedor")}

**Idea central.** Cassandra organizó datos para una pregunta repetitiva conocida. Neo4j hace de las relaciones una parte explícita de la pregunta.

### Recapitulación
Partimos de un proceso, recuperamos adjudicaciones de su entidad, explicitamos caminos, contrastamos un máximo y elegimos un vecindario. La ficha conserva qué se ejecutó, qué decidimos y qué falta.

**Errores para evitar:** NIT ausente no es proveedor; nombre no es identidad; máximo H2-R no es cualquier proveedor; presupuesto no es gasto; conectividad no es irregularidad.

### Referencias y recursos
- [Fuente y criterios del extracto](https://github.com/jazaineam1/BigData2026/blob/main/utils/build_session6_graph_data.py).
- [MERGE](https://neo4j.com/docs/cypher-manual/current/clauses/merge/) y [UNWIND](https://neo4j.com/docs/cypher-manual/current/clauses/unwind/).
- [Cypher MATCH](https://neo4j.com/docs/cypher-manual/current/clauses/match/) y [WITH](https://neo4j.com/docs/cypher-manual/current/clauses/with/).
- [Driver Python](https://neo4j.com/docs/python-manual/current/) y [Aura](https://neo4j.com/docs/aura/).
- [Tutorial Aura](https://jazaineam1.github.io/BigData2026/assets/tutoriales/neo4j-aura-s06-paso-a-paso.html) y [checklist](https://jazaineam1.github.io/BigData2026/assets/tutoriales/s06-laboratorio-guiado.html).

### Lo que sigue

Laura ya puede ver el vecindario, pero ahora tiene muchos nombres y descripciones de procesos. La nueva pregunta será:

> **¿Cuáles de esos procesos son más relevantes para una búsqueda textual concreta?**

`s06_contexto_procesos.jsonl` será la entrada de Elasticsearch/BM25.
'''),
        code("""
if driver is not None:
    driver.close()
    print("Conexión Neo4j cerrada.")
else:
    print("Sin conexión Neo4j abierta (respaldo).")
"""),
    ]


    # Numeración calculada: una sola pregunta por celda, payload oculto al vistazo.
    preguntas = [c for c in cells if c["cell_type"] == "code" and "pregunta_codificada(\"" in "".join(c["source"]) and "def pregunta_codificada" not in "".join(c["source"])]
    for numero, celda in enumerate(preguntas, 1):
        texto = "".join(celda["source"])
        token = texto.split('pregunta_codificada("', 1)[1].split('"', 1)[0]
        payload = json.loads(base64.b64decode(token))
        payload.update(numero=numero, total=len(preguntas))
        celda.update(question_cell(numero, payload["tema"], payload["pregunta"], payload["opciones"], payload["correcta"], payload["retro"], payload["contexto"], len(preguntas)))
    for numero, celda in enumerate(cells, 1):
        celda["id"] = f"s06-{numero:03d}"
    return cells


def build_checklist(cells):
    """Deriva las referencias del cuaderno; conserva el motor visual del HTML."""
    import re

    def celda(inicio):
        coincidencias = [i for i, c in enumerate(cells, 1) if "".join(c["source"]).startswith(inicio)]
        if len(coincidencias) != 1:
            raise ValueError(f"Referencia de checklist ambigua: {inicio!r}")
        return f"celda {coincidencias[0]}"

    pasos = [
        ("abrir", "entiende", "Abre el caso y lee la rúbrica", "# Sesión 6", "Identifica el producto, la pregunta profesional y los criterios antes del laboratorio.", "Lee el mapa, la procedencia y la rúbrica S06; responde las autoevaluaciones a medida que aparecen.", "La ficha pide proceso, dos proveedores si difieren, máximo, mediana, límite, decisión y traza."),
        ("cargar", "ejecuta", "Carga el extracto y elige el ancla", "#@title Cargar o recuperar", "Conservas la selección S5 sin fabricar un proveedor para el candidato.", "Ejecuta carga y selección de ancla. Si falla la red, sube CSV y manifest; si falta S5, elige Enter explícitamente.", "Filas disponibles: 2109; huella SHA256; Origen: archivo propio S5 o ancla pedagógica versionada."),
        ("historial", "entiende", "Lee el historial y la identidad", "nit_deseado =", "NIT es la clave; el nombre puede tener variantes.", "Observa fechas, entidad de trabajo, procesos históricos y proveedores distintos; responde las preguntas de evidencia e identidad.", "NIT de proveedor con varios nombres: 2; Entidad de trabajo; Procesos históricos; Proveedores distintos."),
        ("patron", "decide", "Completa el patrón contractual", "RELACION_PROCESO_PROVEEDOR =", "El verbo de la relación debe representar un hecho observado.", "Completa el hueco del patrón; usa el apoyo plegado si te atascas.", "Patrón correcto: la relación expresa una adjudicación observada."),
        ("contrato", "ejecuta", "Calcula el contrato pandas y H2-R", "# Ambas métricas", "Fijas una respuesta comparable antes de usar Neo4j.", "Ejecuta y explica máximo y mediana; identifica al proveedor que determina H2-R. Responde la pregunta de mediana.", "Entidades de referencia: 28; Mediana de referencia (candidatas S5): 21.0; Proveedor que determina H2-R; tabla de hasta 10 proveedores."),
        ("aura", "externo", "Conecta Aura o declara el respaldo", "#@title Conectar Aura o activar respaldo", "Distingues ejecución del motor real de continuidad con pandas.", "Si Colab reinició, ejecuta RECUPERACIÓN S06. Sigue el <a href='neo4j-aura-s06-paso-a-paso.html' target='_blank' rel='noopener'>tutorial Aura</a>; elige RESPALDO si no puedes conectar.", "Conexión Neo4j verificada. O RESPALDO pandas: Neo4j y CRUD pendientes; no se declarará equivalencia comprobada."),
        ("carga", "ejecuta", "Crea restricciones y carga adjudicaciones válidas", "cols =", "Los 77 candidatos sin proveedor no deben producir adjudicaciones inventadas.", "Ejecuta restricciones y carga. Responde la pregunta UNWIND.", "Carga preparada: 2109 filas; 2032 adjudicaciones válidas. En Aura, también Carga lista; en respaldo, carga pendiente."),
        ("repetir", "ejecuta", "Repite la carga y compara conteos", "if modo_neo4j:\n    consulta_tamano", "Un reinicio no debe multiplicar nodos y relaciones.", "Ejecuta la comprobación de repetición sin borrar los datos de tu instancia.", "Carga repetida sin crecimiento: True y los conteos; o Idempotencia en Neo4j: PENDIENTE."),
        ("comparar", "ejecuta", "Recorre caminos y verifica el contrato", "coinciden = None", "Una tabla coincidente prueba la respuesta de esta consulta, no velocidad ni irregularidad.", "Ejecuta patrones de 0, 1 y 2 relaciones, consulta completa y comparación. Responde WITH y límites.", "pandas == Neo4j: True. En respaldo: PENDIENTE; solo se ejecutó pandas."),
        ("visual", "externo", "Dibuja el ejemplo guiado", "top_demo =", "Un camino muestra cómo se conectan los actores.", "En Aura copia la consulta impresa en Query. En respaldo usa el SVG conceptual y conserva Cypher para después.", "Consulta con camino_ancla y camino_otras; en Aura, dibujo de hasta 8 entidades adicionales."),
        ("vecindario", "decide", "Ejecuta CRUD demo y elige proveedor", "if resultado_contexto.empty:", "Tu exploración puede elegir un proveedor diferente del que determina H2-R.", "Ejecuta CRUD demo cuando uses Aura y elige un número válido del listado de proveedores.", "Tamaño observable de tu vecindario: procesos con mi entidad, entidades conectadas y procesos visibles; tabla del proveedor elegido."),
        ("excluir", "decide", "Cuenta otras entidades", "OPERADOR_EXCLUSION =", "El conteo inicial incluye la entidad ancla.", "Completa el operador de exclusión y justifica la exploración con números y una alternativa descartada. Responde la pregunta de los dos proveedores.", "Otras entidades: N | esperado: N; debe ser una menos que entidades_conectadas."),
        ("propia", "decide", "Construye tu consulta", "# Escribe tu consulta entre", "Defiendes el patrón con una consulta que escribiste.", "Escribe el conteo de procesos distintos para el par entidad–proveedor. Consulta el apoyo plegado si lo necesitas.", "Consulta propia: N | esperado: N. En respaldo se declara que Cypher está pendiente de ejecución."),
        ("hito", "decide", "Genera ficha y JSONL", "from pathlib import Path\nfrom datetime", "La siguiente sesión necesita texto rastreable y una selección justificada.", "Ejecuta el desenlace H2-R y completa autor/alias, modelado, límite y alternativa. Guarda en el repositorio privado y entrega el enlace al commit.", "Exportación S7: N procesos; ficha y JSONL guardados. Incluye motor real, proveedor H2-R, máximo, mediana y proveedor explorado."),
        ("cerrar", "ejecuta", "Cierra y revisa el puente a S7", "if driver is not None:", "Conservas resultados y reconoces qué queda pendiente.", "Revisa la hoja de trucos y el cierre; ejecuta el cierre de conexión.", "Conexión Neo4j cerrada. O Sin conexión Neo4j abierta (respaldo)."),
    ]
    datos = [{"titulo": "Del ancla al producto verificable", "pasos": [
        dict(id=ident, tipo=tipo, titulo=titulo, celda=celda(inicio), explicacion=por_que, instruccion=accion, evidencia=evidencia)
        for ident, tipo, titulo, inicio, por_que, accion, evidencia in pasos
    ]}]
    ruta = ROOT / "assets/tutoriales/s06-laboratorio-guiado.html"
    html = ruta.read_text(encoding="utf-8")
    patron = r"const DATA = \[.*?(?=const ICONS)"
    nuevo = "const DATA = " + json.dumps(datos, ensure_ascii=False, indent=2) + ";\nconst DATA2 = [];\n\n"
    html, cantidad = re.subn(patron, lambda _: nuevo, html, flags=re.S)
    if cantidad != 1:
        raise ValueError("No se encontró el bloque de pasos del checklist")
    html = html.replace('"s06lab:" + id', '"s06lab:nit-v2:" + id')
    html = html.replace("Generado a mano como guía de acompañamiento del laboratorio S06.", "Guía de acompañamiento del laboratorio S06.")
    ruta.write_text(html, encoding="utf-8")


def main():
    cells = build_cells()
    validate(cells)
    save(cells, OUTPUT)
    build_checklist(cells)
    print(f"[OK] S6 generada: {len(cells)} celdas")


if __name__ == "__main__":
    main()
