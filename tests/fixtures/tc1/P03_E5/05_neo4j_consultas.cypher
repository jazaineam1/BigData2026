// --- restricciones ---
CREATE CONSTRAINT tc1_entidad_nit IF NOT EXISTS FOR (e:Entidad) REQUIRE e.nit IS UNIQUE;
CREATE CONSTRAINT tc1_contrato_id IF NOT EXISTS FOR (c:Contrato) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT tc1_proveedor_nit IF NOT EXISTS FOR (p:Proveedor) REQUIRE p.nit IS UNIQUE;

// --- carga ---
UNWIND $filas AS fila
MERGE (e:Entidad {nit: fila.nit_entidad})
  SET e.nombre = fila.entidad
MERGE (c:Contrato {id: fila.id_contrato})
  SET c.valor = fila.valor, c.fecha_firma = fila.fecha_firma, c.tipo = fila.tipo_contrato, c.pareja = fila.pareja
MERGE (p:Proveedor {nit: fila.nit_proveedor})
  SET p.nombre = fila.proveedor
MERGE (e)-[:FIRMA]->(c)
MERGE (c)-[:ADJUDICADO_A]->(p);

// --- ancla ---
MATCH (e:Entidad)-[:FIRMA]->(:Contrato)-[:ADJUDICADO_A]->(p:Proveedor)<-[:ADJUDICADO_A]-(:Contrato)<-[:FIRMA]-(otra:Entidad)
WHERE otra <> e
WITH e, count(DISTINCT p) AS proveedores_compartidos
MATCH (e)-[:FIRMA]->(c:Contrato)
RETURN e.nit AS nit, e.nombre AS entidad, proveedores_compartidos, count(DISTINCT c) AS contratos
ORDER BY proveedores_compartidos DESC, contratos DESC, nit ASC
LIMIT 5;

// --- contexto ---
MATCH (a:Entidad {nit: $nit_ancla})-[:FIRMA]->(c:Contrato)-[:ADJUDICADO_A]->(p:Proveedor)
RETURN a.nombre AS entidad, count(DISTINCT c) AS contratos, count(DISTINCT p) AS proveedores;

// --- compartidos ---
MATCH (a:Entidad {nit: $nit_ancla})-[:FIRMA]->(:Contrato)-[:ADJUDICADO_A]->(p:Proveedor)<-[:ADJUDICADO_A]-(:Contrato)<-[:FIRMA]-(otra:Entidad)
WHERE otra <> a
RETURN p.nit AS nit_proveedor, p.nombre AS proveedor, collect(DISTINCT otra.nombre) AS otras_entidades;

// --- ranking ---
MATCH (a:Entidad {nit: $nit_ancla})-[:FIRMA]->(ca:Contrato)-[:ADJUDICADO_A]->(p:Proveedor)
WITH a, p, count(DISTINCT ca) AS contratos_con_ancla
MATCH (p)<-[:ADJUDICADO_A]-(:Contrato)<-[:FIRMA]-(otra:Entidad)
WHERE otra <> a
RETURN p.nit AS nit_proveedor, p.nombre AS proveedor, contratos_con_ancla, count(DISTINCT otra) AS entidades_conectadas
ORDER BY entidades_conectadas DESC, contratos_con_ancla DESC, nit_proveedor ASC;
