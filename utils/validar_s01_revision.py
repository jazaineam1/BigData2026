#!/usr/bin/env python3
"""Validación manual S01; sin GitHub Actions, sin red y sin alterar materiales oficiales."""
import argparse, ast, json, tempfile, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / "revision"
read = lambda p: json.loads(p.read_text(encoding="utf-8"))
parser = argparse.ArgumentParser()
execution = parser.add_mutually_exclusive_group()
execution.add_argument("--execute", action="store_true", help="Ejecutar todas las celdas con nbclient")
execution.add_argument("--core", action="store_true", help="Ejecutar solo el núcleo hasta el apéndice y QA autónoma")
parser.add_argument("--browser", action="store_true", help="Comprobar Chrome/Chromium con Playwright")
args = parser.parse_args()
slides = read(REV / "s01-source.json")
nb = read(REV / "s01-laboratorio.ipynb")
corpus = read(ROOT / "Datos/tc2_corpus_2026.json")["documentos"]
gate = read(REV / "s01-calidad.json")
teaching = [s for s in slides if s[1] != "Pausa"]
assert len(slides) == 26 and len(teaching) == 25 and sum(s[0] for s in slides) == 150
assert all(len(s)>11 and s[11] and all(u["title"] and u["paragraphs"] for u in s[11]) for s in teaching)
assert len({c["id"] for c in nb["cells"]}) == len(nb["cells"])
assert len(nb["cells"])>=44 and sum(c["cell_type"]=="code" for c in nb["cells"])>=24
assert len({s[10]["question"] for s in teaching}) == 25
assert all(len(s[10]["choices"]) == len(s[10]["feedback"]) == 3 and 0 <= s[10]["correct"] < 3 for s in teaching)
assert all(any(c.get("id") == "s01-" + s[9].lower() for c in nb["cells"]) for s in teaching)
cells = {c["id"]: c for c in nb["cells"]}
fixture = ast.parse("".join(cells["s01-fixture"]["source"]))
assign = next(x for x in fixture.body if isinstance(x, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CORPUS" for t in x.targets))
embedded = json.loads(ast.literal_eval(assign.value.args[0]))
assert embedded == corpus and len(corpus) == len({r["id_proceso"] for r in corpus}) == 200
for c in nb["cells"]:
    if c["cell_type"] == "code":
        compile("".join(c["source"]), c["id"], "exec")
assert "CONSULTA_VIVA=False" in "".join(cells["s01-http"]["source"])
assert gate["state"] == "NO_APROBADA" and not gate["next_session_unlocked"]
print("OK estática: 25 pantallas, 150 min, 25 comprobaciones, corpus exacto, sintaxis Python y puerta cerrada.")

if args.execute or args.core:
    import nbformat
    from nbclient import NotebookClient
    with tempfile.TemporaryDirectory(prefix="qa_s01_") as tmp:
        previous = os.environ.get("TMPDIR")
        os.environ["TMPDIR"] = tmp
        try:
            book = nbformat.read(REV / "s01-laboratorio.ipynb", as_version=4)
            nbformat.validate(book)
            if args.core:
                stop=next(i for i,c in enumerate(book.cells) if c.id=="s01-apendice")
                book.cells=book.cells[:stop]
            book.cells.append(nbformat.v4.new_code_cell('''# Prueba QA añadida solo al cuaderno en memoria, no al archivo docente.\nfor N,l,c in [(41,7,6),(137,29,17),(199,45,40)]:\n    p=(N+l-1)//l; b=(N+c-1)//c\n    h={"paginas":p,"ultima_pagina":N-(p-1)*l,"bloques":b,"ultimo_bloque":N-(b-1)*c}\n    a1,a2,retro,igual=reto_s01(N,l,c,h)\n    assert igual and all(x["coincide"] for x in retro)\n    assert empaquetar_s01(a1,HASH_SNAPSHOT).is_file() and empaquetar_s01(a2,HASH_SNAPSHOT).is_file()\n    casos=comparar_decisiones(N,l,c)\n    assert len(casos)==4 and len({r["hash_raw"] for r in casos[:3]})==1\n    assert casos[3]["hash_raw"]!=casos[0]["hash_raw"]\nprint("QA tres variantes autónomas y aislamiento: OK")\n'''))
            executed = NotebookClient(book, timeout=90, kernel_name="python3",
                resources={"metadata": {"path": tmp}}).execute()
            assert all(c.get("execution_count") is not None for c in executed.cells if c.cell_type == "code")
            assert not any(o.get("output_type") == "error" for c in executed.cells if c.cell_type == "code" for o in c.get("outputs", []))
            print("OK ejecución de núcleo guardado" if args.core else "OK ejecución completa del notebook guardado, sin consulta viva.")
        finally:
            if previous is None: os.environ.pop("TMPDIR", None)
            else: os.environ["TMPDIR"] = previous

if args.browser:
    from playwright.sync_api import sync_playwright
    import shutil
    failures = []
    with sync_playwright() as p:
        chromium = shutil.which("chromium") or shutil.which("google-chrome")
        browser = p.chromium.launch(executable_path=chromium, headless=True) if chromium else p.chromium.launch(headless=True)
        for width,height in [(1366,768),(1920,1080),(360,800)]:
            page=browser.new_page(viewport={"width":width,"height":height})
            errors=[]
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto((REV/"s01.html").as_uri())
            assert page.locator("#cover").is_visible()
            page.locator("#startClass").click()
            assert page.locator("#lesson").is_visible()
            for i,s in enumerate(slides):
                page.locator("#jump").select_option(str(i))
                assert page.locator("#heading").inner_text()==s[2]
                if width>760:
                    dims=page.evaluate("({h:document.documentElement.scrollHeight,v:innerHeight,visual:document.querySelector('.visual').scrollHeight,client:document.querySelector('.visual').clientHeight})")
                    if dims["h"]>dims["v"]+2 or dims["visual"]>dims["client"]+2:
                        failures.append({"viewport":[width,height],"slide":i+1,"overflow":dims})
                else:
                    if page.evaluate("document.documentElement.scrollWidth > innerWidth+2"):
                        failures.append({"viewport":[width,height],"slide":i+1,"horizontal_overflow":True})
                if s[10] if len(s)>10 else False:
                    page.locator("#checkToggle").click()
                    select=page.locator("#quickCheck .checkpanel select")
                    assert select.input_value()==""
                    verify=page.locator(".checkpanel button")
                    assert verify.is_disabled()
                    select.select_option(str(s[10]["correct"]))
                    verify.click()
                    assert "Respuesta correcta" in page.locator(".checkpanel .feedback").inner_text()
                    page.locator("#checkToggle").click()
            if errors: failures.extend({"viewport":[width,height],"error":e} for e in errors)
            page.close()
        browser.close()
    if failures:
        print(json.dumps(failures,ensure_ascii=False,indent=2))
        raise SystemExit("QA visual no aprobada; resolver desbordamientos/errores antes de certificar.")
    print("OK navegador real: tres tamaños, navegación y comprobaciones. Falta inspección visual humana y ensayo.")
