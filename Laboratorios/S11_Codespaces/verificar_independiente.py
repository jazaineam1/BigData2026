#!/usr/bin/env python3
"""Auditoría independiente de S11. Solo biblioteca estándar de Python.

Uso:
    python verificar_independiente.py --caso lab
    python verificar_independiente.py --caso lab --modelo
    python verificar_independiente.py --proyecto proyectos/otro_caso

No afirma que el contenido sea verdadero: exige inspección humana de imagen y audio.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path


BASE = Path(__file__).resolve().parent


def cargar(ruta: Path):
    return json.loads(ruta.read_text(encoding="utf-8"))


def huella(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as entrada:
        for bloque in iter(lambda: entrada.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def comprobar_fuente(ruta: Path, esperada: str):
    if not ruta.is_file():
        raise AssertionError(f"Falta la fuente original: {ruta}")
    if huella(ruta) != esperada:
        raise AssertionError(f"SHA-256 diferente: {ruta}")


def palabras(texto: str) -> list[str]:
    return re.findall(r"\w+", texto.casefold())


def tasa_error_palabras(referencia: str, hipotesis: str) -> float:
    """Distancia mínima a nivel de palabras / número de palabras de referencia."""
    a, b = palabras(referencia), palabras(hipotesis)
    if not a:
        raise ValueError("La referencia de ASR está vacía")
    anterior = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        actual = [i]
        for j, y in enumerate(b, 1):
            actual.append(min(actual[-1] + 1, anterior[j] + 1,
                              anterior[j-1] + (x != y)))
        anterior = actual
    return anterior[-1] / len(a)


def revisar_segmentos(segmentos: list):
    for s in segmentos:
        inicio, fin = float(s["inicio_s"]), float(s["fin_s"])
        if inicio < 0 or fin < inicio or not str(s.get("texto", "")).strip():
            raise AssertionError(f"Segmento inválido: {s}")


def verificar_lab(salidas: Path):
    origen = cargar(salidas / "origen.json")
    for f in origen["archivos"]:
        comprobar_fuente(salidas / f["archivo"], f["sha256"])
    print(f"OK · RAW: {len(origen['archivos'])} archivos coinciden con origen.json")

    ocr = cargar(salidas / "ocr.json")
    imagen = Path(ocr["fuente"])
    comprobar_fuente(imagen, ocr["sha256"])
    # Segunda ruta de ejecución: binario de Tesseract, no lab.py.
    salida = subprocess.run(
        ["tesseract", str(imagen), "stdout", "-l", "spa", "--psm", "6"],
        check=True, text=True, capture_output=True, timeout=90,
    ).stdout.strip()
    if salida != ocr["texto_extraido"].strip():
        raise AssertionError("La CLI Tesseract y el OCR registrado no coinciden")
    print("OK · OCR: la CLI reproduce la salida y su SHA-256 es válido")
    print("REVISAR · Abre el PNG y confirma visualmente cada número: la CLI usa el mismo motor")

    asr_path = salidas / "asr.json"
    if asr_path.is_file():
        voz = cargar(asr_path)
        wav = Path(voz["fuente"])
        comprobar_fuente(wav, voz["sha256"])
        revisar_segmentos(voz["segmentos"])
        print(f"OK · ASR: {len(voz['segmentos'])} segmentos válidos y audio íntegro")
        origen_wav = next((a for a in origen["archivos"]
                           if a["archivo"] == wav.name and a["sha256"] == voz["sha256"]), None)
        if origen_wav and origen.get("referencia_asr"):
            wer = tasa_error_palabras(origen["referencia_asr"], voz["transcripcion"])
            print(f"CALIDAD · WER recalculado con referencia conocida: {wer:.4f}")
        else:
            print("AVISO · WER omitido: no hay referencia válida para este audio")
        print("REVISAR · Escucha el WAV y comprueba nombres y cifras")
    else:
        print("PENDIENTE · ASR: ejecuta python lab.py asr")

    indice_path = salidas / "indice.json"
    if indice_path.is_file():
        indice = cargar(indice_path)
        documentos = indice.get("documentos", [])
        if not documentos or indice["dimension"] != 768:
            raise AssertionError("Índice sin fragmentos o dimensión diferente de 768")
        for doc in documentos:
            if len(doc["embedding"]) != 768:
                raise AssertionError("Vector con dimensión incorrecta")
            if doc["modalidad"] == "imagen" and doc["sha256"] != ocr["sha256"]:
                raise AssertionError("Índice OCR obsoleto: vuelve a indexar")
            if asr_path.is_file() and doc["modalidad"] == "audio" and doc["sha256"] != cargar(asr_path)["sha256"]:
                raise AssertionError("Índice ASR obsoleto: vuelve a indexar")
        print(f"OK · ÍNDICE: {len(documentos)} fragmentos x 768 dimensiones")
    else:
        print("PENDIENTE · ÍNDICE: ejecuta python lab.py indexar")


def verificar_proyecto(raiz: Path):
    salidas = raiz / "salidas"
    manifiesto = cargar(salidas / "manifest.json")
    ruta_catalogo = salidas / "catalogo.jsonl"
    comprobar_fuente(ruta_catalogo, manifiesto["sha256_catalogo"])
    for item in manifiesto["archivos"]:
        comprobar_fuente(raiz / item["path"], item["sha256"])
    filas = [json.loads(s) for s in ruta_catalogo.read_text(encoding="utf-8").splitlines() if s.strip()]
    if len(filas) != manifiesto["documentos_ok"]:
        raise AssertionError("Número de registros distinto al manifiesto")
    for fila in filas:
        comprobar_fuente(raiz / fila["path"], fila["sha256"])
        revisar_segmentos(fila.get("segments", []))
    print(f"OK · CATÁLOGO: {len(filas)} registros; fuentes y manifiesto válidos")
    candidatos_path = salidas / "candidatos.jsonl"
    if candidatos_path.exists():
        candidatos = [json.loads(s) for s in candidatos_path.read_text(encoding="utf-8").splitlines() if s.strip()]
        textos = {f["path"]: f["extracted_text"] for f in filas}
        for candidato in candidatos:
            if candidato["path"] not in textos:
                raise AssertionError("Candidato sin fuente")
            if candidato["evidencia"].casefold() not in textos[candidato["path"]].casefold():
                raise AssertionError(f"Candidato sin respaldo en texto extraído: {candidato}")
        print(f"OK · EXTRACCIÓN: {len(candidatos)} candidatos rastreables al texto")
    indice_path = salidas / "indice.json"
    if indice_path.is_file():
        indice = cargar(indice_path)
        if indice.get("sha256_catalogo") != huella(ruta_catalogo):
            raise AssertionError("Índice desactualizado respecto al catálogo")
        print(f"OK · BÚSQUEDA: índice del catálogo verificado ({len(indice['docs'])} fragmentos)")
    print("REVISAR · Abre los originales y verifica manualmente las cifras reconocidas")


def verificar_modelo():
    payload = json.dumps({"model": "embeddinggemma-2:270m", "input": "Comprobación independiente"}).encode()
    req = urllib.request.Request("http://127.0.0.1:11434/api/embed", payload,
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        vectores = json.load(r)["embeddings"]
    if len(vectores) != 1 or len(vectores[0]) != 768:
        raise AssertionError("Ollama no devolvió exactamente un vector de 768 dimensiones")
    print("OK · OLLAMA: API HTTP directa y 768 dimensiones (no valida precisión semántica)")


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    modo = cli.add_mutually_exclusive_group()
    modo.add_argument("--caso", choices=["lab"], default="lab")
    modo.add_argument("--proyecto", type=Path)
    cli.add_argument("--modelo", action="store_true",
                     help="Consulta directamente a Ollama: requiere servicio y modelo descargado")
    args = cli.parse_args()
    try:
        if args.proyecto:
            verificar_proyecto(args.proyecto.resolve())
        else:
            verificar_lab(BASE / "salidas")
        if args.modelo:
            verificar_modelo()
    except (OSError, ValueError, KeyError, IndexError, AssertionError,
            subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR · Verificación: {exc}", file=sys.stderr)
        return 1
    print("RESULTADO · Controles técnicos correctos; la veracidad exige contrastar fuentes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
