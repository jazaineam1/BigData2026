"""Generador offline de producto final (solo Python estándar).

Entrada:
  secop_final.csv       -> registros reales de S13 filtrados, con split fijo.
  predicciones.csv      -> predicciones reales SOLO para el conjunto test.
  D_modelo_dask.json    -> métrica del entrenamiento ya realizado.
Salida:
  observatorio.html     -> aplicación autocontenida: sin servidor, Internet ni Codespaces encendido.
No aloja datos privados, no detecta fraude, no entrena ningún modelo.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path


def generar(csv_datos, csv_predicciones, evidencia_modelo, html_destino):
    csv_datos = Path(csv_datos)
    csv_predicciones = Path(csv_predicciones)
    evidencia_modelo = Path(evidencia_modelo)
    html_destino = Path(html_destino)
    with csv_datos.open(encoding="utf-8-sig", newline="") as f:
        registros = list(csv.DictReader(f))
    with csv_predicciones.open(encoding="utf-8-sig", newline="") as f:
        predicciones = list(csv.DictReader(f))
    if not registros or not predicciones:
        raise ValueError("El observatorio requiere datos y predicciones reales.")
    esperadas = {"id_del_proceso", "texto", "modalidad", "split"}
    if not esperadas.issubset(registros[0]):
        raise ValueError(f"Faltan columnas del dataset: {sorted(esperadas-set(registros[0]))}")
    ids = [r["id_del_proceso"] for r in registros]
    if len(set(ids)) != len(ids):
        raise ValueError("El origen contiene identificadores repetidos.")
    test = {r["id_del_proceso"]: r for r in registros if r["split"] == "test"}
    pred_por_id = {r["id_del_proceso"]: r for r in predicciones}
    if set(pred_por_id) != set(test) or len(pred_por_id) != len(predicciones):
        raise ValueError("Las predicciones deben cubrir exactamente los IDs de test.")
    datos = []
    for r in registros:
        p = pred_por_id.get(r["id_del_proceso"], {})
        datos.append({
            "id": r["id_del_proceso"], "texto": r["texto"],
            "modalidad": r["modalidad"], "split": r["split"],
            "prediccion": p.get("modalidad_predicha", ""),
            "probabilidad": p.get("probabilidad_clase_predicha", ""),
        })
    metricas = json.loads(evidencia_modelo.read_text(encoding="utf-8"))
    payload = json.dumps({"registros": datos, "metricas": {
        "f1_test": metricas.get("f1_prueba_final"),
        "f1_dummy": metricas.get("f1_dummy"),
        "C": metricas.get("mejor_C"),
        "workers": metricas.get("workers"),
        "n_datos": len(datos), "n_prueba": len(test),
    }}, ensure_ascii=False, separators=(",", ":"))
    # Evita que datos de origen cierren la etiqueta script o creen HTML.
    payload = payload.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    plantilla = r"""<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Observatorio SECOP · Producto de laboratorio</title>
