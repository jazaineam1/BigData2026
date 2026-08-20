# AGENTS.md

Guía para producir material del curso de Big Data de la Universidad Central (Maestría en Analítica de Datos).

**Aquí solo hay principios durables.** Lo que cambia cada semana —qué sesión sigue, qué se anunció, qué está publicado, qué tema pertenece a qué sesión— vive en `.local-docente/Estado_del_curso.md`. Léelo antes de empezar cualquier sesión. Si al escribir una regla aquí necesitas nombrar una sesión, una fecha o un archivo concreto, estás escribiendo en el archivo equivocado.

Este archivo no reemplaza las instrucciones del usuario. Cuando el usuario contradiga algo de aquí, gana el usuario, y si la contradicción es durable, se actualiza este archivo.

---

## 1. Qué es una clase en este repositorio

Un cuaderno no es un contenedor de código: es una clase. Y una clase, aquí, es **una historia que resuelve un problema profesional**.

- La estructura base es de 180 minutos: aproximadamente la mitad de concepto dialogado y la mitad donde el estudiante hace. La segunda mitad es del estudiante, completa.
- **La modalidad es aprender haciendo.** La teoría prepara una decisión concreta que se materializa en el laboratorio. Si un bloque teórico no habilita ninguna acción posterior, sobra.
- **Empieza por una pregunta, una decisión o un problema, nunca por una definición**, y conserva el mismo caso a lo largo de toda la sesión. No organices una sesión como una sucesión de definiciones.
- Explica por qué aparece cada concepto, por qué en ese orden y qué problema del caso permite resolver.
- Separa capacidad de producto: primero la necesidad, después las herramientas reales que la atienden.
- Cuando haya un caso transversal, **lo que produce una sesión es la entrada de la siguiente**. No diseñes prácticas desechables.

**Cómo sabes que se logró:** puedes borrar un bloque y algo posterior se rompe. Si no se rompe nada, no había hilo: había inventario.

---

## 2. Anatomía de un cuaderno

1. Encabezado institucional y ficha de la sesión.
2. Objetivos y **producto**: qué entrega el estudiante al final.
3. Un mapa de bloques **sin relojes** (ver §7).
4. Por qué importa el tema, desde el caso.
5. Desarrollo por bloques, cada uno naciendo del anterior.
6. Laboratorio.
7. Cierre: recapitulación, la idea más importante, errores comunes y qué hace la próxima sesión con esto.

Cada tema importante lleva: motivo, definición, intuición en palabras, ejemplo manual pequeño, ejemplo aplicado, interpretación, error frecuente y una pregunta.

Si introduces una función nueva, agrega una mini ficha: para qué sirve, parámetros usados, qué devuelve, cómo se interpreta la salida y cuál es el error frecuente.

**Sobre la dosis.** El material se lee de noche, después de una jornada laboral. Un cuaderno de nueve mil palabras no cabe en una sesión: o lo lee o te escucha. Prefiere tablas a párrafos —una tabla de cinco filas suele decir lo que dicen quinientas palabras— y manda a `<details>` lo que sea profundización. **Acortar no es simplificar:** si al recortar desapareció el ejemplo manual o el límite del resultado, se perdió la clase y no la grasa.

---

## 3. Interpretación y límites

Esto es el activo intelectual del curso y lo único que un estudiante no obtiene de un tutorial ni de un asistente de IA. Si algo de este archivo hay que respetar sin negociar, es esta sección.

Después de cada salida relevante —tabla, gráfico, conteo, resumen— escribe:

- **Cómo se lee** esta salida.
- **Qué nos dice.**
- **Qué NO permite concluir todavía**, nombrando el dato que falta. "Faltan datos" no cuenta; "no tenemos el denominador de publicaciones por mes" sí.
- **Qué error común** aparece aquí.

Usa siempre esos mismos cuatro rótulos, en ese orden. Cuando cambian de nombre en cada celda, el estudiante tiene que leerlo todo para encontrar el que necesita; cuando son fijos, aprende a ir directo.

