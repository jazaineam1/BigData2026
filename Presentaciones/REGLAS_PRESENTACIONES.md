# Reglas durables para presentaciones del curso Big Data

Estas reglas toman como referencia canónica la arquitectura de **S07 · Elasticsearch Search Lab**.

## 1. Regla de recursos

Por defecto, una sesión tiene **dos recursos visibles para el estudiante**:

1. **Presentación interactiva**.
2. **Cuaderno ejecutable**.

El laboratorio conceptual, simuladores, preguntas, decisiones y controles de comprensión viven **dentro de la presentación**. No crear una tercera página de “laboratorio” salvo que exista una razón pedagógica excepcional y explícita.

## 2. Regla terminológica

**Ningún término técnico nuevo puede utilizarse como requisito previo antes de haber sido definido.**

Una definición núcleo debe incluir, cuando aplique:

- **qué es**;
- **para qué sirve**;
- **ejemplo mínimo**;
- **cómo observarlo, ejecutarlo o medirlo**;
- **error frecuente, límite o confusión habitual**.

Si una palabra aparece por primera vez dentro de un bloque de código, la definición debe aparecer **antes del código**.

No asumir que el estudiante conoce acrónimos. Escribir primero el nombre completo y después el acrónimo.

## 3. Secuencia pedagógica

La secuencia preferida es:

```text
problema / decisión
  ↓
definición
  ↓
ejemplo mínimo
  ↓
herramienta o demostración
  ↓
desafío embebido
  ↓
primer intento
  ↓
pista / explicación
  ↓
reintento
  ↓
dominio
  ↓
cuaderno cuando toca automatizar o trabajar con datos reales
```

La presentación no debe ser una lista de definiciones. Cada concepto debe resolver una necesidad visible.

## 4. Desafíos D1–D8

Cuando una sesión use desafíos en vivo:

- deben vivir en diapositivas;
- la respuesta correcta **no se publica en HTML ni JavaScript**;
- el backend valida la respuesta;
- **primer intento** y **dominio** se guardan por separado;
- fallar puede habilitar explicación y reintento;
- el primer intento no se sobrescribe por acertar después;
- el dominio sí puede mejorar tras la retroalimentación.

Estas señales son **formativas** salvo que la sesión declare explícitamente lo contrario.

## 5. Herramientas interactivas

Si un concepto abstracto puede entenderse mejor manipulándolo, la presentación debe incluir una herramienta simple.

Ejemplos:

- tokenizer → filtros → tokens;
- vectores → similitud;
- consulta → dos rankings;
- parámetros → consulta generada;
- evidencia → artefacto estructurado.

La herramienta debe mostrar **qué cambia** cuando el estudiante cambia una entrada. No debe ser decoración.

## 6. Teacher Wall

Cuando exista una dinámica en vivo, el control docente debe poder abrirse desde la **misma presentación**, preferiblemente mediante:

```text
?wall=docente
```

El Wall debe mostrar diagnóstico útil para decidir si volver a explicar, no solamente actividad o tiempo.

Si la sesión usa identidad LMS, reutilizarla; no duplicar credenciales.

## 7. Reinicio

Toda dinámica compartida que pueda repetirse en clase debe tener un mecanismo docente de reinicio protegido.

El reinicio:

- requiere confirmación explícita;
- indica exactamente qué datos borra;
- no debe borrar calificaciones oficiales salvo que el flujo lo declare;
- no debe afectar otras sesiones.

## 8. Contraste y accesibilidad

Reglas obligatorias:

- cajas claras sobre fondo oscuro fuerzan texto oscuro;
- controles táctiles de al menos 44 px;
- inputs de al menos 16 px en móvil;
- navegación por teclado;
- navegación táctil;
- scroll vertical por diapositiva;
- soporte de safe areas;
- no depender únicamente del color para expresar estado.

## 9. Código y herramientas

Antes de mostrar una API, comando, método, parámetro o bloque de código, definir las piezas nuevas que el estudiante necesita para leerlo.

Ejemplo de orden correcto:

```text
qué es el parámetro
  ↓
qué controla
  ↓
ejemplo
  ↓
código donde aparece
```

## 10. Cierre

Toda sesión debe terminar con:

- glosario operativo;
- error/límite importante;
- transferencia a una situación nueva;
- evidencia observable;
- puente explícito a la siguiente sesión.

## 11. QA mínimo

El validador de cada sesión debe comprobar:

- recurso/presentación existente;
- laboratorio embebido;
- términos nuevos definidos;
- desafíos embebidos cuando correspondan;
- respuestas correctas ausentes del frontend;
- contraste;
- móvil;
- JavaScript válido;
- enlaces principales;
- recursos visibles esperados;
- preservación de sesiones protegidas.
