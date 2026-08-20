# -*- coding: utf-8 -*-
"""
utils/cruzar_noticias_secop.py
==============================
Cruza las noticias de contratacion de El Tiempo con las entidades contratantes
de SECOP II, y deja el resultado listo para el laboratorio.

Pregunta que responde
---------------------
De las entidades que contratan con el Estado, ¿cuales aparecieron en la prensa
este ano, y en cuantas noticias?

Tres formas de cruzar, a proposito
----------------------------------
El cruce se hace de tres maneras porque la diferencia entre ellas es el
contenido pedagogico. Un cruce por subcadena parece mucho mejor y es falso.

  1. subcadena          -> `sena` encuentra `senalo`, `senador`, `ensenanza`
  2. palabra completa   -> honesto para nombres genericos
  3. nombre completo    -> el unico que identifica UNA entidad

Limite que hay que declarar
---------------------------
Esto enlaza NOTICIA <-> ENTIDAD, no NOTICIA <-> CONTRATO. Una noticia puede
nombrar a una entidad por cualquier motivo, no necesariamente por sus contratos.
Sirve para ordenar una fila de revision; no prueba absolutamente nada.

Uso
---
    python utils/cruzar_noticias_secop.py
"""

import glob
import json
import os
import re
import unicodedata
from collections import Counter

import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTICIAS = os.path.join(REPO, "Datos", "noticias_contratacion_2026.json")
SECOP_GLOB = os.path.join(REPO, "Cuadernos", "datos", "secop_chunks", "secop_chunk_*.csv")
SALIDA = os.path.join(REPO, "Datos", "entidades_en_noticias_2026.json")

# Nombres genericos que, aunque sean el nombre completo de alguna entidad, no
# identifican a nadie en un texto periodistico.
DEMASIADO_GENERICOS = {
    "alcaldia municipal", "hospital", "municipio", "gobernacion", "personeria",
    "concejo municipal", "empresa de servicios publicos",
}


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto).lower())
    texto = texto.encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", texto).strip()


def texto_de(noticia):
    partes = [noticia.get("titulo", "")]
    partes += [b.get("texto", "") for b in noticia.get("cuerpo", []) if b.get("texto")]
    partes += [t.get("nombre", "") for t in noticia.get("etiquetas", [])]
    return normalizar(" ".join(partes))


def main():
    print("1/4 Cargando noticias de contratacion...")
    with open(NOTICIAS, encoding="utf-8") as f:
        noticias = json.load(f)
    textos = {n["_id"]: texto_de(n) for n in noticias}
    print(f"    {len(noticias)} noticias")

    print("2/4 Cargando entidades de SECOP...")
    frames = [
        pd.read_csv(f, usecols=["entidad", "departamento_entidad"], low_memory=False)
        for f in sorted(glob.glob(SECOP_GLOB))
    ]
    secop = pd.concat(frames, ignore_index=True)
    procesos_por_entidad = secop["entidad"].value_counts()
    depto_por_entidad = (
        secop.dropna(subset=["entidad"])
        .groupby("entidad")["departamento_entidad"]
        .agg(lambda s: s.mode().iat[0] if not s.mode().empty else "")
    )
    print(f"    {len(secop)} procesos, {secop['entidad'].nunique()} entidades distintas")

    print("3/4 Cruzando por nombre completo de entidad...")
    candidatas = []
    for nombre in procesos_por_entidad.index:
        n = normalizar(nombre)
        n = re.sub(r"^\(|\)$", "", n).strip()
        if len(n) < 14 or n in DEMASIADO_GENERICOS:
            continue
        candidatas.append((nombre, n))

    hallazgos = {}
    for original, norma in candidatas:
        ids = [i for i, t in textos.items() if norma in t]
        if ids:
            hallazgos[original] = ids

    print(f"    Entidades evaluadas: {len(candidatas)}")
    print(f"    Entidades nombradas en al menos una noticia: {len(hallazgos)}")

    noticias_con_entidad = {i for ids in hallazgos.values() for i in ids}
    print(f"    Noticias que nombran al menos una entidad: "
          f"{len(noticias_con_entidad)}/{len(noticias)}")

    print("4/4 Guardando resultado...")
    por_id = {n["_id"]: n for n in noticias}
    registro = []
    for entidad, ids in sorted(hallazgos.items(), key=lambda kv: -len(kv[1])):
        registro.append({
            "entidad": entidad,
            "departamento": str(depto_por_entidad.get(entidad, "")),
            "procesos_en_secop": int(procesos_por_entidad[entidad]),
            "noticias": len(ids),
            "ejemplos": [
                {"id": i, "titulo": por_id[i]["titulo"], "url": por_id[i]["url"],
                 "publicado": por_id[i]["publicado"]}
                for i in ids[:3]
            ],
        })
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=1)
    print(f"    {SALIDA}")

    print()
    print("=" * 78)
    print("ENTIDADES CONTRATANTES QUE FUERON NOTICIA EN 2026")
    print("=" * 78)
    print(f"{'ENTIDAD':52s} {'NOTICIAS':>8s} {'PROCESOS':>9s}")
    print("-" * 78)
    for r in registro[:20]:
        print(f"{r['entidad'][:52]:52s} {r['noticias']:8d} {r['procesos_en_secop']:9d}")

    print()
    print("Contraste de los tres cruces (para el laboratorio):")
    genericas = ["alcaldia", "gobernacion", "ministerio", "universidad", "hospital",
                 "fiscalia", "contraloria", "icbf", "sena", "dian", "policia"]
    sub = sum(1 for t in textos.values() if any(k in t for k in genericas))
    pal = sum(1 for t in textos.values()
              if any(re.search(r"\b" + k + r"\b", t) for k in genericas))
    print(f"  subcadena        : {sub}/{len(textos)} noticias")
    print(f"  palabra completa : {pal}/{len(textos)} noticias")
    print(f"  entidad completa : {len(noticias_con_entidad)}/{len(textos)} noticias")

    falsos = Counter(
        m for t in textos.values()
        for k in ("sena", "dian")
        for m in re.findall(r"\w*" + k + r"\w*", t)
        if m not in ("sena", "dian")
    )
    print()
    print("  De donde salia el exceso del cruce por subcadena:")
    for palabra, veces in falsos.most_common(8):
        print(f"    {palabra:16s} {veces}")

    construir_bandeja(hallazgos, por_id)