No dejes código mudo: si una celda existe para enseñar, el estudiante debe saber qué observar y por qué.

Un resultado descriptivo permite priorizar y describir patrones. **No permite por sí solo demostrar causalidad, fraude ni irregularidad**, y decirlo es parte del contenido, no una cautela legal.

---

## 4. Evaluación

### Una pregunta de opción múltiple ya no evalúa

Un cuestionario de definiciones lo responde en segundos cualquier asistente de IA. Sigue sirviendo para que el estudiante se autorregule mientras estudia; **no sirve para poner una nota**. Tratarlo como evaluación mide el acceso a internet, no el aprendizaje.

Lo que se califica debe anclarse en algo que solo existe si esa persona ejecutó. Cuatro anclajes; una entrega evaluable usa al menos dos:

- **Un resultado propio.** Un número o una salida producida por su ejecución, pegada con su valor. Distinto por estudiante si el ejercicio lo permite.
- **Una decisión con su alternativa descartada.** Qué eligió y qué **no**, y por qué. Una decisión sin alternativa nombrada es una preferencia.
- **Un límite concreto**, con el dato que falta.
- **Una traza:** el commit, el Pull Request o el archivo donde quedó, con autor y fecha.

**La prueba antes de usar un ítem:** escribe la respuesta que daría un asistente de IA sin contexto de la clase. Si obtiene el puntaje completo, el ítem no evalúa nada.

Cuidado con lo determinista: un resultado idéntico para todo el grupo circula por mensajería en cinco minutos. La resistencia no viene de que sea difícil, viene de que **sea distinto para cada uno**.

### Un quiz evalúa la sesión en la que se aplica

Un quiz que cobra sesiones anteriores rompe el momento en que el estudiante acaba de entender algo y se siente como un peaje. El quiz se apoya en **un ejercicio hecho en clase**: el estudiante entrega lo que produjo y las preguntas van sobre eso.

### Toda entrega evaluable tiene rúbrica antes de existir

La rúbrica va **en el cuaderno**, con niveles observables y no adjetivos. Nunca se pide un producto sin decir contra qué se corrige.

**Cómo sabes que se logró:** dos personas calificando el mismo trabajo con esa rúbrica llegarían a la misma nota.

### Preguntas de autoevaluación

No hay número obligatorio. La regla es de **cobertura**: cada bloque que el estudiante deba poder defender tiene al menos una pregunta, y ninguna se agrega para llegar a una cifra.

Una pregunta sirve cuando: se responde con lo que se acaba de ver en este cuaderno; las opciones incorrectas son errores que este grupo comete de verdad; y la retroalimentación de **cada** opción explica por qué y vuelve al caso.

Di explícitamente si son autoevaluación no calificable —pero no las presentes como opcionales en la primera pantalla, o el estudiante cansado sabrá exactamente qué saltar. Mejor: *"fállalas aquí, que sale gratis"*.

**Una pregunta vive en UNA sola celda.** No repitas el enunciado en Markdown y otra vez dentro del widget: en Colab el estudiante lo lee dos veces seguidas, con las cuatro opciones duplicadas una debajo de la otra. Duplicar contenido cuesta más que cualquier beneficio de leerlo fuera de Colab.

**Codifica lo que no debe leerse de un vistazo.** El plegado de Colab (`cellView: form`, `jupyter.source_hidden`) solo lo respetan Colab y JupyterLab: en GitHub el código queda crudo y con él la respuesta correcta. Guarda enunciado, opciones y respuesta codificados dentro de la celda del widget.

**Colab descarta el atributo `style` en las celdas Markdown.** El color no puede venir de CSS: solo se respeta HTML en la salida de `display(HTML(...))`. Si necesitas color en el cuerpo de la clase, que venga de una imagen — y que la imagen lleve contenido, no adorno.

**Cómo sabes que se logró:** abres el cuaderno en Colab y cada pregunta aparece una sola vez, con su caja y su botón.

