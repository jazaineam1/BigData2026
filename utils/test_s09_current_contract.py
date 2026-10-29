"""Prueba el contrato vigente con mutaciones negativas, sin ejecutar Atlas ni E5."""
import copy,json,tempfile
from pathlib import Path
import s09_current_contract as contract
assert contract.validate_notebook()
original=json.loads((contract.ROOT/'Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb').read_text())
real_root=contract.ROOT
for before,after in [('"motor_ann_ejecutado":','"motor_omitido":'),('"advertencia":','"password":'),('NumPy exacto LOCAL (no Atlas)','Respaldo sin identificar'),('json.dump(evidencia','json.dump({}')]:
    nb=copy.deepcopy(original);count=0
    for cell in nb['cells']:
        source=''.join(cell['source']);count+=source.count(before);cell['source']=source.replace(before,after).splitlines(keepends=True)
    assert count>0,before
    with tempfile.TemporaryDirectory() as temp:
        contract.ROOT=Path(temp);p=contract.ROOT/'Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb';p.parent.mkdir();p.write_text(json.dumps(nb))
        try:contract.validate_notebook()
        except (AssertionError,SyntaxError,StopIteration):print('OK: rechaza mutación',before)
        else:raise AssertionError('Aceptó contrato roto: '+before)
contract.ROOT=real_root
assert contract.active_labs((real_root/'Presentaciones/s09-de-palabras-a-significado.html').read_text())==contract.ACTIVE_LABS
print('S09 contrato actual y cuatro mutaciones: OK')
