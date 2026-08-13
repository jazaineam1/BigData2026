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
- Libretos docentes privados cuando el usuario los solicite.

No trates un notebook como un simple contenedor de codigo. En este repositorio un cuaderno es una clase: debe tener introduccion, motivacion, explicacion, practica, preguntas, interpretacion y cierre.

### Libretos docentes privados

- Un libreto docente debe ser mas amplio que el cuaderno del estudiante. Incluye proposito, tiempos, teoria completa, transiciones, preguntas que puede formular el docente, respuestas esperadas, errores previsibles, demostraciones, interpretacion de resultados, contingencias y criterios de evaluacion.
- Distingue con claridad que debe decir o mostrar el docente, que debe hacer el estudiante y que evidencia debe observarse antes de avanzar.
- Si el usuario indica que el libreto no debe subirse, guardalo en `.local-docente/` o en otra ruta excluida y confirma que no aparezca en `git status`.
- No conviertas el libreto privado en una celda extensa del notebook salvo que el usuario lo pida; el cuaderno debe conservar una carga cognitiva adecuada para el estudiante.

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

### Hilo conductor y profundidad conceptual

- No organices una sesion como una sucesion de definiciones. Comienza por una pregunta, decision o problema profesional y conserva el mismo caso a lo largo de la teoria y la practica.
- Explica por que aparece cada concepto, por que se presenta en ese orden y que problema del caso permite resolver.
- Cuando una cadena tecnologica tenga dependencias, hazlas explicitas. Por ejemplo: el proceso produce datos, OLTP registra la operacion, ETL o ELT mueve y transforma la evidencia, el Data Warehouse conserva historia, el Data Mart enfoca un dominio y OLAP permite comparar.
- No menciones ETL y ELT como sinonimos. Compara orden, lugar de transformacion, ventajas, riesgos, controles y situaciones en las que conviene cada enfoque.
- Muestra un flujo empresarial completo: actor, entrada, actividad, dato producido, validacion, salida, problema actual, herramienta posible, KPI y decision soportada.
- Separa capacidad de producto. Primero explica la necesidad empresarial o tecnica y despues presenta herramientas reales equivalentes entre proveedores.
- Una definicion importante debe incluir motivo, definicion formal, intuicion, ejemplo manual, aplicacion real, herramientas, interpretacion, limitacion y error frecuente.

## 4. Reglas tecnicas importantes

### Notebooks y generadores

- Antes de editar un `.ipynb`, busca si existe un generador en `utils/`.
- Si el notebook se genera desde un script, modifica el generador y regenera el notebook. No hagas cambios estructurales a mano en el JSON del notebook.
- `utils/make_notebook.py` centraliza helpers como `md()`, `code()`, `save()`, `validate()`, `uce_header()`, `toc()` y `section_header()`.
- Para notebooks de Spark/Databricks ya modernizados, respeta los patrones existentes de `utils/build_session7_notebook.py` y `utils/make_9_databricks_serverless.py`.
- Valida que el `.ipynb` siga siendo JSON valido despues de cambios.
- No introduzcas celdas vacias.
- En celdas de codigo generadas con `code()`, evita triple comillas dobles dentro del string. Usa triple comillas simples para docstrings internos.

### Google Colab y visibilidad del codigo

- Para los notebooks ejecutables de este curso, Google Colab es la prueba final del entorno del estudiante. Una prueba local es util, pero no sustituye la validacion visual y funcional en Colab.
- Agrega al inicio una instruccion clara para ejecutar las celdas necesarias o usar `Ejecutar todo`.
- Oculta en Colab helpers, importaciones, HTML de interfaz, respuestas y codigo que genera preguntas. Usa metadatos como `cellView: form`, `colab.formView`, `jupyter.source_hidden` y titulos `#@title` comprensibles.
- La pregunta, el contexto, las cuatro opciones, el boton y la retroalimentacion deben permanecer visibles; el estudiante no necesita ver la implementacion ni la respuesta codificada.
- Mantén visibles los comandos y el codigo que el estudiante debe aprender o ejecutar, como Git, el perfilador y el validador. No ocultes un paso conceptual importante dentro de una funcion auxiliar.
- Comprueba en Colab que plegado, imagenes, botones y retroalimentacion funcionan. Si el artefacto aun no esta publicado y no puede abrirse en Colab, reporta con precision que solo se completo la validacion local.