---

## 5. Diseño de ejercicios

Un ejercicio enseña cuando el estudiante toma una decisión pequeña y ve la consecuencia. Ejecutar una celda ya escrita no es un ejercicio; escribir un cuaderno desde cero tampoco: es un examen.

Los escalones, en orden:

1. **Celda resuelta que se lee**, con su salida ya interpretada.
2. **Celda con un hueco nombrado** (`____`), con la instrucción de qué cambiar. **Un solo hueco por celda**, y nunca código comentado que haya que descomentar: una indentación rota consume el tiempo del bloque siguiente y no enseña nada.
3. **Celda con la pregunta y sin el código.**
4. **Pregunta que solo se responde mirando el resultado propio.**

Cada ejercicio declara: qué debe verse si salió bien, cuál es el error más probable y qué significa ese error. **Siempre hay una salida para quien se atasque** —el resultado esperado, plegado— para que nadie pierda el bloque siguiente por haberse quedado en el anterior.

Un laboratorio no es una matriz exhaustiva: es mejor una decisión bien entendida que doce casillas llenadas.

**Cómo sabes que se logró:** alguien que no estuvo en clase puede saber si su respuesta está bien sin preguntarle al docente.

---

## 6. Accesibilidad y condiciones reales de lectura

El material se lee de noche, proyectado, en portátiles con tema claro y con tema oscuro, después de once horas despierto.

- **El color nunca es la única señal.** Si algo es correcto o incorrecto, dilo también con palabras.
- **Todo bloque HTML generado fija color de texto y fondo juntos.** Fijar solo el fondo produce texto invisible en Colab con tema oscuro. Contraste mínimo 4.5:1, también dentro de los SVG.
- La retroalimentación que aparece al pulsar un botón va con `aria-live="polite"`.
- Toda imagen lleva `alt` con la **conclusión**, no con el nombre de la figura. Todo SVG lleva `<title>` y `<desc>`.
- Nada esencial depende de pasar el ratón por encima ni de una pantalla ancha.
- **Las citas en bloque significan una sola cosa cada una.** Si `>` se usa para instrucciones, adelantos, anécdotas y avisos por igual, deja de destacar. Usa etiquetas fijas: `**HAZ ESTO AHORA.**` (exige acción), `**OJO.**` (advertencia), `**PARA LLEVAR.**` (la idea), `**MÁS ADELANTE.**` (adelanto que se puede ignorar hoy).
- Un cuaderno que se consulta debe **repetir**: una hoja de trucos al final con lo que el estudiante necesitará mientras escribe consultas evita cuatro scrolls hacia arriba.

**Cómo sabes que se logró:** cambias Colab a tema oscuro y todo sigue legible.

---

## 7. Los tiempos viven en el libreto, no en el cuaderno

El reparto minuto a minuto es una herramienta del docente y vive en `.local-docente/`. **No va en el cuaderno del estudiante.**

Convierte la clase en un cronómetro, envejece en la primera contingencia y le dice al estudiante que va tarde justo cuando necesita detenerse a pensar.

El cuaderno sí lleva un **mapa sin relojes**: la secuencia de bloques, qué responde cada uno y qué producto deja. Cinco a ocho líneas.

**Cómo sabes que se logró:** el cuaderno no tiene ninguna columna de minutos; el libreto sí, y sus tiempos suman 180 incluyendo el receso.

---

## 8. Generadores, Colab y plataformas

### Generadores

- Antes de editar un `.ipynb`, busca si existe un generador en `utils/`. **Si existe, modifica el generador y regenera. No hagas cambios estructurales a mano en el JSON.**
- `utils/make_notebook.py` centraliza `md()`, `code()`, `sh()`, `save()`, `validate()`, `uce_header()`, `toc()` y `section_header()`.
- En celdas creadas con `code()`, evita triple comilla doble; usa `'''` para docstrings internos.
- No dejes celdas vacías, y valida que el `.ipynb` siga siendo JSON válido.
- **Cada sesión ejecutable tiene su validador** en `utils/`, para que "generador y cuaderno sincronizados" sea comprobable y no un acto de fe. Un validador comprueba estructura y hechos verificables, **no vocabulario**: prohibir palabras produce falsos fallos y contradice la idea de anunciar lo que viene.

