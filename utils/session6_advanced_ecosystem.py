#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Añade el cierre avanzado de red contractual a S06.

Este bloque va al FINAL del cuaderno. No cambia el itinerario zero-to-hero:
primero se aprende Cypher con el ejemplo de juguete y solo después se explora
la red completa de la entidad ancla y la similitud entre ecosistemas.
"""
from __future__ import annotations


def md(text: str, cell_id: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": text.strip("\n").splitlines(keepends=True),
        "id": cell_id,
    }


ADVANCED_CELLS = [
    md(r'''
---
# Apéndice final · De 53 proveedores a una red contractual realmente interesante

Hasta aquí aprendiste a construir y leer patrones. Ahora usamos **el mismo grafo real** para responder preguntas que ya no son simplemente “listar proveedores”.

La entidad ancla del curso es:

- **FUERZA AEROESPACIAL COLOMBIANA**
- NIT usado en el grafo: **899999102**

En el extracto versionado actual, el manifiesto reporta **53 proveedores históricos distintos** para esta entidad y **41 proveedores compartidos** con por lo menos otra entidad. **No memorices 53 y 41**: las consultas siguientes vuelven a calcular esos números. Si el extracto cambia, confía en el resultado de Cypher.

> **Objetivo de este apéndice:** pasar de “veo un proveedor” a “entiendo el ecosistema contractual de la entidad y puedo comparar estructuras de red”.

Trabajaremos en este orden:

1. contar todos los proveedores de Aeronáutica;
2. listar los 53 y medir cuántos procesos tiene cada uno;
3. dibujar **todos** los proveedores de Aeronáutica en una sola componente;
4. separar los proveedores exclusivos de los compartidos;
5. ordenar los compartidos por alcance institucional;
6. entender por qué un `LIMIT 30` puede mostrar un solo proveedor;
7. expandir de forma controlada un proveedor;
8. comparar pares de entidades mediante similitud de Jaccard;
9. abrir gráficamente el subgrafo que explica esa similitud.

**Regla de interpretación:** una conexión contractual es evidencia de una relación registrada en el extracto; por sí sola no demuestra fraude, colusión, favorecimiento ni parentesco.
''', "s06-adv-001"),

    md(r'''
## A1. ¿Cuántos proveedores históricos distintos tiene Aeronáutica?

Copia esta consulta en **Aura Query**:

```cypher
MATCH
(a:Entidad {nit:"899999102"})
-[:PUBLICA]->(:Proceso)
-[:ADJUDICADO_A]->(v:Proveedor)

RETURN count(DISTINCT v) AS proveedores_distintos
```

### Léela de izquierda a derecha

```text
(a:Entidad {nit:"899999102"})
```

- `a` es una **variable**: durante esta consulta usaremos ese nombre corto para referirnos al nodo.
- `:Entidad` es el **label**.
- `{nit:"899999102"}` fija cuál Entidad queremos: la Fuerza Aeroespacial Colombiana.

```text
-[:PUBLICA]->
```

Sigue únicamente relaciones de tipo `PUBLICA`.

```text
(:Proceso)
```

Acepta cualquier nodo con label `Proceso`. No le damos variable porque en esta consulta no necesitamos devolverlo ni medirlo.

```text
-[:ADJUDICADO_A]->(v:Proveedor)
```

Desde cada Proceso sigue una adjudicación observada hasta un Proveedor. A ese proveedor sí lo llamamos `v`.

Finalmente:

```cypher
count(DISTINCT v)
```

significa:

- `count(...)`: contar;
- `v`: nodos Proveedor encontrados;
- `DISTINCT`: si el mismo proveedor aparece en varios procesos, cuéntalo **una sola vez**.

### Qué debes obtener

En el extracto actual, la salida esperada es aproximadamente:

```text
proveedores_distintos
---------------------
53
```

Si aparece `53`, **no significa 53 procesos**. Significa 53 nodos Proveedor diferentes conectados con la entidad a través de por lo menos un proceso histórico adjudicado.
''', "s06-adv-002"),

    md(r'''
## A2. No quiero solo el número: quiero ver los 53 proveedores

Ahora conserva el Proceso en una variable `p` para poder contar cuántos procesos de Aeronáutica llegan a cada proveedor:

```cypher
MATCH
(a:Entidad {nit:"899999102"})
-[:PUBLICA]->(p:Proceso)
-[:ADJUDICADO_A]->(v:Proveedor)

RETURN
    v.nit AS nit_proveedor,
    v.nombre AS proveedor,
    count(DISTINCT p) AS procesos_con_aeronautica

ORDER BY
    procesos_con_aeronautica DESC,
    proveedor ASC
```

### Qué cambió respecto de A1

Antes teníamos:

```text
(:Proceso)
```

Ahora usamos:

```text
(p:Proceso)
```

Le pusimos la variable `p` porque necesitamos contar los procesos.

### Explicación de RETURN

```cypher
v.nit AS nit_proveedor
```

devuelve la propiedad `nit` del Proveedor y llama a esa columna `nit_proveedor`.

```cypher
v.nombre AS proveedor
```

devuelve su nombre.

```cypher
count(DISTINCT p) AS procesos_con_aeronautica
```

cuenta cuántos procesos **distintos** de Aeronáutica llegan a ese proveedor.

### Explicación de ORDER BY

```cypher
ORDER BY procesos_con_aeronautica DESC
```

pone primero a los proveedores con más procesos de la entidad.

```cypher
proveedor ASC
```

solo sirve como segundo criterio cuando dos proveedores tienen el mismo conteo: los ordena alfabéticamente.

### Qué debes mirar

Cambia el resultado a **Table**. Debes ver muchas filas: una por proveedor.

La pregunta que responde ya no es “¿cuántos proveedores hay?”, sino:

> **¿Con cuáles proveedores aparece históricamente la entidad y con cuántos procesos aparece cada uno?**
''', "s06-adv-003"),

    md(r'''
## A3. Ahora sí: dibuja TODOS los proveedores de Aeronáutica

Esta consulta devuelve **caminos completos**, no columnas escalares:

```cypher
MATCH camino =
(a:Entidad {nit:"899999102"})
-[:PUBLICA]->(p:Proceso)
-[:ADJUDICADO_A]->(v:Proveedor)

RETURN camino
```

### ¿Qué hace `camino =`?

Le damos un nombre al patrón completo:

```text
Entidad → Proceso → Proveedor
```

Entonces `RETURN camino` devuelve los nodos **y** las relaciones que forman cada coincidencia. Eso permite que Aura los dibuje en **Graph**.

### Qué debes ver

Conceptualmente:

```text
                           ┌→ Proceso 1 → Proveedor A
                           ├→ Proceso 2 → Proveedor B
FUERZA AEROESPACIAL ───────┼→ Proceso 3 → Proveedor C
                           ├→ ...
                           └→ Proceso n → Proveedor ...
```

Debes ver **muchos proveedores**, aunque todo se dibuje como **una sola componente conectada**.

> **Una componente no significa un proveedor.**

Todos los caminos comparten la misma Entidad ancla, por eso quedan unidos en una sola isla gráfica.

### Cómo revisar el dibujo

1. Busca el nodo `Entidad` de Aeronáutica.
2. Desde él sigue varias flechas `PUBLICA`.
3. Cada una llega a un `Proceso`.
4. Desde esos procesos sigue `ADJUDICADO_A`.
5. Comprueba que llegas a **proveedores diferentes**.
6. Haz clic en varios proveedores y compara `nit` y `nombre`.

### Graph vs Table

- **Graph** te ayuda a entender la forma de la red.
- **Table** es mejor para comprobar cantidades y valores exactos.

No intentes contar 53 círculos a ojo. Para eso ya usamos `count(DISTINCT v)`.
''', "s06-adv-004"),

    md(r'''
## A4. De los 53, ¿cuántos también aparecen con otras entidades?

Ahora añadimos un **segundo recorrido** que llega al mismo proveedor `v`:

```cypher
MATCH
(a:Entidad {nit:"899999102"})
-[:PUBLICA]->(:Proceso)
-[:ADJUDICADO_A]->(v:Proveedor)

MATCH
(otra:Entidad)
-[:PUBLICA]->(:Proceso)
-[:ADJUDICADO_A]->(v)

WHERE otra.nit <> a.nit

RETURN count(DISTINCT v) AS proveedores_compartidos
```

### La clave está en reutilizar `v`

Primer `MATCH`:

```text
Aeronáutica → Proceso → v
```

Segundo `MATCH`:

```text
otra Entidad → Proceso → v
```

La misma variable `v` aparece en ambos patrones. Eso obliga a que los dos recorridos terminen en **el mismo nodo Proveedor**.

### ¿Para qué sirve WHERE?

```cypher
WHERE otra.nit <> a.nit
```

`<>` significa **distinto de**.

Sin esa línea, Aeronáutica podría contarse a sí misma como “otra entidad”.

### Qué debes obtener

En el extracto versionado actual, el resultado esperado es aproximadamente:

```text
proveedores_compartidos
-----------------------
41
```

Interpretación:

```text
53 proveedores históricos de Aeronáutica
              │
              ├── algunos solo aparecen con Aeronáutica en este extracto
              │
              └── 41 también aparecen vinculados con otras entidades
```

Eso todavía **no dice** que los 41 sean problemáticos. Solo describe alcance relacional.
''', "s06-adv-005"),

    md(r'''
## A5. ¿Cuáles proveedores compartidos conectan más entidades?

Ahora queremos distinguir entre:

- un proveedor compartido con **una** entidad adicional;
- un proveedor compartido con **muchas** entidades adicionales.

Usa:

```cypher
MATCH
(a:Entidad {nit:"899999102"})
-[:PUBLICA]->(p_a:Proceso)
-[:ADJUDICADO_A]->(v:Proveedor)

WITH
    a,
    v,
    count(DISTINCT p_a) AS procesos_aeronautica

MATCH
(otra:Entidad)
-[:PUBLICA]->(p_otra:Proceso)
-[:ADJUDICADO_A]->(v)

WHERE otra.nit <> a.nit

RETURN
    v.nit AS nit_proveedor,
    v.nombre AS proveedor,
    procesos_aeronautica,
    count(DISTINCT otra) AS otras_entidades,
    count(DISTINCT p_otra) AS procesos_otras_entidades

ORDER BY
    otras_entidades DESC,
    procesos_aeronautica DESC,
    nit_proveedor ASC
```

### Primera etapa

```cypher
MATCH ... Aeronáutica ... (v:Proveedor)
```

encuentra los proveedores de la entidad.

```cypher
count(DISTINCT p_a)
```

mide cuántos procesos de Aeronáutica llegan a cada proveedor.

### ¿Por qué aparece WITH?

```cypher
WITH a, v, count(DISTINCT p_a) AS procesos_aeronautica
```

`WITH` cierra la primera etapa y conserva tres cosas para la siguiente:

- `a`: la Entidad ancla;
- `v`: cada Proveedor;
- `procesos_aeronautica`: el conteo calculado.

No crea una tabla permanente. Es una tubería dentro de la misma consulta.

### Segunda etapa

Volvemos a usar `v`:

```cypher
MATCH
(otra:Entidad)-[:PUBLICA]->(p_otra:Proceso)-[:ADJUDICADO_A]->(v)
```

Ahora buscamos qué otras entidades alcanzan esos mismos proveedores.

### Tres métricas diferentes

```text
procesos_aeronautica
→ cuántos procesos de Aeronáutica llegan al proveedor

otras_entidades
→ cuántas entidades diferentes, excluyendo Aeronáutica, llegan al proveedor

procesos_otras_entidades
→ cuántos procesos de esas otras entidades llegan al proveedor
```

Esta tabla es mucho más informativa que “proveedor compartido = sí/no”.

> Un proveedor puede tener pocos procesos con Aeronáutica pero una red institucional enorme, o al revés.
''', "s06-adv-006"),

    md(r'''
## A6. ¿Por qué `LIMIT 30` podía hacerme ver un solo proveedor?

Este es el punto que causó la confusión anterior.

La consulta larga:

```text
Aeronáutica → Proceso → Proveedor ← Proceso ← otra Entidad
```

no produce “una fila por proveedor”.

Produce **una fila por coincidencia del camino**.

Compruébalo:

```cypher
MATCH
(a:Entidad {nit:"899999102"})
-[:PUBLICA]->(:Proceso)
-[:ADJUDICADO_A]->(v:Proveedor)
<-[:ADJUDICADO_A]-(p_otra:Proceso)
<-[:PUBLICA]-(otra:Entidad)

WHERE otra.nit <> a.nit

RETURN
    v.nit AS nit_proveedor,
    v.nombre AS proveedor,
    count(*) AS caminos_generados

ORDER BY caminos_generados DESC
```

### ¿Qué significa `count(*)` aquí?

Después de que `MATCH` produjo las coincidencias, `count(*)` cuenta **filas/caminos**, no proveedores distintos.

Imagina:

```text
Proveedor X → genera 48 caminos
Proveedor Y → genera 20 caminos
Proveedor Z → genera  7 caminos
```

Si haces una consulta sin agrupar y escribes:

```cypher
LIMIT 30
```

las primeras 30 coincidencias podrían pertenecer todas al **Proveedor X**.

Por eso:

```text
LIMIT 30
≠
30 proveedores
```

Significa:

```text
como máximo 30 filas/caminos del resultado
```

### Regla para no volver a confundirte

Si quieres limitar proveedores, primero debes **agrupar o deduplicar proveedores** y solo después aplicar `LIMIT`.

Ejemplo:

```cypher
MATCH
(a:Entidad {nit:"899999102"})
-[:PUBLICA]->(:Proceso)
-[:ADJUDICADO_A]->(v:Proveedor)

WITH DISTINCT v

RETURN v.nit, v.nombre
LIMIT 30
```

Aquí sí el `LIMIT 30` se aplica después de dejar una fila por proveedor.
''', "s06-adv-007"),

    md(r'''
## A7. Quiero explorar visualmente UN proveedor sin perder el contexto de los demás

Primero usa la tabla de **A5** y copia el NIT de un proveedor que te interese.

No lo adivines. Tómalo literalmente de la columna `nit_proveedor`.

Después reemplaza `"PEGA_NIT_AQUI"`:

```cypher
MATCH camino_ancla =
(a:Entidad {nit:"899999102"})
-[:PUBLICA]->(p_a:Proceso)
-[:ADJUDICADO_A]->(v:Proveedor {nit:"PEGA_NIT_AQUI"})

MATCH camino_otras =
(otra:Entidad)
-[:PUBLICA]->(p_otra:Proceso)
-[:ADJUDICADO_A]->(v)

WHERE otra.nit <> a.nit

RETURN
    camino_ancla,
    camino_otras
```

### Qué estamos haciendo

El primer camino fija simultáneamente:

- Aeronáutica;
- sus procesos;
- **un proveedor concreto**.

El segundo camino conserva ese mismo `v` y busca todas las otras entidades que llegan a él.

### Qué debes ver en Graph

```text
                           otra Entidad 1
                                │
                              Proceso
                                │
                                ▼
Aeronáutica → Proceso ─────→ PROVEEDOR
                                ▲
                                │
                              Proceso
                                │
                           otra Entidad 2
```

Aquí sí tiene sentido hablar de un proveedor como **puente** entre entidades.

### Por qué no expandimos los 41 a la vez

Si cada proveedor conecta muchos procesos y entidades, devolver toda la red puede producir cientos o miles de elementos superpuestos. El resultado existe, pero puede convertirse en un **hairball**: demasiadas líneas para leer.

La estrategia correcta es:

1. medir todo;
2. ordenar;
3. seleccionar;
4. expandir el subgrafo que necesitas explicar.
''', "s06-adv-008"),

    md(r'''
## A8. Una pregunta realmente estructural: ¿qué entidades tienen ecosistemas de proveedores parecidos?

Compartir **un** proveedor puede ser circunstancial.

Una pregunta más fuerte es:

> **¿Qué pares de entidades comparten una fracción grande de sus carteras de proveedores?**

Para comparar carteras usaremos la **similitud de Jaccard**:

```text
J(A,B) =
proveedores compartidos
────────────────────────────────────────
proveedores de A + proveedores de B - compartidos
```

Ejemplo:

```text
Entidad A tiene 10 proveedores
Entidad B tiene 12 proveedores
Comparten 8

Jaccard = 8 / (10 + 12 - 8)
        = 8 / 14
        = 0.571
```

Una similitud de `0.571` significa que aproximadamente el 57,1 % de la unión de ambas carteras está compartida.

### Consulta

```cypher
MATCH
(e1:Entidad)
-[:PUBLICA]->(:Proceso)
-[:ADJUDICADO_A]->(v:Proveedor)
<-[:ADJUDICADO_A]-(:Proceso)
<-[:PUBLICA]-(e2:Entidad)

WHERE e1.nit < e2.nit

WITH
    e1,
    e2,
    count(DISTINCT v) AS proveedores_compartidos

WHERE proveedores_compartidos >= 3

MATCH
(e1)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(va:Proveedor)

WITH
    e1,
    e2,
    proveedores_compartidos,
    count(DISTINCT va) AS total_e1

MATCH
(e2)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(vb:Proveedor)

WITH
    e1,
    e2,
    proveedores_compartidos,
    total_e1,
    count(DISTINCT vb) AS total_e2

WITH
    e1,
    e2,
    proveedores_compartidos,
    total_e1,
    total_e2,
    toFloat(proveedores_compartidos)
    / (total_e1 + total_e2 - proveedores_compartidos)
      AS similitud_jaccard

RETURN
    e1.nit AS nit_1,
    e1.nombre AS entidad_1,
    e2.nit AS nit_2,
    e2.nombre AS entidad_2,
    total_e1,
    total_e2,
    proveedores_compartidos,
    round(similitud_jaccard, 3) AS similitud_jaccard

ORDER BY
    similitud_jaccard DESC,
    proveedores_compartidos DESC

LIMIT 20
```

### Explicación completa

#### 1. Primer MATCH

```text
e1 → Proceso → v ← Proceso ← e2
```

Busca pares de entidades que llegan al mismo proveedor.

#### 2. ¿Por qué `e1.nit < e2.nit`?

Sin esa condición aparecerían dos versiones del mismo par:

```text
A - B
B - A
```

La comparación `<` se usa únicamente para conservar un orden estable y quedarnos con una sola combinación. **No significa que una entidad sea “menor” en importancia.**

#### 3. Primer conteo

```cypher
count(DISTINCT v)
```

cuenta cuántos proveedores diferentes comparten `e1` y `e2`.

#### 4. Filtro de al menos tres

```cypher
WHERE proveedores_compartidos >= 3
```

evita dedicar cálculo adicional a pares cuya coincidencia es mínima. El valor 3 es un umbral exploratorio, no una regla de riesgo.

#### 5. Total de proveedores de e1

```cypher
count(DISTINCT va) AS total_e1
```

necesitamos el tamaño completo de la cartera de la primera entidad.

#### 6. Total de proveedores de e2

```cypher
count(DISTINCT vb) AS total_e2
```

hacemos lo mismo con la segunda.

#### 7. Jaccard

```cypher
toFloat(proveedores_compartidos)
/
(total_e1 + total_e2 - proveedores_compartidos)
```

El denominador calcula el tamaño de la **unión**. Restamos los compartidos una vez porque, al sumar los dos totales, quedaron contados dos veces.

#### 8. ORDER BY

Ponemos primero los pares con mayor proporción de cartera compartida. Si empatan, priorizamos el que tenga más proveedores compartidos en términos absolutos.

### Por qué esta pregunta es más propia de grafos

No nos limitamos a recuperar una fila contractual. Estamos comparando **formas de vecindarios**:

```text
Entidad 1 → conjunto de proveedores
Entidad 2 → conjunto de proveedores
```

SQL o pandas también podrían calcularlo, pero en Neo4j el patrón que define la comparación está expresado directamente como recorrido del grafo.
''', "s06-adv-009"),

    md(r'''
## A9. Convierte el primer par de A8 en un subgrafo explicable

La tabla anterior te devuelve:

```text
nit_1
entidad_1
nit_2
entidad_2
...
```

Toma literalmente los NIT del par que quieras inspeccionar y reemplaza:

- `"NIT_1_AQUI"`
- `"NIT_2_AQUI"`

```cypher
MATCH camino_1 =
(e1:Entidad {nit:"NIT_1_AQUI"})
-[:PUBLICA]->(p1:Proceso)
-[:ADJUDICADO_A]->(v:Proveedor)

MATCH camino_2 =
(e2:Entidad {nit:"NIT_2_AQUI"})
-[:PUBLICA]->(p2:Proceso)
-[:ADJUDICADO_A]->(v)

RETURN
    camino_1,
    camino_2
```

### ¿Por qué solo aparecen proveedores compartidos?

Porque los dos `MATCH` reutilizan la **misma variable `v`**.

El primer recorrido dice:

```text
e1 → ... → v
```

y el segundo:

```text
e2 → ... → v
```

Por tanto, Neo4j solo conserva proveedores que cumplen ambos patrones.

### Qué debes buscar visualmente

```text
                 Proveedor A
                ↗           ↖
Entidad 1 → P1                 P8 ← Entidad 2

                 Proveedor B
                ↗           ↖
Entidad 1 → P2                 P9 ← Entidad 2

                 Proveedor C
                ↗           ↖
Entidad 1 → P3                P10 ← Entidad 2
```

Aquí el dato interesante ya no es un proveedor aislado: es un **subgrafo repetido de coincidencias entre dos entidades**.

### Preguntas correctas

- ¿Cuántos proveedores comparten?
- ¿Qué fracción de sus carteras representa?
- ¿Cuántos procesos explican esas coincidencias?
- ¿La similitud se concentra en uno o muchos proveedores?

### Preguntas que este grafo NO responde

Con los datos actuales no puedes afirmar:

- relación familiar;
- mismo propietario;
- mismo beneficiario final;
- coordinación entre oferentes;
- colusión;
- fraude.

Para estudiar eso habría que incorporar nodos y relaciones verificadas adicionales, por ejemplo `Persona`, `REPRESENTADO_POR`, `SOCIO_DE`, dirección, teléfono o beneficiario final.
''', "s06-adv-010"),

    md(r'''
## A10. Qué te llevas de este cierre

Ya no estamos usando Neo4j solo para hacer el equivalente gráfico de un `JOIN`.

La progresión fue:

```text
53 proveedores históricos
        ↓
41 proveedores compartidos
        ↓
alcance institucional de cada proveedor
        ↓
expansión de un proveedor como puente
        ↓
comparación de carteras completas
        ↓
subgrafo que explica la similitud
```

### Respuesta a la confusión inicial

Si Aura te mostraba un solo proveedor al usar `LIMIT 30`, no era porque Aeronáutica tuviera un proveedor.

Era porque:

```text
LIMIT
```

estaba restringiendo **caminos**, y el mismo proveedor podía ocupar muchas de esas filas.

Para saber cuántos actores distintos existen:

```cypher
count(DISTINCT v)
```

Para listarlos:

```cypher
WITH DISTINCT v
```

Para entender la estructura:

```cypher
RETURN camino
```

### Criterio profesional

Primero **mide** la red. Después **selecciona** una parte relevante. Finalmente **explica** el subgrafo.

No uses el tamaño, la posición o la cercanía automática de los círculos como evidencia cuantitativa.

> **Table mide; Graph explica.**
''', "s06-adv-011"),
]


def append_advanced_ecosystem(cells: list[dict]) -> list[dict]:
    """Añade una sola vez el apéndice avanzado al final del cuaderno."""
    marker = "Apéndice final · De 53 proveedores a una red contractual realmente interesante"
    if any(marker in "".join(c.get("source", [])) for c in cells):
        return cells
    cells.extend(ADVANCED_CELLS)
    return cells
