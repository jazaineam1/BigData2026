"""SECOP II: descarga paginada con OFFSET según el contrato del Taller 1.

No descarga nada al importar. El ejercicio usa 40 registros de ventana histórica
y compara solicitudes secuenciales con ThreadPoolExecutor. Cliente HTTP inyectable
para poder probar sin red, con respuestas simuladas explícitamente etiquetadas.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
from time import perf_counter, sleep
from typing import Callable
import json

ENDPOINT = "https://www.datos.gov.co/resource/p6dx-8zbt.json"
# Ventana '2024-01' del TC1: enero-febrero, límite superior exclusivo.
WHERE = ("fecha_de_publicacion_del >= '2024-01-01T00:00:00.000' "
         "AND fecha_de_publicacion_del < '2024-03-01T00:00:00.000'")
# Mismo orden del TC1: :id desempata registros que comparten los otros campos.
ORDER = ("fecha_de_publicacion_del ASC,id_del_proceso ASC,"
         "nit_del_proveedor_adjudicado ASC,nombre_del_proveedor ASC,:id ASC")
SELECT = ("id_del_proceso,fecha_de_publicacion_del,"
          "descripci_n_del_procedimiento,modalidad_de_contratacion")
PAGE_SIZE = 20


def parametros(offset: int, *, total: int = 40, page_size: int = PAGE_SIZE) -> dict:
    """Genera exactamente la página solicitada; el último LIMIT puede ser menor."""
    if page_size < 1 or total < 1 or offset < 0 or offset >= total or offset % page_size:
        raise ValueError("OFFSET/LIMIT fuera de rango o mal alineados")
    return {"$select": SELECT, "$where": WHERE, "$order": ORDER,
            "$limit": min(page_size, total - offset), "$offset": offset}


def huella(filas: list[dict]) -> str:
    return sha256(json.dumps(filas, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8")).hexdigest()


def obtener_pagina(offset: int, *, get: Callable, total: int = 40,
                   page_size: int = PAGE_SIZE, timeout: int = 20,
                   dormir: Callable = sleep):
    """Dos intentos acotados, respeta Retry-After hasta tres segundos."""
    params = parametros(offset, total=total, page_size=page_size)
    for intento in (1, 2):
        try:
            resp = get(ENDPOINT, params=params,
                       headers={"Accept": "application/json",
                                "User-Agent": "UC-BigData2026-proyecto-final/1"},
                       timeout=timeout)
        except Exception:
            if intento == 2:
                raise
            dormir(1)
            continue
        estado = resp.status_code
        if estado in (429, 500, 502, 503, 504):
            if intento == 2:
                resp.raise_for_status()
                raise RuntimeError(f"HTTP {estado} tras dos intentos")
            retry = str(resp.headers.get("Retry-After", "1"))
            dormir(min(3, max(1, int(retry))) if retry.isdigit() else 1)
            continue
        resp.raise_for_status()
        filas = resp.json()
        if not isinstance(filas, list):
            raise ValueError("La API no devolvió una lista JSON")
        if len(filas) != params["$limit"]:
            raise ValueError(f"OFFSET {offset}: solicitadas {params['$limit']} "
                             f"filas; recibidas {len(filas)}. Página incompleta")
        if any(not isinstance(x, dict) for x in filas):
            raise ValueError(f"OFFSET {offset}: estructura de fila inválida")
        return {"offset": offset, "limit": params["$limit"],
                "rows": len(filas), "sha256": huella(filas),
                "status": estado, "attempts": intento, "data": filas}
    raise RuntimeError("No se obtuvo página")


def descargar(*, paralelo: bool, get: Callable, total: int = 40,
              page_size: int = PAGE_SIZE, dormir: Callable = sleep):
    """Plan de OFFSET validado: 0,20 para 40 registros, con máximo tres páginas."""
    offsets = tuple(range(0, total, page_size))
    if len(offsets) > 3:
        raise ValueError("Esta práctica está limitada a un máximo de tres páginas")
    inicio = perf_counter()

    def trabajo(off):
        return obtener_pagina(off, get=get, total=total, page_size=page_size, dormir=dormir)

    if paralelo:
        with ThreadPoolExecutor(max_workers=2) as pool:
            bloques = list(pool.map(trabajo, offsets))
    else:
        bloques = [trabajo(o) for o in offsets]

    bloques.sort(key=lambda b: b["offset"])
    if [b["offset"] for b in bloques] != list(offsets):
        raise ValueError("Falta página o hay OFFSET repetido")
    if sum(b["rows"] for b in bloques) != total:
        raise ValueError("La descarga ensamblada está incompleta")
    filas = [x for b in bloques for x in b["data"]]
    assert len(filas) == total
    resumen = {"modo": "paralelo" if paralelo else "secuencial",
               "url": ENDPOINT, "where": WHERE, "order": ORDER,
               "select": SELECT, "offsets": list(offsets), "size": page_size,
               "total": total, "segundos": round(perf_counter()-inicio, 5),
               "sha256": huella(filas),
               "paginas": [{k: v for k, v in b.items() if k != "data"} for b in bloques]}
    return filas, resumen


def ejecutar(*, destino, get: Callable, total: int = 40,
             page_size: int = PAGE_SIZE, dormir: Callable = sleep):
    """Registra una falla auténtica y no la suplanta por datos ficticios."""
    dest = Path(destino)
    dest.mkdir(parents=True, exist_ok=True)
    resumen = {"exito": False, "origen": "API SECOP II",
               "window": WHERE, "page_size": page_size, "total": total}
    try:
        serie, met_serie = descargar(paralelo=False, get=get, total=total,
                                    page_size=page_size, dormir=dormir)
        paralelo, met_para = descargar(paralelo=True, get=get, total=total,
                                      page_size=page_size, dormir=dormir)
        resumen.update({"exito": True, "serie": met_serie, "paralelo": met_para,
                        "mismas_filas_y_orden": serie == paralelo,
                        "advertencia": "La API puede cambiar entre las dos lecturas."})
        (dest / "A_paginas_secuencial.json").write_text(
            json.dumps(serie, ensure_ascii=False, indent=2), encoding="utf-8")
        (dest / "A_paginas_paralelo.json").write_text(
            json.dumps(paralelo, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as error:
        resumen.update({"error_tipo": type(error).__name__,
                        "error_detalle": str(error)[:450],
                        "advertencia": "API no verificada. Continuar con snapshot S13."})
    (dest / "A_descarga.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    return resumen