### Colab

- Colab es la prueba final del entorno del estudiante. Una prueba local es útil pero no la sustituye.
- Oculta helpers, importaciones y HTML de interfaz con `cellView: form` y títulos `#@title` orientados al estudiante. **Mantén visible el código que el estudiante debe aprender o ejecutar.**
- Las celdas de carga deben ser **idempotentes**: repetibles sin duplicar ni fallar. El runtime se reinicia por inactividad, y eso pasa en el receso.
- Una celda que depende de una variable creada mucho antes debe poder recuperarla sola. Un `NameError` a mitad del laboratorio cuesta el bloque entero.

### Plataformas gestionadas

- Antes de escribir código para una plataforma gestionada, **verifica en su documentación vigente qué sigue disponible en el plan gratuito**, y anota la fecha de esa verificación en el generador. Lo que funcionaba hace un año puede haber desaparecido, y el estudiante se estrella en clase.
- Cuando evites una API por compatibilidad, **escríbelo en el cuaderno cerca de la celda**. Un workaround sin explicación se copia mal el semestre siguiente.
- No pidas tarjetas, claves ni cuentas de servicio para una sesión conceptual.

### Nivel del estudiante

- Usa el lenguaje y las herramientas ya introducidas. No adelantes abstracciones sin explicarlas.
- No escondas pasos importantes en funciones auxiliares si el objetivo es que el estudiante entienda el proceso.
- **Consulta el perfil real del grupo antes de elevar la complejidad**, y ofrece apoyos escalonados sin reducir la profundidad profesional del caso.

---

## 9. Diagramas y recursos visuales

- Un diagrama debe verse en Colab y en GitHub **sin depender de que el repositorio ya esté publicado**. Un `<img>` a `raw.githubusercontent.com` muestra un ícono roto hasta el push: sirve para material estable, no para el que se está construyendo. Un SVG embebido como `data:` URI funciona desde la primera ejecución.
- **El fuente debe quedar editable.** Si embebes SVG, guarda el SVG legible en `assets/diagrams/sNN/` y que el generador lo lea y lo codifique al construir. Un blob base64 pegado a mano es un diagrama que nadie podrá corregir nunca.
- Los diagramas deben estar al nivel conceptual del cuaderno: jerarquía clara, pasos, datos, decisiones y lo que cuesta cada opción. Evita flujos lineales demasiado simples.
- Después de cada diagrama explica cómo leerlo, cuál es la conclusión, qué limitación tiene y cómo conecta con lo siguiente.
- Conserva las imágenes existentes al reorganizar; si cambian de lugar, documenta la correspondencia.
- Cuando una guía dependa de una interfaz externa, usa capturas reales y actuales. Si no puedes obtenerlas, usa un esquema claramente identificado como conceptual; **no inventes una captura**.

---

## 10. Datos: procedencia y trato

- **Declara la procedencia de cada dato derivado:** qué script lo produjo, cuándo y de qué fuente. Publica el script.
- Si el dato se recolectó de un tercero, **di cómo**: una sola descarga del lado del docente, con pausa entre peticiones e identificación visible. Diez runtimes golpeando una fuente durante la clase es descortés y frágil. Que el estudiante lo lea es parte de la lección.
- Publica también los **criterios de selección** —filtros, palabras clave, recortes— para que el estudiante pueda auditar el criterio en vez de confiar en él. Un corpus construido buscando un término no puede usarse para contar ese término.
- Los datasets llevan contexto y diccionario cuando corresponde.

---

## 11. Replicabilidad: un cuaderno replicable o no está terminado