### Databricks, Spark y serverless

- Explica dentro del cuaderno cualquier adaptacion de compatibilidad. No dejes workarounds sin contexto.
- En Databricks moderno, no asumas que `Single Node`, `DBFS root`, `FileStore`, `sparkContext`, RDDs o Spark UI clasica estaran disponibles.
- Prefiere patrones compatibles con Databricks Free/Community moderno: `spark`, Spark SQL, DataFrames, Unity Catalog, tablas administradas, `saveAsTable(...)`, `display(...)`, Query Profile y datos publicos como `samples.nyctaxi.trips` cuando aplique.
- Evita `.rdd`, escrituras locales y rutas tipo `FileStore` si el cuaderno debe correr en serverless.
- Para dependencias en Databricks, prefiere `%pip` sobre `%sh pip install`.

### Python y nivel del estudiante

- Usa el lenguaje y las herramientas ya introducidas en la sesion. No adelantes abstracciones sin explicarlas.

- No ocultes pasos importantes en funciones auxiliares si el objetivo es que el estudiante entienda el proceso.
- Si introduces una funcion nueva de R, Python, PySpark o SQL, agrega una mini ficha:
  - Funcion usada: `nombre_funcion()`
  - Para que sirve.
  - Parametros usados.
  - Que devuelve.
  - Como interpretar la salida.

### Recursos visuales, diagramas y capturas

- No elimines imagenes existentes por simplificar un cuaderno. Conserva los recursos originales y, si reorganizas, documenta su nueva ubicacion en una tabla de correspondencia.
- Los diagramas docentes deben estar al nivel conceptual del cuaderno: jerarquia clara, carriles o dominios cuando correspondan, pasos numerados, datos, decisiones, retrabajo, controles y KPI. Evita flujos lineales demasiado simples o conectores ambiguos.
- Para diagramas complejos visibles en el cuaderno, conserva el fuente reproducible fuera del `.ipynb` y genera SVG y PNG legibles. Mermaid puede seguir usandose como fuente o como artefacto que el estudiante deba versionar en GitHub, pero no debe imponerse como visual final si reduce la calidad pedagogica.
- Usa una paleta consistente e institucional, tipografia legible, texto alternativo y dimensiones que funcionen tanto en GitHub como en Colab.
- Despues de cada diagrama explica: como leerlo, cual es la conclusion, que limitacion tiene y como conecta con el bloque siguiente.
- Cuando una guia dependa de la interfaz de GitHub, Codespaces, Pull Requests o Actions, usa capturas reales y actuales obtenidas con una sesion autorizada. No expongas roster, correos, tokens, invitaciones, repositorios privados ni otra informacion sensible.
- Acompana cada captura con la accion, el resultado esperado y la solucion al error mas probable. Si no puede obtenerse una captura real, usa un esquema claramente identificado como conceptual; no inventes una captura.

### Sitio e indice

- `index.html` es la puerta de entrada del curso. Cambialo de forma quirurgica.
- Si el usuario pide agregar un cuaderno al indice, agrega solo ese cuaderno y conserva el resto de enlaces y textos funcionales.
- Mantén la ruta pedagogica visible: fundamentos, nube, arquitectura, procesamiento distribuido, herramientas y laboratorios.
- Durante la preparacion actual del periodo 2026-2, el indice publico debe mostrar solamente las sesiones 1 y 2. No presentes la sesion 2 como una fusion curricular ni publiques tarjetas posteriores hasta que el usuario lo solicite.
- Despues de un cambio destinado a publicacion, verifica enlaces, imagenes, el workflow de GitHub Pages y una respuesta HTTP satisfactoria. Un workflow verde no basta si la pagina no abre.
- Si `actions/configure-pages` informa `Get Pages site failed: Not Found`, revisa que Pages este habilitado y configurado para desplegar mediante GitHub Actions antes de cambiar codigo sin evidencia.

### Infraestructura