<style>
:root{--bg:#eff4f9;--surface:#fff;--text:#13253a;--muted:#486076;--line:#becedc;--accent:#12647c;--focus:#b86d16}
*{box-sizing:border-box}body{font:16px/1.48 system-ui,sans-serif;background:var(--bg);color:var(--text);margin:0}header,main,footer{padding:18px max(15px,calc((100vw - 1080px)/2))}header{background:#152943;color:white}h1{margin:8px 0;font-size:clamp(1.5rem,3vw,2.3rem)}h2{font-size:1.3rem}main{display:grid;gap:18px}.box{background:var(--surface);padding:17px;border:1px solid var(--line);border-radius:14px;min-width:0}.row{display:flex;gap:12px;flex-wrap:wrap}.stat{flex:1;min-width:140px;background:#e7f4f5;border-radius:9px;padding:12px}.stat strong{display:block;font-size:1.6rem}.stat span{font-size:.87rem}label{display:block;font-weight:650;margin-bottom:4px}input,select,button{font:inherit;padding:10px;border:1px solid var(--line);border-radius:8px;background:white;color:var(--text);width:100%}button{background:var(--accent);color:white;cursor:pointer;width:auto}button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid var(--focus);outline-offset:2px}.field{flex:1;min-width:180px}table{width:100%;border-collapse:collapse;font-size:.91rem}th,td{text-align:left;padding:10px;border-bottom:1px solid var(--line)}th{background:#e8f0f7}tr:hover{background:#f2f7fb}.scroll{overflow-x:auto}td button{padding:5px 8px}.help{color:var(--muted)}.note{border-left:4px solid var(--accent);padding:8px 13px;background:#eaf3fa}pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:280px;overflow-y:auto}.footer{font-size:.85rem;color:var(--muted)}@media(max-width:600px){header,main,footer{padding:14px}.box{padding:12px}}@media(prefers-color-scheme:dark){:root{--bg:#0b1624;--surface:#182a3b;--text:#f2f5f9;--muted:#d0dfed;--line:#405268;--accent:#225f85}header{background:#0c1d2e}.stat,.note,th{background:#233b4c}input,select{background:#182a3b;color:var(--text)}tr:hover{background:#263f54}}
</style></head>
<body>
<header><small>Big Data 2026-2S · Proyecto final del estudiante</small><h1>Compras Claras · Observatorio de modalidad SECOP II</h1>
<p>Datos reales de aula · consulta por texto · modalidades observadas y predicciones de un clasificador entrenado.</p></header>
<main>
<section class="box"><h2>Indicadores calculados a partir de mi ejecución</h2><div class="row" id="kpis" aria-live="polite"></div>
<p class="note"><strong>Advertencia:</strong> este modelo intenta predecir una modalidad administrativa del conjunto SECOP de clase. No detecta fraude, sobreprecios ni irregularidades. Las métricas y los resultados pertenecen exclusivamente a la muestra evaluada.</p></section>
<section class="box"><h2>Consultar y filtrar procesos</h2>
<div class="row">
<div class="field"><label for="q">Texto del proceso</label><input id="q" type="search" placeholder="Ej.: sistemas de información"></div>
<div class="field"><label for="clase">Modalidad observada</label><select id="clase"><option value="">Ambas modalidades</option><option>Contratación directa</option><option>Contratación régimen especial</option></select></div>
<div class="field"><label for="split">Conjunto de datos</label><select id="split"><option value="">Entrenamiento y prueba</option><option value="train">Entrenamiento</option><option value="test">Prueba</option></select></div>
</div>
<p class="help" id="resumen" aria-live="polite"></p><div class="scroll"><table><thead><tr><th>ID</th><th>Texto del procedimiento</th><th>Modalidad real</th><th>Predicción en test</th><th>Acción</th></tr></thead><tbody id="filas"></tbody></table></div>
<p class="help">Se muestran hasta 40 filas por búsqueda para evitar una página pesada. Los filtros sí revisan todos los registros.</p>
<button type="button" id="exportar">Descargar resultados filtrados (CSV)</button></section>
<section class="box"><h2>Expediente consultado</h2><div id="detalle" aria-live="polite" class="help">Selecciona “Ver” en una fila para consultar el expediente sin salir del observatorio.</div></section>
<section class="box"><h2>Interpretación de las métricas</h2>
<p><strong>Cómo se lee:</strong> F1 macro es la media del F1 por clase en el conjunto reservado para prueba.</p>
<p><strong>Qué nos dice:</strong> cuánto acierta el modelo en la distribución concreta de este laboratorio, comparado con una referencia muy simple.</p>
<p><strong>Qué NO permite concluir:</strong> desempeño en todos los contratos del país o detección de irregularidades; se necesita una evaluación temporal externa para ello.</p>
<p><strong>Qué error común:</strong> confundir predicciones del conjunto test con predicciones sobre procesos nuevos y desconocidos.</p>
<p class="help">Página exportada por el propio cuaderno. No necesita servidor, APIs ni mantener Codespaces abierto. No está conectada a SECOP en tiempo real.</p></section>
</main><footer class="footer">Herramienta estática verificable · funcionamiento sin conexión · resultados provenientes de los archivos de este proyecto.</footer>
<script type="application/json" id="payload">__DATOS__</script>
<script>
"use strict";
const base=JSON.parse(document.getElementById("payload").textContent),data=base.registros,metrics=base.metricas;
const $=id=>document.getElementById(id);
function metric(title,value){let el=document.createElement("div");el.className="stat";let n=document.createElement("strong");n.textContent=String(value);let s=document.createElement("span");s.textContent=title;el.append(n,s);$("kpis").append(el)}
metric("Registros",metrics.n_datos);metric("Reservados para test",metrics.n_prueba);
metric("F1 macro en test",metrics.f1_test===null?"No disponible":metrics.f1_test);
metric("F1 del control",metrics.f1_dummy===null?"No disponible":metrics.f1_dummy);
function norm(x){return String(x||"").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"")}
function filtrados(){const q=norm($("q").value.trim()),c=$("clase").value,s=$("split").value;return data.filter(r=>(!c||r.modalidad===c)&&(!s||r.split===s)&&(!q||norm(r.texto+" "+r.id+" "+r.modalidad).includes(q)))}
function render(){const matches=filtrados();$("resumen").textContent=matches.length+" expedientes coinciden con los filtros";const body=$("filas");body.replaceChildren();for(const r of matches.slice(0,40)){const tr=document.createElement("tr");for(const v of [r.id,r.texto.slice(0,170),r.modalidad,r.prediccion||"Solo en test"]){const td=document.createElement("td");td.textContent=v;tr.append(td)}const td=document.createElement("td");const b=document.createElement("button");b.type="button";b.textContent="Ver";b.addEventListener("click",()=>{const detail=$("detalle");detail.replaceChildren();const title=document.createElement("strong");title.textContent="ID "+r.id;const p=document.createElement("p");p.textContent=r.texto;const q=document.createElement("p");q.textContent="Modalidad real: "+r.modalidad+" · split: "+r.split+" · predicción: "+(r.prediccion||"no calculada para entrenamiento")+" · probabilidad de clase predicha: "+(r.probabilidad||"no aplica");detail.append(title,p,q);detail.scrollIntoView({behavior:"smooth",block:"nearest"})});td.append(b);tr.append(td);body.append(tr)}}
for(const id of ["q","clase","split"])$(id).addEventListener("input",render);
$("exportar").addEventListener("click",()=>{const subset=filtrados(),head=["id","texto","modalidad","split","prediccion","probabilidad"];const campo=x=>'"'+String(x||"").replace(/"/g,'""')+'"';const csv=[head.join(","),...subset.map(r=>head.map(k=>campo(r[k])).join(","))].join("\r\n");const blob=new Blob(["\ufeff"+csv],{type:"text/csv;charset=utf-8"});const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download="consulta_observatorio_secop.csv";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)});
render();
</script></body></html>"""
    html_destino.parent.mkdir(parents=True, exist_ok=True)
    html_destino.write_text(plantilla.replace("__DATOS__", payload), encoding="utf-8")
    return {"filas": len(registros), "test": len(test), "html": str(html_destino)}