- **Córrelo completo en un entorno limpio**, de la primera celda a la última, sin editar nada. Anota cuánto tardó la celda más lenta: ese número decide si el bloque cabe en la clase.
- **Vuelve a ejecutar las celdas de carga.** Si una celda solo funciona la primera vez, quien se equivoque pierde la sesión.
- **Prueba el camino de respaldo de principio a fin**, con el mismo laboratorio. Un respaldo no ejecutado es una intención, no un respaldo.
- **Todo dato externo que el cuaderno descargue debe existir ya en `main`** antes de la clase. Comprueba cada URL con una petición real.
- Di qué pasa en el sistema operativo del grupo. Si el cuaderno solo corre en Colab, escríbelo: alguien va a perder una noche intentándolo en su máquina.
- **Si el entorno no te permitió validar algo, dilo con precisión.** No inventes validación.

**Cómo sabes que se logró:** puedes decir a qué hora corriste el cuaderno completo en limpio y qué devolvió.

---

## 12. Publicación

`index.html` es la única puerta por la que el estudiante llega al material. Una sesión que no aparece ahí no existe para el grupo.

- **Toda sesión que se planea o se construye entra al índice en el mismo cambio en que se genera su cuaderno.** No hay sesiones invisibles "en preparación".
- Una tarjeta está bien hecha cuando ocupa el lugar cronológico correcto, el título nombra la pregunta de la sesión y no la herramienta, la descripción dice qué sabrá hacer el estudiante, y el enlace apunta a un archivo que existe en `main`.
- Verifica el enlace con una petición real, nunca de memoria.
- Toca solo la tarjeta de la que se trate; las demás quedan intactas.
- Después de publicar, abre la página, pulsa la tarjeta y comprueba que el cuaderno abre. Un workflow verde no prueba que la página funcione.
- Si `actions/configure-pages` informa `Get Pages site failed: Not Found`, revisa que Pages esté habilitado para desplegar mediante Actions antes de cambiar código sin evidencia.

---

## 13. Límites que no se negocian

**Nunca publiques datos personales de estudiantes** —nombres, correos, roster, respuestas individuales de encuestas, entregas, notas ni reclamos—, **credenciales**, ni material docente privado. Las guías, libretos, soluciones y planes viven en `.local-docente/`, fuera de Git. Antes de terminar, confirma que no aparecen en `git status`.

Los datos de la encuesta diagnóstica se usan **solo de forma agregada** para planear ritmo, ejemplos y apoyos.

Los repositorios de estudiantes se crean o se habilitan únicamente cuando el docente comparte el acceso. No simules aceptaciones ni contribuciones en nombre de nadie.

---

## 14. Cómo trabajar con las correcciones del usuario

Las correcciones son decisiones de dirección. Aplícalas de inmediato y de forma local.

- "hazlo", "agrégalo", "amplía esto" → implementa en el artefacto, no propongas.
- "este cuaderno" → limita el alcance a ese cuaderno.
- "dímelo antes de incluirlo" → entrega mapa o propuesta; no edites todavía.
- "solo agrega esto al índice" → cambia solo esa entrada.
- "haz el push" → publica solo lo previsto; no arrastres trabajo sucio.

Si una corrección contradice una decisión previa, sigue la instrucción más reciente y deja el material consistente. Respeta los cambios locales del usuario que no hiciste.

---

## 15. Señales de que el material todavía no está listo

No son prohibiciones: son síntomas. Si aparece uno, hay trabajo pendiente.

- **El cuaderno se lee como una lista.** Borra un bloque: si nada posterior se rompe, no había hilo.
- **Hay una salida sin lectura.** Una tabla que el estudiante ve sin saber qué mirar enseña a pulsar Shift+Enter.
- **Una herramienta llegó antes que el problema que resuelve.** El estudiante memoriza sintaxis en vez de entender una decisión.
- **El cambio tocó más archivos de los que la tarea nombró.**
- **Se resumió algo esencial.**
- **El material afirma algo que su propia salida contradice.** Vuelve a mirar la tabla que acabas de imprimir antes de escribir la conclusión.

---

