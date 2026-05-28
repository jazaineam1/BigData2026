# AGENTS.md

Guia operativa para agentes que trabajen en este repositorio.

Este archivo no reemplaza las instrucciones del usuario. Sirve para mantener consistencia pedagogica, tecnica y de estilo cuando se creen, reparen, amplien o publiquen materiales del curso.

## 1. Proposito del repositorio

Este repositorio contiene materiales del curso de Big Data de la Universidad Central para la Maestria en Analitica de Datos. Su objetivo es construir una ruta guiada para aprender fundamentos, arquitectura, procesamiento distribuido, herramientas de nube, Spark, Dask, Databricks, Airflow, NoSQL, Git y laboratorios aplicados.

El repositorio combina:

- Cuadernos Jupyter para clase y practica.
- Un sitio `index.html` que organiza y publica la ruta de aprendizaje.
- Datasets de trabajo en `Datos/` y subcarpetas de cuadernos.
- Recursos visuales en `Images/` y `assets/`.
- Material de infraestructura en `infraestructura/` y `Airflow/`.
- Scripts generadores y utilidades en `utils/`.

La prioridad del proyecto es pedagogica: el material debe ayudar a estudiantes a entender por que una herramienta importa, como se conecta con lo visto antes y como se interpreta cada resultado.

## 2. Productos que se construyen aqui

Los productos principales son:

- Cuadernillos `.ipynb` con narrativa de clase guiada.
- Laboratorios aplicados con datos reales o simulados.
- Talleres evaluables o semi-guiados.
- Scripts que generan notebooks de forma reproducible.
- Paginas o entradas de navegacion en `index.html`.
- Modulos de infraestructura reproducible con Docker, Airflow, Dask, Spark y servicios relacionados.
- Tutoriales paso a paso en Markdown.

No trates un notebook como un simple contenedor de codigo. En este repositorio un cuaderno es una clase: debe tener introduccion, motivacion, explicacion, practica, preguntas, interpretacion y cierre.

## 3. Estilo esperado de escritura y comunicacion

Escribe en espanol claro, docente y directo. El tono debe sentirse como una clase guiada, no como apuntes sueltos ni como documentacion tecnica aislada.

Cada cuaderno debe:

- Explicar por que se estudia el tema.
- Conectar cada bloque con el bloque anterior.
- Presentar teoria breve pero suficiente antes de la practica.
- Incluir ejemplos pequenos antes de ejemplos aplicados.
- Interpretar los resultados despues de las salidas relevantes.
- Advertir errores comunes.
- Cerrar con recapitulacion y proxima sesion.

Despues de una tabla, grafico, conteo, `display`, resumen o salida de codigo, agrega una interpretacion docente cuando el resultado sea importante:

- Que nos dice este resultado.
- Como se lee esta tabla.
- Que conclusion descriptiva podemos sacar.
- Que no podemos concluir todavia.
- Que error comun podria aparecer aqui.

Evita dejar codigo "mudo". Si una celda existe para ensenar, el estudiante debe saber que observar y por que.

## 4. Reglas tecnicas importantes

### Notebooks y generadores

- Antes de editar un `.ipynb`, busca si existe un generador en `utils/`.
- Si el notebook se genera desde un script, modifica el generador y regenera el notebook. No hagas cambios estructurales a mano en el JSON del notebook.
- `utils/make_notebook.py` centraliza helpers como `md()`, `code()`, `save()`, `validate()`, `uce_header()`, `toc()` y `section_header()`.
- Para notebooks de Spark/Databricks ya modernizados, respeta los patrones existentes de `utils/build_session7_notebook.py` y `utils/make_9_databricks_serverless.py`.
- Valida que el `.ipynb` siga siendo JSON valido despues de cambios.
- No introduzcas celdas vacias.
- En celdas de codigo generadas con `code()`, evita triple comillas dobles dentro del string. Usa triple comillas simples para docstrings internos.

