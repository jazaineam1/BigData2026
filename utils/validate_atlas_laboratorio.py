# -*- coding: utf-8 -*-
"""Valida la presentación Compass -> Atlas -> pandas -> bandeja de Laura.

No necesita una cuenta Atlas ni una API viva. Recalcula los resultados de
control con los archivos versionados y comprueba que la presentación enlaza los
artefactos reproducibles. Las capturas pueden permanecer pendientes durante la
construcción; use ``--require-captures`` antes de publicar la versión final.

Uso
---
    py -3 utils/validate_atlas_laboratorio.py
    py -3 utils/validate_atlas_laboratorio.py --require-captures
"""

from __future__ import annotations

import argparse
import csv
import html as html_lib
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML_PREDETERMINADO = ROOT / "assets" / "tutoriales" / "atlas-laboratorio-consultas.html"
CONSULTAS = ROOT / "assets" / "tutoriales" / "consultas" / "atlas"
CAPTURAS = ROOT / "assets" / "tutoriales" / "capturas"
NOTICIAS = ROOT / "Datos" / "noticias_contratacion_2026.json"
ENTIDADES = ROOT / "Datos" / "entidades_en_noticias_2026.json"
SECOP = ROOT / "Cuadernos" / "datos" / "secop_chunks" / "prueba_chunk_0000000.csv"

ARTEFACTOS = {
    "dian-palabra-completa-v1.json",
    "resumen-secciones-v1.json",
    "clasificar-noticias-v1.json",
    "menciones-clasificadas-v1.json",
    "resumen-mensual-ampliacion-v1.json",
}

CAPTURAS_ESPERADAS = [
    "10-compass-conexion-atlas.png",
    "11-compass-crear-base-noticias.png",
    "12-compass-importar-noticias.png",
    "13-compass-importar-entidades.png",
    "14-atlas-data-explorer-colecciones.png",
    "15-atlas-editar-revision.png",
    "16-atlas-filtros-regex.png",
    "17-atlas-guardar-consulta.png",
    "18-atlas-pipeline-resumen.png",
    "19-atlas-vista-noticias.png",
    "20-atlas-vista-menciones.png",
    "21-colab-cruce-secop.png",
    "22-colab-bandeja-laura.png",
]


def cargar_json(ruta, errores):
    try:
        with ruta.open(encoding="utf-8") as archivo:
            return json.load(archivo)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errores.append(f"JSON inválido o ilegible: {ruta.relative_to(ROOT)} ({exc})")
        return None