## 16. Las cinco preguntas que deciden si el material enseña

Las casillas de forma se pueden cumplir todas y aun así no enseñar nada. Antes de dar por lista una sesión:

1. **La historia.** ¿El estudiante puede contar en cinco frases y sin saltos qué pasó y por qué? Si tienes que decir "y también vimos…", hay dos clases metidas en una.
2. **La decisión.** ¿Qué decidió que no habría podido decidir antes de entrar? Si la respuesta es "ninguna, ejecutó celdas", es una demostración, no una clase.
3. **El límite.** ¿Puede nombrar algo que su propio resultado NO permite concluir, y qué dato le falta?
4. **El puente.** ¿La sesión siguiente empieza con algo que esta produjo, y esta empezó con algo que produjo la anterior?
5. **La grieta.** ¿Qué se rompe si alguien llega tarde, sin la tarea, o si la red falla a mitad del laboratorio? ¿Cuál es la versión reducida que sí cabe?

---

## 17. Cómo se actualiza este archivo

Aquí solo entra lo que seguirá siendo cierto dentro de diez sesiones.

- **Prueba de caducidad, obligatoria.** ¿Podría esta regla aplicarse a cualquier sesión sin cambiarle una palabra? Si no, va a `.local-docente/Estado_del_curso.md` o al plan de esa sesión.
- **Ninguna regla nombra una sesión, una fecha, un archivo concreto ni un estado del curso.** Si necesitas escribir "en la sesión 2" o "por ahora", estás en el archivo equivocado.
- **Cada regla se escribe en tres partes:** qué buscar, por qué importa y cómo se sabe que se logró. Una regla sin la tercera parte se convierte en folclore que nadie se atreve a tocar.
- **Prefiere el criterio al mecanismo.** "Que el diagrama se vea sin push" sobrevive; "que el SVG esté en tal carpeta" caduca y obliga a inventar rodeos peores.
- **Al agregar, borra.** Cada línea que un agente lee aquí es una línea que no dedica al material. Si el archivo crece, algo sobra.
- **Prohibir es el último recurso.** Una prohibición sin razón se obedece mal o se rodea. Escribe el criterio y el riesgo; el "no" se deduce solo. Reserva las prohibiciones absolutas para lo irreversible: datos personales, credenciales y material privado.

---

## 18. Ejemplos

### Buena transición

> Ya sabemos procesar datos en una sola máquina. Ahora necesitamos entender qué cambia cuando el problema deja de ser solo de memoria y se vuelve también de coordinación, fallos y observabilidad. Ahí aparece Spark.

### Buena interpretación

> Esta tabla no prueba causalidad. Solo resume cómo se distribuyen los registros. La categoría con mayor conteo merece exploración, pero todavía no sabemos si el patrón se debe a volumen real, sesgo de captura o datos faltantes.

### Buena mini ficha

```markdown
Función usada: `groupBy()`

- Para qué sirve: agrupa filas que comparten una o varias columnas.
- Parámetros usados: columna de agrupación.
- Qué devuelve: un objeto agrupado sobre el que se aplican agregaciones.
- Cómo interpretar la salida: cada fila final es un grupo con sus métricas.
- Error frecuente: agrupar antes de filtrar y hacer trabajo de más.
```

### Buen ítem de evaluación

Débil, porque una IA lo responde sin haber estado en clase:

> ¿Cuál de estas es una familia NoSQL? A. Documental B. Relacional C. Tabular D. Plana

Fuerte, porque depende de la ejecución y la decisión de esa persona:

> Elige una entidad de la tabla que produjo tu consulta. Di cuántas apariciones tuvo, si la pondrías o no en la fila de revisión, y qué dato te falta para estar seguro.

### Buena correspondencia al reorganizar

```markdown
| Cuaderno original | Nueva ubicación |
|---|---|
| Introducción a Spark | Sección 1: Por qué Spark importa |
| Ejemplo de lectura CSV | Sección 4: Lectura guiada de datos |
```