def construir_bandeja(hallazgos, por_id):
    """
    Lleva el cruce de ENTIDAD a CONTRATO, que es lo que Laura necesita de verdad.

    Una entidad nombrada en prensa no es accionable: Laura no revisa entidades,
    revisa procesos concretos. Aqui se arma la bandeja de revision: los procesos
    de esas entidades, con las senales que SECOP si trae y la senal externa de
    la prensa al lado.

    Limite que hay que declarar en clase: el enlace es ENTIDAD <-> NOTICIA, no
    CONTRATO <-> NOTICIA. La noticia habla de la entidad, casi nunca de este
    proceso en particular. La bandeja ordena por donde empezar a mirar; no dice
    que haya nada malo en ninguna fila.
    """
    print()
    print("5/5 Construyendo la bandeja de revision (nivel contrato)...")

    columnas = [
        "entidad", "nombre_del_procedimiento", "precio_base",
        "modalidad_de_contratacion", "respuestas_al_procedimiento",
        "estado_del_procedimiento", "fecha_de_publicacion_del",
        "departamento_entidad", "id_del_proceso",
    ]
    procesos = pd.concat(
        [pd.read_csv(f, usecols=columnas, low_memory=False)
         for f in sorted(glob.glob(SECOP_GLOB))],
        ignore_index=True,
    )

    noticias_por_entidad = {e: len(ids) for e, ids in hallazgos.items()}
    procesos["noticias_entidad"] = procesos["entidad"].map(noticias_por_entidad)
    con_prensa = procesos[procesos["noticias_entidad"].notna()].copy()

    print(f"    Procesos totales: {len(procesos)}")
    print(f"    De entidades que salieron en prensa: {len(con_prensa)} "
          f"({len(con_prensa) / len(procesos) * 100:.1f}%)")

    # Tres senales, ninguna concluyente por si sola.
    con_prensa["sin_competencia"] = (
        con_prensa["modalidad_de_contratacion"].str.contains("directa", case=False, na=False)
    )
    con_prensa["sin_respuestas"] = con_prensa["respuestas_al_procedimiento"].fillna(-1).eq(0)

    directa_total = procesos["modalidad_de_contratacion"].str.contains(
        "directa", case=False, na=False).mean()
    print(f"    OJO: la contratacion directa es el {directa_total * 100:.0f}% de TODO SECOP.")
    print("         Por si sola no senala nada; solo sirve combinada.")

    bandeja = con_prensa[
        con_prensa["sin_competencia"] & con_prensa["sin_respuestas"]
    ].nlargest(200, "precio_base")

    salida = os.path.join(REPO, "Datos", "bandeja_revision_2026.json")
    registros = []
    for _, r in bandeja.iterrows():
        ids = hallazgos.get(r["entidad"], [])
        registros.append({
            "id_del_proceso": r["id_del_proceso"],
            "entidad": r["entidad"],
            "departamento": r["departamento_entidad"],
            "objeto": str(r["nombre_del_procedimiento"])[:180],
            "valor": float(r["precio_base"]) if pd.notna(r["precio_base"]) else None,
            "modalidad": r["modalidad_de_contratacion"],
            "respuestas": int(r["respuestas_al_procedimiento"] or 0),
            "estado": r["estado_del_procedimiento"],
            "publicado": str(r["fecha_de_publicacion_del"])[:10],
            "noticias_de_la_entidad": int(r["noticias_entidad"]),
            "titulares": [
                {"titulo": por_id[i]["titulo"], "url": por_id[i]["url"],
                 "publicado": por_id[i]["publicado"][:10]}
                for i in ids[:2]
            ],
        })
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=1)
    print(f"    {salida}  ({len(registros)} procesos)")

    print()
    print("=" * 78)
    print("BANDEJA DE REVISION — los 10 primeros")
    print("=" * 78)
    for r in registros[:10]:
        print(f"  ${r['valor']:>16,.0f}  {r['noticias_de_la_entidad']:3d} not.  "
              f"{r['entidad'][:32]:32s}  {r['objeto'][:38]}")


if __name__ == "__main__":
    main()
