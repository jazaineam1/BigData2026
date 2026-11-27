# Puerta secuencial de calidad — S01
Estado: **NO APROBADA / S02 BLOQUEADA**. Se exige ≥4,5/5, cada dimensión esencial ≥4, 40.000 palabras originales sustantivas deduplicadas por sesión, ≥25 diapositivas de enseñanza, laboratorio reproducible, evidencia visual y ensayo de 150 minutos. La calificación se justifica con evidencia; no se redondea para desbloquear. Solo se trabaja sobre S01 hasta que todas las puertas pasen. No se modifica main ni el curso publicado.
 
## Implementación actual
S01 tiene 25 pantallas de enseñanza y una pausa, agenda total 150 min, presentación específica que conserva el piloto anterior, cinco mecanismos nuevos, lectura ampliada por pantalla, enlaces por sección A0–A8, y un cuaderno alternativo autónomo con 200 registros reales del snapshot (no descarga viva). La ruta por defecto no depende de red, ICFES remoto ni API. Se conservan el cuaderno original y las demás sesiones. Paquete RAW, derivados y manifiesto persistente en runtime. La consulta viva es optativa y separada.
 
Conteo bruto de prosa de lectura en presentación: 8746; markdown de cuaderno: 1477. El total bruto 10223 no es elegible deduplicado y está por debajo de 40.000 incluso antes de excluir coincidencias. No se contabilizan datos incrustados, código ni metadatos. Estado de extensión: NO CUMPLE.
 
## Evidencia previa al guardado
Corpus comprobado: 200 filas, 200 IDs, 51 entidades distintas. Cuatro páginas de 50 con salto 40: 200 filas y 170 IDs; 30 repetidos y 30 ausentes. Agenda de 150 y 25 pantallas de enseñanza; compilación JavaScript correcta. La ejecución Python del nuevo notebook, pruebas de navegador, ensayo docente y evaluación pedagógica todavía deben documentarse con evidencia independiente.
 
## Matriz de calificación provisional
| Dimensión | Peso | Estado |
|---|---:|---|
| Profundidad | 20% | No cumple extensión, desarrollo parcial |
| Actividad y autonomía | 20% | Actividades y transferencia implementadas; autonomía de estudiante no observada |
| Práctica reproducible | 20% | Código y datos disponibles; ejecución completa por validar |
| Alineación | 15% | Anclas A0–A8 diseñadas, falta prueba integral |
| Interpretación | 10% | Lectura y límites por pantalla; verificación pendiente |
| Visual y accesibilidad | 10% | Interfaz adaptativa, proyección real pendiente |
| Tiempo | 5% | 150 planificados, no medidos |
 
No se otorga 4,5/5 sin comprobaciones; no se autoriza iniciar S02. La política de revisión secuencial se aplica a todas las sesiones, incluida S14A opcional. Los borradores anteriores se conservan como referencia, no como sesiones aceptadas.
