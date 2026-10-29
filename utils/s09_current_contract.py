"""Contrato activo de S09, separado de compatibilidad LMS histórica.
El cuaderno vigente exporta un expediente local Atlas/NumPy, no envía LAB9.
La QA del backend histórico se conserva en sus validadores; este módulo comprueba
el material que efectivamente abre el estudiante sin exigir UI retirada.
"""
import ast,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ACTIVE_LABS={'bd-s09-lab1','bd-s09-lab-e5','bd-s09-lab-chunk','bd-s09-lab2','bd-s09-lab3','bd-s09-lab4'}
def active_labs(deck):
    m=re.search(r'const LAB_BY_SLIDE=(\{[^;]+\});',deck)
    if not m:raise AssertionError('Falta mapa de laboratorios activos')
    return set(re.findall(r"'([^']+)'",m.group(1)))
def validate_notebook():
    nb=json.loads((ROOT/'Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb').read_text())
    sources=[''.join(c['source']) for c in nb['cells']]
    for c,s in zip(nb['cells'],sources):
        if c['cell_type']=='code':compile('\n'.join(l for l in s.splitlines() if not l.lstrip().startswith(('%','!'))),'S09','exec')
    export=next(s for s in sources if 'evidencia={' in s and 's09_atlas_evidencia.json' in s)
    tree=ast.parse(export);schema=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='evidencia' for t in n.targets))
    keys={ast.literal_eval(k) for k in schema.keys}
    required={'sesion','tipo','timestamp_utc','origen','lote','modelo','dimensiones','atlas_ping','index_queryable','motor_ann_ejecutado','motor_enn_ejecutado','respaldo','consulta','resultados_ann_atlas','resultados_enn_atlas','resultados_numpy_local','advertencia'}
    assert required<=keys,'Expediente incompleto'
    assert not keys & {'uri','password','token','api_key','credential'},'Credenciales en exportación'
    assert '"NO EJECUTADO"' in export and 'NumPy exacto LOCAL (no Atlas)' in export,'Motor no ejecutado debe quedar explícito'
    assert 'json.dump(evidencia' in export and 'atlas_real' in export,'Exportación debe provenir del estado ejecutado'
    assert not any('LMSBridge' in s or 'lms.registrar(' in s for s in sources),'No mezclar contrato retirado con expediente local'
    return True
if __name__=='__main__':
    assert validate_notebook()
    assert active_labs((ROOT/'Presentaciones/s09-de-palabras-a-significado.html').read_text())==ACTIVE_LABS
    print('S09 contrato actual: Python compilable, expediente con linaje y motores explícitos, seis LAB activos')