### Databricks, Spark y serverless

- Explica dentro del cuaderno cualquier adaptacion de compatibilidad. No dejes workarounds sin contexto.
- En Databricks moderno, no asumas que `Single Node`, `DBFS root`, `FileStore`, `sparkContext`, RDDs o Spark UI clasica estaran disponibles.
- Prefiere patrones compatibles con Databricks Free/Community moderno: `spark`, Spark SQL, DataFrames, Unity Catalog, tablas administradas, `saveAsTable(...)`, `display(...)`, Query Profile y datos publicos como `samples.nyctaxi.trips` cuando aplique.
- Evita `.rdd`, escrituras locales y rutas tipo `FileStore` si el cuaderno debe correr en serverless.
- Para dependencias en Databricks, prefiere `%pip` sobre `%sh pip install`.

###  Python y nivel del estudiante

- Usa el lenguaje y las herramientas ya introducidas en la sesion. No adelantes abstracciones sin explicarlas.

- No ocultes pasos importantes en funciones auxiliares si el objetivo es que el estudiante entienda el proceso.
- Si introduces una funcion nueva de R, Python, PySpark o SQL, agrega una mini ficha:
  - Funcion usada: `nombre_funcion()`
  - Para que sirve.
  - Parametros usados.
  - Que devuelve.
  - Como interpretar la salida.

### Sitio e indice

- `index.html` es la puerta de entrada del curso. Cambialo de forma quirurgica.
- Si el usuario pide agregar un cuaderno al indice, agrega solo ese cuaderno y conserva el resto de enlaces y textos funcionales.
- Mantén la ruta pedagogica visible: fundamentos, nube, arquitectura, procesamiento distribuido, herramientas y laboratorios.

### Infraestructura

- `infraestructura/` contiene guias, modulos, Docker, Spark, Dask, Git y proyecto final.
- `Airflow/` contiene DAGs, datos de staging, configuracion y logs. Evita modificar logs o artefactos generados salvo que la tarea lo requiera explicitamente.
- No mezcles cambios de infraestructura con cambios pedagogicos si el usuario no lo pidio.

## 5. Estructura esperada de archivos principales

### Cuadernillos de clase

Un cuaderno robusto debe seguir esta estructura base:

1. Encabezado institucional.
2. Alcance u objetivos de la sesion.
3. Agenda sugerida.
4. Por que importa el tema.
5. Desarrollo por bloques.
6. Teoria breve pero suficiente.
7. Ejemplo simple.
8. Ejemplo aplicado.
9. Pregunta interactiva.
10. Comentario docente o interpretacion.
11. Aplicacion en R, Python, SQL, Spark o la herramienta objetivo.
12. Ejercicios guiados.
13. Cierre de sesion.

Cada tema importante debe incluir:

- Definicion formal.
- Intuicion en palabras.
- Ejemplo pequeno manual.
- Ejemplo aplicado a datos o contexto real.
- Interpretacion del resultado.
- Error comun o advertencia.
- Pregunta interactiva con el estilo establecido.

En sesiones aplicadas, usa bloques como:

- Caso 1.
- Caso 2.
- Aplicacion de la teoria al caso real.
- Conclusion descriptiva guiada.

Para sesiones mas teoricas, deja el laboratorio grande al final. Durante la clase puede aparecer codigo, pero debe estar muy guiado.

### Preguntas interactivas

Las preguntas deben distribuirse a lo largo del cuaderno, no solo al final.

- Sesion corta: minimo 8 preguntas.
- Sesion robusta: 10 a 16 preguntas.

El formato esperado, inspirado en la sesion 7, es:

- Caja azul.
- Titulo tipo: `Pregunta 1 de 8 -- Tema`.
- Contexto en caja amarilla.
- Pregunta clara.
- 4 opciones.
- Boton `Verificar respuesta`.
- Retroalimentacion verde si es correcta.
- Retroalimentacion roja si es incorrecta.