def numero(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def dimensiones_png(ruta):
    """Lee firma e IHDR sin depender de Pillow."""
    with ruta.open("rb") as archivo:
        cabecera = archivo.read(24)
    if len(cabecera) < 24 or cabecera[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("firma PNG inválida")
    if cabecera[12:16] != b"IHDR":
        raise ValueError("no contiene IHDR en la posición esperada")
    return struct.unpack(">II", cabecera[16:24])


def validar_artefactos(errores):
    cargados = {}
    for nombre in sorted(ARTEFACTOS):
        ruta = CONSULTAS / nombre
        if not ruta.exists():
            errores.append(f"falta el artefacto {ruta.relative_to(ROOT)}")
            continue
        cargados[nombre] = cargar_json(ruta, errores)

    consulta = cargados.get("dian-palabra-completa-v1.json")
    if consulta is not None:
        esperado = {"titulo": {"$regex": r"\bdian\b", "$options": "i"}}
        if consulta.get("filter") != esperado:
            errores.append("dian-palabra-completa-v1.json no conserva el filtro de palabra completa")
        if consulta.get("nombre") != "dian-palabra-completa-v1":
            errores.append("la consulta DIAN no conserva su nombre versionado")
        if consulta.get("coleccion") != "noticias":
            errores.append("la consulta DIAN no apunta a la colección noticias")

    resumen = cargados.get("resumen-secciones-v1.json")
    if resumen is not None:
        if not isinstance(resumen, list) or [next(iter(x), "") for x in resumen] != [
            "$match", "$group", "$sort", "$limit"
        ]:
            errores.append("resumen-secciones-v1.json debe contener match -> group -> sort -> limit")

    clasificar = cargados.get("clasificar-noticias-v1.json")
    if clasificar is not None:
        try:
            ramas = clasificar[1]["$set"]["clasificacion"]["$switch"]["branches"]
            patrones = [rama["case"]["$regexMatch"]["regex"] for rama in ramas]
            etiquetas = [rama["then"] for rama in ramas]
        except (IndexError, KeyError, TypeError):
            errores.append("clasificar-noticias-v1.json no tiene la estructura $switch esperada")
        else:
            if patrones != [
                r"sobrecost|detriment|peculad|corrupci(?:o|ó)n|irregular",
                r"contrat|licitaci(?:o|ó)n|adjudic|secop|convenio",
                r"obra|retras|incumpl|ejecuci(?:o|ó)n",
            ]:
                errores.append("cambiaron los patrones o el orden de clasificar-noticias-v1.json")
            if etiquetas != ["terminos_control", "proceso_contractual", "ejecucion_obra"]:
                errores.append("cambiaron las categorías o el orden de clasificar-noticias-v1.json")

    menciones = cargados.get("menciones-clasificadas-v1.json")
    if menciones is not None:
        try:
            switch = menciones[0]["$set"]["nivel_menciones"]["$switch"]
            umbrales = [rama["case"]["$gte"][1] for rama in switch["branches"]]
            niveles = [rama["then"] for rama in switch["branches"]]
        except (IndexError, KeyError, TypeError):
            errores.append("menciones-clasificadas-v1.json no tiene la estructura $switch esperada")
        else:
            if umbrales != [20, 5] or niveles != ["alta", "media"] or switch.get("default") != "baja":
                errores.append("menciones-clasificadas-v1.json cambió los cortes 20/5 o sus niveles")

    mensual = cargados.get("resumen-mensual-ampliacion-v1.json")
    if mensual is not None:
        try:
            expresion = mensual[0]["$group"]["_id"]["$substr"]
        except (IndexError, KeyError, TypeError):
            errores.append("resumen-mensual-ampliacion-v1.json no agrupa con $substr")
        else:
            if expresion != ["$publicado", 0, 7]:
                errores.append("el resumen mensual no extrae YYYY-MM desde publicado")


def validar_baselines(errores, informe):
    noticias = cargar_json(NOTICIAS, errores)
    entidades = cargar_json(ENTIDADES, errores)
    if noticias is None or entidades is None:
        return

    informe["noticias"] = len(noticias)
    if len(noticias) != 987:
        errores.append(f"baseline noticias: esperado 987, obtenido {len(noticias)}")

    largas = sum((numero(n.get("n_palabras")) or 0) > 800 for n in noticias)
    informe["n_palabras_gt_800"] = largas
    if largas != 189:
        errores.append(f"baseline n_palabras > 800: esperado 189, obtenido {largas}")

    titulos = [str(n.get("titulo") or "") for n in noticias]
    dian_subcadena = sum(bool(re.search("dian", titulo, re.I)) for titulo in titulos)
    dian_palabra = sum(bool(re.search(r"\bdian\b", titulo, re.I)) for titulo in titulos)
    informe["dian_subcadena"] = dian_subcadena
    informe["dian_palabra_completa"] = dian_palabra
    if (dian_subcadena, dian_palabra) != (8, 1):
        errores.append(
            f"baseline DIAN: esperado 8 -> 1, obtenido {dian_subcadena} -> {dian_palabra}"
        )

    por_seccion = defaultdict(list)
    for noticia in noticias:
        palabras = numero(noticia.get("n_palabras"))
        if palabras is not None and palabras > 0:
            por_seccion[str(noticia.get("seccion"))].append(palabras)
    investigacion = por_seccion.get("justicia/investigacion", [])
    promedio_investigacion = sum(investigacion) / len(investigacion) if investigacion else 0
    informe["justicia_investigacion"] = [len(investigacion), round(promedio_investigacion, 1)]
    if len(investigacion) != 238 or abs(promedio_investigacion - 560.5) > 0.06:
        errores.append(
            "baseline justicia/investigacion: esperado 238 y 560,5; "
            f"obtenido {len(investigacion)} y {promedio_investigacion:.1f}"
        )

    reglas = [
        ("terminos_control", re.compile(r"sobrecost|detriment|peculad|corrupci(?:o|ó)n|irregular", re.I)),
        ("proceso_contractual", re.compile(r"contrat|licitaci(?:o|ó)n|adjudic|secop|convenio", re.I)),
        ("ejecucion_obra", re.compile(r"obra|retras|incumpl|ejecuci(?:o|ó)n", re.I)),
    ]
    clases = Counter()
    for noticia in noticias:
        texto = f'{noticia.get("titulo") or ""} {noticia.get("subtitulo") or ""}'
        etiqueta = "contexto"
        for nombre, patron in reglas:
            if patron.search(texto):
                etiqueta = nombre
                break
        clases[etiqueta] += 1
    esperado_clases = {
        "terminos_control": 313,
        "proceso_contractual": 349,
        "ejecucion_obra": 26,
        "contexto": 299,
    }
    informe["clasificacion_noticias"] = dict(clases)
    if dict(clases) != esperado_clases:
        errores.append(f"baseline clasificación noticias cambió: {dict(clases)}")

    niveles = Counter(
        "alta" if fila["noticias"] >= 20 else "media" if fila["noticias"] >= 5 else "baja"
        for fila in entidades
    )
    esperado_niveles = {"alta": 6, "media": 25, "baja": 111}
    informe["niveles_menciones"] = dict(niveles)
    if dict(niveles) != esperado_niveles:
        errores.append(f"baseline niveles de menciones cambió: {dict(niveles)}")

    entidades_por_nombre = {fila["entidad"]: fila for fila in entidades}
    enlazados = 0
    bandeja = 0
    with SECOP.open(encoding="utf-8-sig", newline="") as archivo:
        filas = list(csv.DictReader(archivo))
    for fila in filas:
        if fila.get("entidad") not in entidades_por_nombre:
            continue
        enlazados += 1
        directa = "directa" in str(fila.get("modalidad_de_contratacion") or "").lower()
        respuestas = numero(fila.get("respuestas_al_procedimiento"))
        if directa and respuestas == 0:
            bandeja += 1
    informe["procesos_secop"] = len(filas)
    informe["cruce_entidad"] = enlazados
    informe["bandeja_laura"] = bandeja
    if len(filas) != 1000:
        errores.append(f"baseline muestra SECOP: esperado 1000, obtenido {len(filas)}")
    if enlazados != 163:
        errores.append(f"baseline cruce entidad: esperado 163, obtenido {enlazados}")
    if bandeja != 77:
        errores.append(f"baseline bandeja Laura: esperado 77, obtenido {bandeja}")

    mensual = Counter(str(n.get("publicado") or "")[:7] for n in noticias)
    esperado_mensual = {
        "2026-01": 141,
        "2026-02": 129,
        "2026-03": 120,
        "2026-04": 140,
        "2026-05": 110,
        "2026-06": 92,
        "2026-07": 175,
        "2026-08": 80,
    }
    informe["resumen_mensual"] = dict(sorted(mensual.items()))
    if dict(sorted(mensual.items())) != esperado_mensual:
        errores.append(f"baseline mensual cambió: {dict(sorted(mensual.items()))}")


def validar_html(ruta, require_captures, errores, avisos):
    if not ruta.exists():
        errores.append(f"falta la presentación {ruta.relative_to(ROOT)}")
        return
    try:
        texto = ruta.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errores.append(f"no se pudo leer la presentación como UTF-8: {exc}")
        return

    texto_min = texto.lower()
    if "\ufffd" in texto:
        errores.append("la presentación contiene el carácter de reemplazo Unicode U+FFFD")

    requeridos = [
        "MongoDB Compass",
        "Add New Connection",
        "Create Database",
        "Add Data",
        "Import JSON or CSV file",
        "Stop on errors",
        "View Log",
        "noticias_contratacion_2026.json",
        "entidades_en_noticias_2026.json",
        "dian-palabra-completa-v1",
        "resumen-secciones-v1",
        "noticias_clasificadas",
        "menciones_clasificadas",
        "nivel_menciones",
        "client.close",
        "0.0.0.0/0",
        "laura",
        "pandas",
    ]
    for termino in requeridos:
        if termino.lower() not in texto_min:
            errores.append(f"la presentación no contiene el elemento requerido {termino!r}")

    for nombre in sorted(ARTEFACTOS):
        if nombre not in texto:
            errores.append(f"la presentación no enlaza o menciona {nombre}")

    if "la carga borra y repone" in texto_min or "delete_many(" in texto:
        errores.append(
            "la presentación propone borrar antes de cargar; una interrupción dejaría la colección incompleta"
        )
    for prohibido in ["insert_many(", "cargar desde colab"]:
        if prohibido in texto_min:
            errores.append(
                f"la presentación conserva el flujo anterior de carga con Colab: {prohibido!r}"
            )
    if re.search(r"fillna\(\s*0\s*\)\.eq\(\s*0\s*\)", texto):
        errores.append(
            "el cruce convierte respuestas faltantes en cero; faltante y cero no tienen el mismo significado"
        )

    bloques_codigo = "\n".join(
        html_lib.unescape(bloque)
        for bloque in re.findall(
            r"<pre\b[^>]*class=[\"'][^\"']*\bcodigo\b[^\"']*[\"'][^>]*>(.*?)</pre>",
            texto,
            re.I | re.S,
        )
    )
    for pieza in [
        "pymongo[srv]", "getpass(", "quote_plus(", "MongoClient(",
        "pd.read_csv(", ".merge(", "client.close()",
    ]:
        if pieza not in bloques_codigo:
            errores.append(
                f"la presentación no incluye código Colab copiable para {pieza!r}; no existe cuaderno complementario"
            )

    pendientes = []
    for nombre in CAPTURAS_ESPERADAS:
        referencia = f"capturas/{nombre}"
        if referencia not in texto.replace("\\", "/"):
            errores.append(f"la presentación no referencia {referencia}")
        ruta_png = CAPTURAS / nombre
        if not ruta_png.exists():
            pendientes.append(nombre)
            continue
        try:
            ancho, alto = dimensiones_png(ruta_png)
        except (OSError, ValueError) as exc:
            errores.append(f"captura inválida {nombre}: {exc}")
            continue
        ancho_minimo = 800 if nombre == "10-compass-conexion-atlas.png" else 1000
        if ancho < ancho_minimo or alto < 600:
            errores.append(f"captura {nombre} demasiado pequeña: {ancho}x{alto}")

    if pendientes:
        mensaje = f"capturas reales pendientes ({len(pendientes)}): " + ", ".join(pendientes)
        if require_captures:
            errores.append(mensaje)
        else:
            avisos.append(mensaje)
            if not re.search(r"captura\s+(?:real\s+)?pendiente", texto_min):
                errores.append(
                    "hay capturas ausentes, pero la presentación no las rotula como 'Captura pendiente'"
                )

    # Ningún tutorial puede depender de un cuaderno que todavía no existe.
    for ruta_nb in set(re.findall(r"/Cuadernos/([^\"'?#]+\.ipynb)", texto, re.I)):
        archivo_nb = ROOT / "Cuadernos" / ruta_nb
        if not archivo_nb.exists():
            errores.append(f"la presentación enlaza un cuaderno inexistente: Cuadernos/{ruta_nb}")

    # URI de ejemplo permitida; cualquier hostname real de Atlas es un secreto operativo.
    for coincidencia in re.finditer(
        r"mongodb\+srv://[^\s\"'<]+@([^/\s\"'<]+\.mongodb\.net)", texto, re.I
    ):
        host = coincidencia.group(1)
        if "pega-tu-host" not in host.lower() and "<" not in host:
            errores.append(f"posible hostname real de Atlas expuesto: {host}")

    patrones_secretos = {
        "token GitHub": r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b",
        "clave AWS": r"\bAKIA[0-9A-Z]{16}\b",
        "clave Google": r"\bAIza[0-9A-Za-z_-]{30,}\b",
        "clave privada": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        "contraseña literal": r"(?i)(?:password|contrase(?:ñ|n)a)\s*[:=]\s*[\"'][^<\s][^\"']{7,}[\"']",
    }
    for etiqueta, patron in patrones_secretos.items():
        if re.search(patron, texto):
            errores.append(f"posible {etiqueta} expuesto en la presentación")

    # Una captura necesita inspección visual: el análisis binario no puede detectar texto sensible.
    if any((CAPTURAS / nombre).exists() for nombre in CAPTURAS_ESPERADAS):
        avisos.append(
            "las capturas existentes requieren inspección visual ampliada para descartar correo, IP, "
            "host, contraseña e identificadores de organización/proyecto"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, default=HTML_PREDETERMINADO)
    parser.add_argument("--require-captures", action="store_true")
    args = parser.parse_args()

    ruta_html = args.html if args.html.is_absolute() else ROOT / args.html
    errores, avisos, informe = [], [], {}

    validar_artefactos(errores)
    validar_baselines(errores, informe)
    validar_html(ruta_html, args.require_captures, errores, avisos)

    print("Validación Atlas — consultas, vistas y bandeja de Laura")
    print(f"HTML: {ruta_html.relative_to(ROOT) if ruta_html.exists() else ruta_html}")
    print("Baselines locales:")
    for clave, valor in informe.items():
        print(f"  - {clave}: {valor}")
    print()

    if avisos:
        print(f"AVISOS ({len(avisos)}):")
        for aviso in avisos:
            print("  -", aviso)
        print()

    if errores:
        print(f"ERRORES ({len(errores)}):")
        for error in errores:
            print("  -", error)
        return 1

    print("OK: JSON, HTML y baselines locales son coherentes.")
    if not args.require_captures:
        print("Antes de publicar la versión final, repita con --require-captures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
