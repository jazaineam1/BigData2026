from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
migration=(ROOT/"infraestructura/lms/lms-s09-distractor-quality-v13.sql").read_text(encoding="utf-8")
deck=(ROOT/"Presentaciones/s09-de-palabras-a-significado.html").read_text(encoding="utf-8")

new_labels=[
 "Coincidencia literal de la frase completa, sin ponderar términos",
 "Como una puntuación absoluta comparable entre modelos de embeddings distintos",
 "En la memoria del modelo mientras permanece desplegado",
 "Lexical/BM25 aumentando el peso de términos raros",
 "Aproximada sobre una muestra aleatoria del corpus",
 "Explora más candidatos, pero la latencia suele bajar",
 "El vector de un documento de referencia elegido manualmente",
 "Scores normalizados de ambos mecanismos antes de sumarlos",
]
banned=[
 "Orden aleatorio de documentos",
 "Como distancia física",
 "Solo en el navegador",
 "Aleatoria",
 "Ninguna búsqueda",
 "Garantiza recall perfecto y costo cero",
 "Porque ninguno produce números",
]
checks=[
 ("migración solo cambia etiquetas", "jsonb_set" in migration and "config" not in migration and "answers" not in migration),
 ("values/hashes permanecen intactos", ",value}" not in migration and ",value}'" not in migration),
 ("nuevos distractores versionados", all(x in migration for x in new_labels)),
 ("D2 sin distractor caricaturesco", "El documento siempre es relevante" not in deck and "comparable directamente con 0.91 de cualquier otro modelo" in deck),
 ("D5 usa error plausible", "Descarta siempre el ranking lexical" not in deck and "score máximo sea numéricamente mayor" in deck),
 ("etiquetas caricaturescas reemplazadas por migración", all(x not in migration for x in banned)),
]
failed=[name for name,ok in checks if not ok]
for name,ok in checks: print(("OK   " if ok else "FAIL ")+name)
if failed: raise SystemExit("Distractores S09 FAIL: "+", ".join(failed))
print("S09 distractor quality: OK")
