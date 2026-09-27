from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path): return (ROOT/path).read_text(encoding="utf-8")

progress=read("lms/progress.html")
portfolio=read("lms/portfolio.html")
tests=read("tests/lms-v7-portfolio.spec.js")

checks=[
    ("progreso enlaza portafolio", 'href="portfolio.html"' in progress and "Exportar mi portafolio" in progress),
    ("competencias simples en progreso", all(x in progress for x in ["competency-simple","Evidencia suficiente ✓","Aún sin evidencia suficiente"])),
    ("progreso evita dashboard porcentual", "no añadimos otro tablero de porcentajes" in progress),
    ("portafolio usa sesión autenticada", "L.requireBigData()" in portfolio and "L.session('course_progress')" in portfolio),
    ("portafolio reúne evidencia propia", "L.session('me',{session_number:n})" in portfolio and "detail?.evidence||[]" in portfolio),
    ("portafolio reúne competencias", "L.core('competencies')" in portfolio),
    ("exportación PDF por impresión", "window.print()" in portfolio and "@media print" in portfolio),
    ("portafolio excluye telemetría", "No incluye heartbeats, telemetría técnica" in portfolio),
    ("portafolio no renderiza IDs", "user_id" not in portfolio and "auth_session_id" not in portfolio),
    ("QA portafolio", all(x in tests for x in ["competencias simples","solo sesiones, evidencias y competencias propias","responsive sin overflow horizontal"])),
]
failed=[n for n,ok in checks if not ok]
for n,ok in checks: print(("OK   " if ok else "FAIL ")+n)
if failed: raise SystemExit("Validación LMS V7 falló: "+", ".join(failed))
print("LMS V7 portafolio: OK")
