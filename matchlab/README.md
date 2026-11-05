# MatchLab 4.2 · Identidad de clubes, análisis y jugadores

Sitio público: https://jazaineam1.github.io/BigData2026/matchlab/

## Novedades implementadas 5 de noviembre de 2026
- Escudos para los 20 clubes de Liga BetPlay II 2026 en resumen, tabla y partidos, con alternativa textual.
- Ficha de club: puntos actuales/máximo, posición, cotas matemáticas, diferencia respecto al octavo y próximos adversarios.
- Probabilidades 1X2 vistas desde el club seleccionado, no solo desde el local.
- Panel de muestra de goleadores de cada equipo, consultado en AS el 5 de noviembre, claramente separado del modelo predictivo; no es plantilla ni alineación.
- Panorama conjunto de las 20 probabilidades simuladas y puntos esperados, con selección interactiva.
- Navegación móvil horizontal y tabla compacta (#, club, PJ, DG, pts), tabla completa en escritorio.
- Bloqueo preventivo: fuentes de resultados marcadas como atrasadas no pueden consolidar nuevos finales en la tabla; se conserva el corte histórico.
- Conservados el motor de Monte Carlo, editor 1X2, índice 3^N y lectura de live.json.

## Datos, limitaciones y derechos
- Tabla y calendario: instantánea Liga BetPlay II del 5 de noviembre de 2026 con 17 PJ y 20 encuentros restantes. Marcadores posteriores sujetos a verificación del proveedor.
- El motor Poisson no utiliza jugadores, lesiones, xG ni cuotas. Sus probabilidades son experimentales, no calibradas para apuestas ni pronósticos comerciales.
- Escudos: URLs de identidad de equipo obtenidas de la API pública SportScore; son marcas de sus clubes. La atribución Powered by SportScore aparece en la página. Antes de un uso comercial, revisar la licencia y los derechos de imágenes.
- Goleadores: muestra de ranking público de AS Liga BetPlay II 2026, consulta 5 de noviembre de 2026; no tiene actualización automática.
- No se copian clasificaciones numéricas históricas de SportScore a la tabla vigente, porque su endpoint mezcla cortes de temporada.

Fuentes: https://sportscore.com/developers/ ; https://as.com/resultados/futbol/colombia_ii/2026/ranking/jugadores/goles/ ; https://www.sofascore.com/news/sofascores-redesigned-lineup-feature-take-match-analysis-to-the-next-level/ .

## Pruebas
- 20/20 clubes se seleccionan y presentan análisis y muestra de goleadores.
- 20 encuentros compartidos -> 40 apariciones por clubes, sin duplicados.
- Monte Carlo conjunto: top8 suma exactamente ocho por temporada.
- Proyección completa: cada club termina con 19 PJ.
- Chromium 1440px y 390px sin errores JS ni desbordamiento horizontal.
- Fallback de escudos cuando bloqueamos la red al probar.

**No es aún un producto de datos en vivo garantizados ni un modelo con impacto individual de jugadores.**
