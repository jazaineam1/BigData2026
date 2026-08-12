# Sistema visual de la sesión 2

Las diez láminas de la sesión se generan desde `utils/build_session2_visuals.py`.
El generador reemplaza los diagramas Mermaid anteriores porque las relaciones pedagógicas
requieren capas, carriles, artefactos, métricas y anotaciones que no deben reducirse a un
`flowchart` genérico.

## Gramática visual

- azul: proceso, estado local o captura;
- amarillo: datos, preparación y transformación;
- verde: almacenamiento, remoto, validación o resultado aprobado;
- morado: aplicaciones, analítica y colaboración;
- naranja/rojo: decisión humana, retrabajo, riesgo o corrección;
- azul oscuro: propósito, gobierno y conclusión.

Todas las láminas usan un lienzo `1600 × 900`, encabezado común, conclusión visible,
texto alternativo en el cuaderno y una versión SVG ampliable. Los PNG se conservan para
la renderización estable en Google Colab.

## Regeneración

```powershell
python utils/build_session2_visuals.py
```

Si Chrome no está disponible, se pueden actualizar únicamente los SVG:

```powershell
python utils/build_session2_visuals.py --svg-only
```

Antes de publicar se deben inspeccionar visualmente los diez PNG y ejecutar:

```powershell
python utils/validate_session2_notebook.py
```
