"""Calidad de distractores de las autocomprobaciones de S09.

Comprueba estructura y hechos verificables, no vocabulario general:
- la migración V55 solo cambia etiquetas, contra los value/etiquetas reales de V51;
- es idempotente por construcción (guardas por value y etiqueta antigua, versión
  solo si algo cambió);
- ninguna cadena caricaturesca antigua reaparece en deck, front-end ni migraciones
  posteriores;
- los value y los hashes no se tocan.

Uso: python utils/validate_s09_distractors.py [raiz_del_repo]
El argumento opcional permite ejecutar la prueba negativa sobre una copia.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
LMS_SQL = ROOT / "infraestructura/lms"
V51 = LMS_SQL / "lms-s09-deterministic-v51.sql"
V55 = LMS_SQL / "lms-s09-distractor-quality-v55.sql"
DECK = ROOT / "Presentaciones/s09-de-palabras-a-significado.html"

EXPECTED_CODES = {
    "bd-s09-lab1", "bd-s09-lab2", "bd-s09-lab-e5", "bd-s09-lab-chunk", "bd-s09-lab4",
    "bd-s09-lab5", "bd-s09-lab6", "bd-s09-lab7", "bd-s09-lab8",
}
EXPECTED_ROWS = 20

# Cadenas caricaturescas que no deben volver a aparecer (frases específicas).
BANNED = [
    "El documento siempre es relevante",
    "Descarta siempre el ranking lexical",
    "Orden aleatorio de documentos",
    "Como distancia física",
    "Solo en el navegador",
    "Garantiza recall perfecto y costo cero",
    "Garantiza relevancia perfecta",
    "Porque ninguno produce números",
    "No puede buscar sobre documentos",
    "No necesita índice",
]

# Decisión docente pendiente: se conservan con su etiqueta de V51 y NO están en la
# migración. Al decidir, mover la fila a la migración y quitarla de aquí.
PENDING = {
    ("bd-s09-lab8", 0, 2): ("embeddings", "Vectores concatenados"),
    ("bd-s09-lab4", 1, 2): ("none", "Ninguna búsqueda"),
}

ROW_RE = re.compile(
    r"\(\s*'(bd-s09-[a-z0-9-]+)'\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*'([^']*)'\s*,\s*'([^']*)'\s*,\s*'([^']*)'\s*\)"
)


def read(path):
    return path.read_text(encoding="utf-8")


def v51_steps():
    """code -> steps (lista) leídos del JSON de V51."""
    steps = {}
    for block in re.split(r"(?im)^update public\.bd_activity_catalog set", read(V51))[1:]:
        code = re.search(r"where code='([^']+)'", block)
        raw = re.search(r"steps='(\[.*?\])'::jsonb", block, re.S)
        if code and raw:
            steps[code.group(1)] = json.loads(raw.group(1))
    return steps


def sql_code(text):
    return "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("--"))


def main():
    checks = []

    def add(name, ok):
        checks.append((name, bool(ok)))

    mig_full = read(V55)
    mig = sql_code(mig_full)
    rows = [(c, int(s), int(o), v, old, new) for c, s, o, v, old, new in ROW_RE.findall(mig)]
    keys = [(c, s, o) for c, s, o, *_ in rows]
    base = v51_steps()

    add("V51 legible con las 9 actividades", EXPECTED_CODES <= set(base))
    add(f"migración con {EXPECTED_ROWS} cambios de etiqueta", len(rows) == EXPECTED_ROWS)
    add("cambios únicos y solo sobre actividades esperadas",
        len(set(keys)) == len(keys) and {r[0] for r in rows} <= EXPECTED_CODES)

    def option(code, s, o):
        try:
            return base[code][s]["options"][o]
        except (KeyError, IndexError):
            return None

    # Cada fila coincide con V51: mismo value y etiqueta antigua exacta.
    add("value y etiqueta antigua coinciden con V51",
        all(option(c, s, o) and option(c, s, o)["value"] == v and option(c, s, o)["label"] == old
            for c, s, o, v, old, _ in rows))
    add("cada etiqueta nueva difiere de la antigua", all(old != new for *_, old, new in rows))
    add("ninguna etiqueta nueva es una cadena caricaturesca",
        all(not any(b in new for b in BANNED) for *_, new in rows))

    # Estado final simulado: sin etiquetas antiguas ni repetidas dentro de un paso.
    final = json.loads(json.dumps(base))
    for c, s, o, _, _, new in rows:
        if option(c, s, o):
            final[c][s]["options"][o]["label"] = new
    old_labels = {old for *_, old, _ in rows}
    pend_labels = {label for _, label in PENDING.values()}
    stale = [(c, i) for c in EXPECTED_CODES for i, st in enumerate(final.get(c, []))
             for op in st.get("options", []) if op["label"] in old_labels - pend_labels]
    dup = [(c, i) for c in EXPECTED_CODES for i, st in enumerate(final.get(c, []))
           if len({op["label"] for op in st.get("options", [])}) != len(st.get("options", []))]
    add("estado final sin etiquetas antiguas reemplazadas", not stale)
    add("estado final sin etiquetas repetidas dentro de un paso", not dup)
    add("value y estructura de pasos intactos tras aplicar la migración",
        all([[op["value"] for op in st.get("options", [])] for st in final[c]]
            == [[op["value"] for op in st.get("options", [])] for st in base[c]] for c in EXPECTED_CODES))

    # Decisión docente pendiente: sin tocar y con su etiqueta de V51.
    add("los 2 distractores pendientes conservan su etiqueta de V51 y no están en la migración",
        all(k not in keys and option(*k) and option(*k)["value"] == vl[0] and option(*k)["label"] == vl[1]
            for k, vl in PENDING.items()))

    # Solo etiquetas: la migración no menciona hashes, config, evaluator ni hints.
    add("la migración solo escribe steps, version y updated_at",
        not re.search(r"\b(config|answers|evaluator|wall_prompt|hint)\b", mig)
        and len(re.findall(r"(?i)\bupdate\s+public\.", mig)) == 1
        and re.search(r"set steps = v_new,\s*version = version \+ 1,\s*updated_at = now\(\)", mig))

    # Idempotencia por construcción.
    guard_value = "= m.opt_value" in mig
    guard_label = "= m.old_label" in mig
    distinct = mig.find("v_new is distinct from a.steps")
    bump = mig.find("version = version + 1")
    add("idempotente: guardas por value y etiqueta antigua",
        guard_value and guard_label and mig.count("version = version + 1") == 1)
    add("idempotente: la versión solo sube dentro de 'if v_new is distinct from a.steps'",
        0 <= distinct < bump)
    add("la migración documenta qué hace y qué no hace",
        all(x in mig_full for x in ["QUÉ HACE", "QUÉ NO HACE", "IDEMPOTENCIA"]))

    # Deck: los dos distractores cambiaron de etiqueta, no de value.
    deck = read(DECK)
    add("D2 conserva value y usa error plausible",
        "['always_relevant','Un 0.91 es comparable directamente con 0.91 de cualquier otro modelo de embeddings']" in deck)
    add("D5 conserva value y usa error plausible",
        "['vector_only','Conserva únicamente el ranking cuyo score máximo sea numéricamente mayor']" in deck)

    # Ninguna cadena caricaturesca reaparece fuera de V51 (histórico) y de las
    # etiquetas antiguas de V55.
    skip = {V51.resolve(), V55.resolve()}
    hits = []
    scan_roots = [LMS_SQL, ROOT / "lms", ROOT / "Presentaciones"]
    for base_dir in scan_roots:
        if not base_dir.exists():
            continue
        for p in base_dir.rglob("*"):
            if not p.is_file() or p.resolve() in skip or p.suffix not in {".sql", ".html", ".js", ".json", ".ts", ".md"}:
                continue
            if base_dir.name == "Presentaciones" and not p.name.startswith("s09"):
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            hits += [f"{p.relative_to(ROOT)}: {b}" for b in BANNED if b in text]
    add("sin cadenas caricaturescas en deck, front-end ni migraciones (salvo V51 histórico)", not hits)

    failed = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(("OK   " if ok else "FAIL ") + n)
    for h in hits:
        print("     reaparece -> " + h)
    if failed:
        raise SystemExit("Distractores S09 FAIL: " + ", ".join(failed))
    print("S09 distractor quality: OK")


if __name__ == "__main__":
    main()
