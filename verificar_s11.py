"""Diagnóstico S11 sin instalaciones, descargas ni inferencia."""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def git(*args):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else "(no disponible)"

def verificar():
    print("\n=== Diagnóstico de acceso S11 (NO ejecuta modelos) ===")
    print("Carpeta:", ROOT)
    print("Repositorio:", git("remote", "-v").splitlines()[:2])
    print("Rama actual:", git("branch", "--show-current"))
    print("Python:", sys.executable, sys.version.split()[0])
    paths = ["01_laboratorio.ipynb", "configuracion_s11.json",
             ".devcontainer/devcontainer.json", "GUIA_ACCESO_ESTUDIANTES.md"]
    for name in paths:
        file = ROOT / name
        print(("OK  " if file.is_file() else "FALTA  ") + name)
    nb = ROOT / "01_laboratorio.ipynb"
    if nb.is_file():
        try:
            notebook = json.loads(nb.read_text(encoding="utf-8"))
            assert notebook["nbformat"] == 4
            for i, cell in enumerate(notebook["cells"]):
                if cell.get("cell_type") == "code":
                    src = "".join(cell.get("source", []))
                    compile(src, f"celda {i}", "exec")
            print("OK  Archivo notebook JSON y sintaxis de sus celdas válidos",
                  len(notebook["cells"]), "celdas.")
        except (ValueError, KeyError, AssertionError, SyntaxError) as exc:
            print("ERROR  El cuaderno tiene un problema de formato:", exc)
    print("Extensiones recomendadas: ms-python.python / ms-toolsai.jupyter")
    print("Bibliotecas (solo comprobar):")
    for package in ["ipykernel", "nbformat", "PIL", "pytesseract", "requests", "streamlit"]:
        print(" ", package, "OK" if importlib.util.find_spec(package) else "FALTA")
    print("Tesseract:", shutil.which("tesseract") or "NO INSTALADO")
    print("Ollama:", shutil.which("ollama") or "NO INSTALADO")
    print("\nSi el notebook NO aparece: verifica que tu rama sea s11-estudiantes.")
    print("Si se abre como JSON: Abrir con... → Jupyter Notebook.")
    print("Si el Markdown .md no se previsualiza: Ctrl+Shift+V, o")
    print("Ctrl+Shift+P → Markdown: Open Preview to the Side.")
    print("Si una celda Markdown del notebook muestra ##: sal de edición con Shift+Enter.")
    print("No borres tu Codespace sin guardar cambios.")
    return nb.is_file()

if __name__ == "__main__":
    sys.exit(0 if verificar() else 1)