- `infraestructura/` contiene guias, modulos, Docker, Spark, Dask, Git y proyecto final.
- `Airflow/` contiene DAGs, datos de staging, configuracion y logs. Evita modificar logs o artefactos generados salvo que la tarea lo requiera explicitamente.
- No mezcles cambios de infraestructura con cambios pedagogicos si el usuario no lo pidio.
- No solicites tarjetas, claves JSON, cuentas de servicio ni roles amplios de GCP para una sesion conceptual. Las capturas historicas de nube deben incluir fecha, contexto y advertencia de vigencia.
- En la sesion 2 ampliada, GCP es solo una referencia visual y conceptual; omite anexos de activacion de cuentas, credenciales, videos y consultas historicas que no apoyen el hilo principal.
- Docker y la implementacion asociada quedan reservados para una sesion tecnica posterior o para el momento que el usuario confirme. No adelantes cambios en otro cuaderno, tarjeta o infraestructura solo porque se mencione como continuidad.

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

En Colab, cada celda de pregunta debe tener un titulo de formulario orientado al estudiante, por ejemplo `Activar pregunta 3 -- OLTP y OLAP`. La retroalimentacion debe explicar por que la opcion elegida es correcta o incorrecta y conectarla con el caso conductor; no basta con mostrar `Correcto` o `Incorrecto`.

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
- Revisa el contexto real del grupo antes de elevar la complejidad y ofrece apoyos escalonados para estudiantes con menos experiencia, sin reducir la profundidad profesional del caso.

### Evita

- No convertir el cuaderno en una lista de bullets sin narrativa.
- No reemplazar contenido esencial por un resumen corto.
- No agregar codigo sin interpretacion cuando el resultado tenga valor docente.
- No introducir herramientas nuevas sin explicar por que aparecen.
- No editar mas archivos de los necesarios.
- No tocar `index.html` de forma amplia si solo se pidio agregar o corregir una entrada.
- No asumir que el entorno de Databricks antiguo sigue igual.
- No borrar logs, datos, notebooks copiados o cambios locales sin instruccion explicita.
- No publiques datos personales, respuestas individuales de encuestas, roster, correos o documentos docentes privados.

## 7. Organizacion vigente del curso 2026-2

### Dinamica de las sesiones

- La estructura base es de 180 minutos: 90 minutos de explicacion de conceptos y herramientas y 90 minutos de tareas o ejercicios en un entorno cercano a la realidad.
- La modalidad es aprender haciendo. La teoria debe preparar una decision o accion concreta que se materializa durante el laboratorio.
- Cuando haya un caso transversal, los productos de una sesion deben servir como entrada de la siguiente; no diseñes practicas desechables sin conexion con el proyecto.

### Contexto pedagogico del grupo

- Existe una encuesta diagnostica local en `otros/` con contexto de parte del grupo. Puede usarse para planear explicaciones, apoyos, ejemplos y ritmo.
- Trata ese archivo como insumo docente privado. Analiza resultados de manera agregada y no copies al cuaderno nombres, correos, respuestas individuales ni datos identificables.
- No asumas dominio previo de Bash, Git, nube, contenedores o arquitectura. Explica cada comando, el estado esperado y el error mas probable, pero conserva extensiones opcionales para quien avance mas rapido.

### Sesion 2 ampliada: historia y alcance confirmado

