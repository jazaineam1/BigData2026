# Sistema visual de la sesión 2

Las once láminas se generan desde `utils/build_session2_visuals.py`: siete mapas conceptuales y cuatro apoyos del flujo Git. El sistema reemplaza diagramas genéricos por relaciones con capas, carriles, artefactos, métricas, umbrales y anotaciones pedagógicas.

## Secuencia narrativa

1. `01_hilo_decision`: decisión, proceso, roles, datos, evidencia, acción y conversación.
2. `02_proceso_as_is`: BPM con carriles, datos, gateway y retrabajo.
3. `03_adopcion_valor`: motivación, preparación y decisión incremental de adopción.
4. `04_casos_bi`: anatomía del caso de uso y criterio BI frente a Big Data.
5. `05_arquitectura_to_be`: trazabilidad entre negocio, información, aplicaciones y tecnología.
6. `06_ciclo_nist`: captura, preparación, análisis, visualización, acción y retroalimentación.
7. `07_estados_git`: propuesta, objeciones de los roles, corrección, PR, CI y juicio humano.

Las otras cuatro láminas documentan la ruta desde GitHub.com: reconocer el repositorio, leer `Files changed`,
conversar en un Pull Request y distinguir CI de revisión humana. La terminal aparece únicamente como equivalencia
opcional dentro del cuaderno.

## Gramática visual

- azul: proceso, propuesta o captura;
- amarillo: evidencia, preparación o punto de control;
- verde: suficiencia, corrección, validación o resultado aprobado;
- morado: capacidades analíticas y colaboración;
- naranja/rojo: decisión humana, retrabajo, riesgo o corrección;
- azul oscuro: propósito, gobierno y conclusión.

Todas las láminas usan un lienzo `1600 × 900`, encabezado común, conclusión visible, texto alternativo en el cuaderno y una versión SVG ampliable. Los PNG se conservan para una representación estable en Google Colab.

## Regeneración

```powershell
python utils/build_session2_visuals.py
```

Si Chrome no está disponible, se pueden actualizar únicamente los SVG:

```powershell
python utils/build_session2_visuals.py --svg-only
```

Antes de publicar se deben inspeccionar visualmente los once PNG y ejecutar:

```powershell
python utils/validate_session2_notebook.py
```
