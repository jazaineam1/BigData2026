# -*- coding: utf-8 -*-
"""
utils/patch_13_actividad1.py
============================
Actualiza Actividad 1 del taller 13 para reflejar limitaciones técnicas reales
encontradas por estudiantes con Databricks Community Edition.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(ROOT, "Cuadernos", "13_Taller_Final_MongoDB_SECOP_Tiempo_Real.ipynb")

with open(path, encoding="utf-8") as f:
    nb = json.load(f)

# Buscar la celda con "Actividad 1. Descarga completa desde 2021"
MARKER = "### Actividad 1. Descarga completa desde 2021"
found = False

for cell in nb["cells"]:
    src = "".join(cell.get("source", []))
    if MARKER in src:
        found = True
        # Reemplazar todo el contenido de Actividades (desde "## Actividades" hasta antes de "## Entregables")
        nueva_actividades = [
            "## Actividades del taller\n",
            "\n",
            "### Actividad 1. Descarga de datos desde 2021 (o ventana temporal justificada)\n",
            "\n",
            "**Meta ideal:** Descargar contratos, adiciones y ejecución contractual desde `2021-01-01`.\n",
            "\n",
            "**Realidad operativa:** El dataset de adiciones (2021–2026) contiene ~9.9 millones de registros, lo que puede exceder los límites de memoria y tiempo de ejecución en Databricks Community Edition. Si el equipo encuentra estos límites técnicos, puede usar una ventana temporal más reciente (p. ej., 2025–2026 o últimos 3 meses), **siempre que:**\n",
            "\n",
            "1. Documente el intento original de descarga desde 2021.\n",
            "2. Reporte explícitamente la limitación técnica encontrada (memoria, timeout, API limits).\n",
            "3. Justifique que la ventana temporal reducida sigue siendo representativa para el reto.\n",
            "4. Descargue el **volumen máximo posible** dentro de esa ventana.\n",
            "\n",
            "Guardar los datos crudos y reportar fecha/hora de descarga.\n",
            "\n",
            "**Resultado esperado:**\n",
            "\n",
            "- archivos raw o evidencia de descarga;\n",
            "- conteo de registros por tabla;\n",
            "- evidencia del filtro temporal aplicado;\n",
            "- reporte de limitaciones técnicas si aplican.\n",
            "\n",
            "### Actividad 2. Limpieza e integración\n",
            "\n",
            "Convertir tipos de datos y unir las bases.\n",
            "\n",
            "Resultado esperado:\n",
            "\n",
            "- contratos con valores numéricos;\n",
            "- fechas convertidas;\n",
            "- adiciones resumidas por contrato;\n",
            "- último avance de ejecución;\n",
            "- cruce territorial con DIVIPOLA;\n",
            "- reporte de registros sin cruce territorial.\n",
            "\n",
            "### Actividad 3. Texto no estructurado\n",
            "\n",
            "Crear `texto_busqueda` y `temas_detectados`.\n",
            "\n",
            "Resultado esperado:\n",
            "\n",
            "- tabla con contratos y temas;\n",
            "- resumen de contratos por tema;\n",
            "- explicación de reglas y limitaciones.\n",
            "\n",
            "### Actividad 4. Índice de prioridad\n",
            "\n",
            "Diseñar un índice descriptivo.\n",
            "\n",
            "Puede incluir:\n",
            "\n",
            "- valor alto;\n",
            "- número de adiciones;\n",
            "- avance bajo;\n",
            "- modalidad contractual;\n",
            "- tema detectado;\n",
            "- texto insuficiente o ambiguo.\n",
            "\n",
            "Resultado esperado:\n",
            "\n",
            "- ranking de contratos;\n",
            "- niveles baja, media y alta;\n",
            "- explicación de la fórmula.\n",
            "\n",
            "### Actividad 5. Modelo NoSQL en MongoDB\n",
            "\n",
            "Crear colecciones documentales.\n",
            "\n",
            "Colecciones mínimas:\n",
            "\n",
            "- `contratos_operativos`;\n",
            "- `alertas_revision`;\n",
            "- `entidades_resumen`;\n",
            "- `proveedores_resumen`;\n",
            "- `temas_resumen`;\n",
            "- `metadata_pipeline`.\n",
            "\n",
            "Resultado esperado:\n",
            "\n",
            "- documentos anidados;\n",
            "- índices;\n",
            "- consultas;\n",
            "- agregaciones;\n",
            "- evidencia de actualización.\n",
            "\n",
            "### Actividad 6. Dashboard\n",
            "\n",
            "Construir un tablero con:\n",
            "\n",
            "- total de contratos;\n",
            "- valor total;\n",
            "- contratos con prioridad alta;\n",
            "- contratos con adiciones;\n",
            "- ranking de entidades;\n",
            "- ranking de proveedores;\n",
            "- temas detectados;\n",
            "- tabla de alertas.\n",
            "\n",
            "Resultado esperado:\n",
            "\n",
            "- dashboard o capturas;\n",
            "- evidencia antes/después de una actualización.",
        ]
        cell["source"] = nueva_actividades
        break

if found:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print("[OK] Actividades actualizadas en el notebook 13")
    print("     - Actividad 1 ahora permite ventanas temporales justificadas")
else:
    print("[ERROR] No se encontró la celda con 'Actividad 1'")