- La historia conductora es Compras Claras: una analista necesita priorizar revision humana de procesos contractuales usando evidencia de SECOP.
- El orden conceptual confirmado es: decision y KPI; motivaciones y preparacion para adoptar; proceso AS-IS y BPM; roles y relevos; caso de uso; BI tradicional frente a capacidades Big Data; arquitectura empresarial; ciclo analitico NIST; capacidades y herramientas; Git/GitHub como puente para conversar sobre los artefactos.
- En la sesion 2, limita el contenido estudiantil a siete responsabilidades esenciales: dueno del proceso, arquitecto empresarial, arquitecto de datos, data steward, ingeniero de datos, analista BI/datos y cientifico de datos. El experto de dominio y el usuario de la evidencia son actores del proceso; seguridad, privacidad, calidad, observabilidad y costos son controles transversales. No uses RACI ni catalogos extensos de cargos en el cuaderno, laboratorio, rubrica o glosario.
- Explica estos siete roles mediante decisiones, artefactos y relevos concretos. Usa un cambio semantico de datos, como `fecha_de_inicio`, para mostrar la cadena definicion, diseno, implementacion, validacion e interpretacion. El cientifico de datos aparece solo cuando una pregunta predictiva o experimental y una linea base justifican su participacion.
- Explica en cada actividad contractual actor, entrada, tarea, dato, validacion, salida, problema, herramienta y KPI.
- Conserva `Images/2.1.png`, `Images/GCP/5.png`, `Images/GCP/6.png` y las imagenes originales. No modifiques `Cuadernos/2_BigData.ipynb` cuando se use solo como fuente historica.
- El caso permite priorizar revision y describir patrones; no permite por si solo demostrar causalidad, fraude o irregularidad.
- Integra casos de uso y BI tradicional frente a Big Data dentro de la historia, sin explicar al estudiante la reorganizacion curricular. No incluye presentaciones relampago de estudiantes; el cierre usa un ticket individual o de pareja.
- OLTP, OLAP, Data Marts, Data Warehouses, Data Lakes y ETL pertenecen a la sesion 4. En la sesion 2 solo pueden nombrarse como adelanto curricular, sin definicion formal, comparacion, pregunta evaluable ni implementacion.
- La proxima sesion anunciada es la sesion 4. Conserva los cuadernos historicos de la sesion 3, pero no los publiques como una tarjeta separada.

### Git como puente de colaboracion del proyecto semestral

- Git no es un ejercicio independiente ni una obligacion presentada fuera del hilo. Introducelo cuando los roles necesiten compartir, revisar, corregir y conservar decisiones. El repositorio propio de cada equipo puede sostener el proyecto semestral y crecer semana a semana.
- Usa un solo repositorio por equipo durante el semestre. No crees un repositorio nuevo por taller ni pidas copias finales por correo cuando el flujo acordado sea Git.
- `main` representa la version integrada; una rama como `hito/sNN-tema` puede aislar una propuesta; el Pull Request abre revision y CI; las correcciones conservan la respuesta a objeciones; el merge deja una base posible para la siguiente semana. Presenta este flujo como una buena practica de colaboracion, no como finalidad de aprendizaje.
- Explica que un commit sigue siendo local hasta hacer push. El push actualiza la rama remota y el Pull Request, pero no equivale por si solo a una entrega aprobada.
- Los talleres e hitos, salvo instruccion contraria, son incrementos del mismo proyecto. La retroalimentacion debe atenderse mediante cambios trazables que permanezcan en el historial.
- La cantidad de commits, pushes o lineas no determina la nota. Usa el historial para trazabilidad individual y colectiva, y evalua contenido, ejecucion, interpretacion, limites, revision y comprension.
- El cuaderno debe explicar este modelo desde las necesidades de los roles. Git no tiene criterio independiente en la rubrica de la sesion 2, no hay examen de comandos y el aprendizaje conceptual no depende de instalar Git. La conversacion puede servir como evidencia, pero nunca como contador automatico.

- En la sesion 2, la ruta principal funciona desde GitHub.com: editar un archivo, proponerlo en `hito/s02-negocio`, abrir o continuar un Pull Request, comentar una decision y observar una correccion. Working tree, staging y terminal quedan como profundizacion opcional.

### Repositorios gratuitos y mantenibles

