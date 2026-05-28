# Modulo 04: NoSQL con MongoDB

## Objetivo

Entender cuando usar NoSQL documental y realizar operaciones de consulta, agregacion e indexacion en MongoDB para analitica.

## Conceptos clave

- modelo documental
- diferencia entre SQL y NoSQL
- diseno de documentos para consultas reales
- aggregation pipeline
- indices simples, compuestos y geoespaciales
- Atlas como ruta principal y Docker local como respaldo

## Practica guiada

1. Levantar perfil `nosql`:

```bash
docker compose --profile nosql up -d
```

2. Cargar datos demo locales con el script del curso:

```bash
python infraestructura/scripts/seed_mongo.py
```

El script intenta primero conexion local y luego conexion desde contenedor:

```text
mongodb://admin:admin123@localhost:27017/?authSource=admin
mongodb://admin:admin123@mongo:27017/?authSource=admin
```

3. Consultar por filtros, agregaciones, indices y geodatos.

## Entregable

- coleccion creada con datos del ejercicio
- consultas documentadas (`find`, filtro anidado, agregacion)
- lectura de `explain()`
- interpretacion de un resultado analitico