En Databricks/Python, puede usarse HTML con `displayHTML` y fallback a `IPython.display`. En R, puede usarse un patron compatible con `IRdisplay` si la sesion lo permite.

### Cierre de sesion

El cierre debe incluir:

- Recapitulacion.
- Idea mas importante.
- Errores comunes.
- Proxima sesion.

### Recursos y referencias

Si hay recursos externos importantes, incluyelos en el cuerpo de la clase y tambien en referencias:

- Lecturas.
- Simuladores.
- PDFs.
- Articulos historicos.
- Documentacion oficial.
- Libros base.

## 6. Que hacer y que evitar

### Haz

- Lee primero la estructura del repo y el archivo objetivo.
- Conserva el contenido tematico valioso de cuadernos de referencia.
- Agrega mejoras sin borrar ejemplos importantes.
- Incluye una seccion de correspondencia si reorganizas un cuaderno basado en otro.
- Explica dentro del notebook los cambios tecnicos que afecten la experiencia del estudiante.
- Usa ejemplos manuales pequenos antes de ejemplos con datos.
- Agrega diccionarios de datos cuando presentes datasets.
- Mantén el producto final claramente identificable: que entrega el estudiante al final de la sesion.
- Respeta cambios locales existentes que no hiciste.

### Evita

- No convertir el cuaderno en una lista de bullets sin narrativa.
- No reemplazar contenido esencial por un resumen corto.
- No agregar codigo sin interpretacion cuando el resultado tenga valor docente.
- No introducir herramientas nuevas sin explicar por que aparecen.
- No editar mas archivos de los necesarios.
- No tocar `index.html` de forma amplia si solo se pidio agregar o corregir una entrada.
- No asumir que el entorno de Databricks antiguo sigue igual.
- No borrar logs, datos, notebooks copiados o cambios locales sin instruccion explicita.

## 7. Criterios de calidad antes de terminar una tarea

Antes de finalizar, revisa:

- El cuaderno se siente como una clase guiada.
- Hay objetivos, agenda, motivacion y cierre.
- Cada bloque se conecta con el anterior.
- Los ejemplos van de simple a aplicado.
- Las salidas relevantes tienen interpretacion docente.
- Hay suficientes preguntas interactivas y cubren todos los bloques.
- Las preguntas siguen el formato visual y funcional esperado.
- Las funciones nuevas estan explicadas con mini ficha.
- Los datasets tienen contexto y diccionario cuando corresponde.
- El notebook sigue siendo JSON valido.
- Si se uso generador, el generador y el notebook quedaron sincronizados.
- Si se modifico `index.html`, el cambio fue minimo y los enlaces siguen siendo coherentes.
- Si no se pudo validar algo por restricciones del entorno, dilo claramente.

Comandos utiles segun el caso:

```powershell
git status --short
rg --files
rg -n "texto_a_buscar"
python utils/make_9_databricks_serverless.py
python utils/build_session7_notebook.py
```

Si `python` falla por permisos en este entorno, no inventes validacion. Reporta la limitacion y usa otra verificacion razonable, como inspeccion JSON con la herramienta disponible o lectura estructural del archivo.

## 8. Como manejar correcciones del usuario

Las correcciones del usuario son decisiones de direccion del proyecto. Aplicalas de forma inmediata y local.

Ejemplos de interpretacion:

- "hazlo", "agregalo" o "amplia esto": implementa en el artefacto, no solo propongas.
- "este cuaderno": limita el alcance al cuaderno mencionado.
- "dimelo antes de incluirlo en el cuaderno": primero entrega mapa, ubicacion o propuesta; no edites todavia.
- "no uses function" o "solo hemos usado R base": simplifica el codigo al nivel enseñado.
- "no explicas en el cuadernillo lo que haces": agrega la explicacion dentro del notebook, cerca del codigo afectado.
- "solo quiero que agregues en el index este cuaderno": cambia solo la entrada necesaria en `index.html`.
- "haz el push": publica solo los cambios previstos y evita incluir trabajo sucio no relacionado.