- No dependas de GitHub Classroom, Copilot, organizaciones con facturacion ni servicios pagos para ejecutar el curso.
- La alternativa vigente es GitHub Free con repositorios privados creados por el docente y estudiantes agregados como colaboradores. No publiques las URL privadas.
- El curso tiene actualmente 12 estudiantes y se planean equipos de maximo dos personas, por lo que se esperan seis repositorios si la matricula se mantiene. Los grupos aun no estan definidos: no asignes personas ni crees repositorios finales en su nombre hasta recibir la composicion de los equipos.
- Cuando los grupos esten confirmados, prepara un repositorio por equipo a partir de una plantilla semestral comun. Los repositorios deben aceptar actualizaciones semanales sin borrar el trabajo del grupo.
- Mantén una estructura estable, por ejemplo `README.md`, `docs/`, `data/`, `scripts/`, `resultados/`, `.github/` y carpetas de hitos cuando sean necesarias. Agrega contenido mediante cambios pequenos y evita reemplazar el repositorio completo.
- La plantilla debe incluir validador local, CI que no dependa de una API viva, plantilla de Pull Request, datos pequenos reproducibles y documentacion para entorno local gratuito. Codespaces puede ofrecerse como opcion sujeta a cuota personal, no como requisito.
- No uses forks como estrategia principal de evaluacion: complican privacidad, permisos y sincronizacion. Prefiere repositorios de equipo creados desde una plantilla comun y mantenidos por sus integrantes.
- Distribuye actualizaciones semanales de manera aditiva mediante una version de la plantilla, una rama de referencia o un Pull Request docente. Nunca reemplaces `main` ni borres cambios del equipo para sincronizar contenido nuevo.
- La ruta gratuita principal es Git y Python locales. Si un estudiante tiene cuota, puede usar Codespaces; `github.dev` sirve como contingencia para editar y abrir un PR, pero no sustituye la ejecucion de Python.
- Si la API SECOP falla, usa una muestra local; si Actions se demora, acepta temporalmente el validador local; si Codespaces no tiene cuota, trabaja localmente o comparte un entorno por pareja con coautoria explicada.
- Los repositorios reales de estudiantes se crean o habilitan solo cuando el docente comparte el acceso; no simules aceptaciones ni contribuciones en nombre de estudiantes.

### Evaluacion, tareas y visibilidad

- Diferencia la rubrica de un hito de la ponderacion oficial del curso. No publiques porcentajes, fechas o reglas definitivas hasta confirmarlas con el documento oficial y el docente.
- El mecanismo esperado es acumulativo: taller o hito en rama y Pull Request; retroalimentacion en comentarios; correccion mediante nuevos commits; integracion a `main`; proyecto final construido sobre esa evolucion.
- Para evidencia individual pueden revisarse commits atribuibles, comentarios y explicaciones, pero nunca usar el volumen mecanico como calificacion automatica.
- No publiques tareas, invitaciones o enlaces de repositorios a estudiantes hasta que el usuario indique que estan listos para envio.
- Las guias docentes, libretos extensos, soluciones, credenciales, enlaces privados y materiales de preparacion deben permanecer fuera de Git, preferiblemente en `.local-docente/`, salvo instruccion explicita de publicarlos.

## 8. Criterios de calidad antes de terminar una tarea

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
- Las preguntas de Colab tienen interfaz visible y codigo plegado.
- Los diagramas son legibles, reproducibles y estan acompanados por lectura, conclusion, limitacion y conexion.
- Las imagenes originales y los cambios locales del usuario se conservaron.
- Si el material usa Git como entrega, queda claro que el repositorio es acumulativo y que push, PR, revision y merge cumplen funciones distintas.
- La auditoria pedagogica automatica se complemento con lectura manual del hilo narrativo; no presentes el puntaje heuristico como unica evidencia de calidad.

Comandos utiles segun el caso:

```powershell
git status --short
rg --files
rg -n "texto_a_buscar"
python utils/make_9_databricks_serverless.py
python utils/build_session7_notebook.py
python utils/build_session2_notebook.py
```

Si `python` falla por permisos en este entorno, no inventes validacion. Reporta la limitacion y usa otra verificacion razonable, como inspeccion JSON con la herramienta disponible o lectura estructural del archivo.

## 9. Como manejar correcciones del usuario

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

## 10. Como actualizar este AGENTS.md de forma iterativa

Actualiza este archivo cuando aparezca una regla durable del proyecto, no por preferencias momentaneas.

Al actualizar:

- Integra la regla en la seccion existente mas cercana.
- Si una regla se repite, reorganizala sin eliminar su sentido.
- Convierte frases ambiguas en acciones verificables.
- Agrega ejemplos concretos si ayudan a futuros agentes.
- No conviertas este archivo en historial de cambios.
- No incluyas decisiones temporales que solo aplican a una tarea puntual.

Una buena actualizacion responde: que debe hacer el proximo agente, cuando debe hacerlo y como sabra que lo hizo bien.

## 11. Ejemplos concretos de buenas practicas

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
