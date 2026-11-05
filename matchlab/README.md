# MatchLab 4.1 — Página pública (Colombia 2026-II)

Publicación: `https://jazaineam1.github.io/BigData2026/matchlab/`

## Pantallas y cálculos

- **Real**: estadística de resultados finales confirmados, sin sumar partidos futuros.
- **Mi escenario**: solamente los encuentros que el usuario fijó; cuando fija pocos, sigue mostrando 17–19 PJ según el club, por definición.
- **Pronóstico completo**: un único calendario coherente de marcadores modales para todos los partidos restantes; todos llegan a 19 PJ.
- **Promedio Monte Carlo**: distribución conjunta de temporadas; todos llegan a 19 PJ y el promedio de victorias, empates y puntos suele ser fraccionario. No representa una clasificación concreta.
- **Explorador 3^N**: indexa todas las combinaciones de victoria, empate y derrota; el contador es exacto, sin afirmar que se enumeró todo.

## Actualización de resultados

1. El navegador intenta consultar el proveedor SportScore cada **60 segundos** (depende de CORS, conexión y disponibilidad).
2. GitHub Actions ejecuta el respaldo cada **10 minutos durante horarios de partido y fechas 5–15 de noviembre de 2026**, con actualización de `matchlab/live.json` solamente al observar cambios. GitHub Pages vuelve a desplegar ese recurso.
3. Cada fecha se consulta por competición, y se identifica por club local, visitante y fecha.
4. Un marcador `live` **no se registra como final**. Solo el estado de finalización explícito, score válido y emparejamiento unívoco pueden modificar la instantánea de la página que lo consume.
5. El proveedor puede estar retrasado. Si contradice partidos verificados del 4 de noviembre, muestra advertencia.
6. Esta es una **integración de datos de terceros de mejor esfuerzo**; no tiene acuerdo de tiempo real ni latencia garantizada. Para producción comercial se necesita un proveedor licenciado con coberturas y SLA.

## Seguridad y consistencia

- El histórico verificado queda incrustado en la página, con versiones y hora de corte.
- El resumen derivado en `live.json` no expone API keys y no reemplaza en GitHub el snapshot verificado.
- No se almacenan marcadores de otros partidos ni se redistribuye la base completa del proveedor.
- `live_sync.py` ignora estados sin score, identifica fechas y clubes, valida score 0–20 y comprueba duplicados.
- Cualquier final nuevo recalcula el modelo y descarta cotas matemáticas antiguas.
- `live.json` se produce mediante sustitución atómica, y se commitea solo cuando cambia.

## Pruebas ejecutadas

```bash
python matchlab/tests/test_ui.py
python matchlab/tests/test_regression.py
python matchlab/tests/test_live_sync.py
```

Validan escritorio (1440px), móvil (390px), 20 filas y 19 PJ proyectados; incorporación de final y reducción de 3^20 a 3^19; marcador vivo separado del definitivo; consistencia de puntos y calendario.

El optimizador de cotas de posiciones continúa en el backend Python separado; el sitio estático no anuncia certificación dinámica.