Si una correccion contradice una decision previa, sigue la instruccion mas reciente del usuario y deja el material consistente.

## 9. Como actualizar este AGENTS.md de forma iterativa

Actualiza este archivo cuando aparezca una regla durable del proyecto, no por preferencias momentaneas.

Al actualizar:

- Integra la regla en la seccion existente mas cercana.
- Si una regla se repite, reorganizala sin eliminar su sentido.
- Convierte frases ambiguas en acciones verificables.
- Agrega ejemplos concretos si ayudan a futuros agentes.
- No conviertas este archivo en historial de cambios.
- No incluyas decisiones temporales que solo aplican a una tarea puntual.

Una buena actualizacion responde: que debe hacer el proximo agente, cuando debe hacerlo y como sabra que lo hizo bien.

## 10. Ejemplos concretos de buenas practicas

### Buena transicion docente

Antes de pasar de Pandas o Dask a Spark:

> Ya sabemos procesar datos en una sola maquina y tambien distribuir algunas tareas con Dask. Ahora necesitamos entender que cambia cuando el problema deja de ser solo de memoria y se vuelve tambien de coordinacion, almacenamiento, fallos y observabilidad. Ahi aparece Spark.

### Buena interpretacion despues de una salida

Despues de un `groupBy`:

> Esta tabla no prueba causalidad. Solo resume como se distribuyen los registros por categoria. La categoria con mayor conteo merece exploracion, pero todavia no sabemos si ese patron se debe a volumen real, sesgo de captura o datos faltantes.

### Buena mini ficha de funcion

```markdown
Funcion usada: `groupBy()`

- Para que sirve: agrupa filas que comparten una o varias columnas.
- Parametros usados: columna de agrupacion.
- Que devuelve: un objeto agrupado sobre el que se aplican agregaciones.
- Como interpretar la salida: cada fila final representa un grupo y sus metricas resumidas.
```

### Buena pregunta interactiva

```markdown
Pregunta 3 de 12 -- Lazy evaluation

Contexto. Spark no ejecuta todas las transformaciones inmediatamente. Primero construye un plan y luego lo ejecuta cuando aparece una accion.

Pregunta. Cual operacion obliga a Spark a ejecutar el plan?

A. `select()`
B. `filter()`
C. `count()`
D. `withColumn()`
```

La version final debe presentarse en caja azul, con contexto amarillo, cuatro opciones, boton de verificacion y retroalimentacion verde o roja.

### Buena correspondencia al reorganizar

```markdown
## Correspondencia con el cuaderno de referencia

| Cuaderno original | Nueva ubicacion |
|---|---|
| Introduccion a Spark | Seccion 1: Por que Spark importa |
| Ejemplo de lectura CSV | Seccion 4: Lectura guiada de datos |
| Taller final | Seccion 9: Laboratorio aplicado |
```

Esta tabla permite mejorar la estructura sin perder contenido esencial.

### Buena regla para Databricks moderno

Si una celda evita `FileStore` o `.rdd`, explica cerca:

> En Databricks Free/Community moderno algunas rutas heredadas y APIs de bajo nivel pueden no estar disponibles. Por eso trabajamos con tablas administradas y DataFrames: el objetivo de la sesion es aprender el flujo que el estudiante puede ejecutar en la plataforma actual.

### Buena actualizacion de `index.html`

Si se agrega una nueva sesion:

- Ubica la tarjeta en la secuencia pedagogica correcta.
- Usa titulo, categoria y descripcion breve.
- Enlaza al notebook correcto en GitHub/Colab si ese es el patron actual.
- No reordenas ni reescribes tarjetas ajenas salvo instruccion explicita.
