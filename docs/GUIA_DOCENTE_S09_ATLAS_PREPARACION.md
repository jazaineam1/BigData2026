# S09 · Lista de preparación del docente (NO es un recurso del estudiante)

**Curso:** Big Data · Universidad Central · Grupo 2.  
**Objetivo:** que la sesión sobre SECOP, E5 y MongoDB Atlas sea ejecutable por alumnos con o sin acceso a Atlas. Esta es documentación operativa para el docente, **no forma parte de los dos recursos del LMS**. El repositorio GitHub es público: **no guardar aquí hosts privados, nombres de usuario personales, contraseñas, IP de estudiantes ni datos sensibles**.

## 1. La ruta principal YA NO REQUIERE preparación docente de Atlas

El cuaderno vigente tiene como opción predeterminada **Atlas temporal automático**. Cada estudiante crea por la API oficial de MongoDB su propio clúster Ephemeral Free/M0, con URI y usuario generados individualmente; ni host ni contraseña ni autorización de IP deben salir del docente. **No configures el clúster compartido para esta ruta.** El proveedor permite 0.0.0.0/0 exclusivamente en el clúster temporal y exige autenticación. Se pausa después de dos días y elimina después de siete si no se reclama.

La consola Atlas se aprende con el enlace privado de reclamación que muestra la celda 3. El estudiante puede reclamar el clúster con su propia cuenta gratuita y examinar colección, índice y Aggregations. Esta acción opcional requiere login personal, pero no datos del docente.

**Lo que sigue es SOLO una alternativa avanzada para quienes opten por un clúster compartido preexistente**, no un prerrequisito del curso.

## 2. Opcional · preparación del clúster compartido (ruta alternativa)

1. Verificar en [cloud.mongodb.com](https://cloud.mongodb.com/) la organización, proyecto y clúster activos. Preparar **un único índice** del tipo Vector Search en la colección del ejercicio: ruta `embedding`, dimensión 384, similitud `cosine` y filtros `lote` y `entidad`.
2. La consola de Atlas necesita rol de proyecto autorizado para crear/administrar índices (según el método empleado, `Project Data Access Admin`, `Project Search Index Editor` o rol superior). El **usuario de base de datos** PyMongo puede tener `readWrite` en el ámbito acotado: no confundir roles de interfaz con roles de base de datos.
3. Preparar con antelación cuentas de usuario **individuales de base de datos** y entregar a cada alumno, por canal privado, su nombre de usuario, host del clúster y mecanismo seguro de obtención de la contraseña. No insertar contraseñas en slides, LMS, GitHub, correos masivos, capturas ni mensajes públicos.
4. En el momento de clase, cada estudiante ejecuta la celda **0** del cuaderno. Esas salidas `IP_COLAB` identifican la IP pública del runtime. Un operador autorizado añade solo `IP_COLAB/32` en Network Access como regla temporal; no confiar en la IP del navegador ni abrir `0.0.0.0/0`.
5. Confirmar **cada capa por separado**: `ping` (acceso), `count_documents({lote: LOTE}) == N` (persistencia), `queryable=True` (índice), `atlas_query_ejecutada=True` (consulta real) y exportación JSON individual (evidencia). No contar una tabla NumPy ni un pipeline generado como ejecución en Atlas.
6. Verificar permiso de lectura/escritura en la colección y la regla IP /32 vigente antes de que comience la clase, pero anticipar que **Colab puede cambiar de IP tras reiniciar**.

## 3. ¿Qué va en cada soporte?

- **Presentación S09:** historia SECOP, significado de documentos y vectores, acceso a tutorial de seis pasos y guía de Atlas desde cero como ayuda, sin instrucciones de administración del proyecto.
- **Colab S09:** Atlas temporal automático es predeterminado y no requiere datos del docente. La opción Mi Atlas propio conserva instrucciones y credenciales personales para usuarios avanzados.
- **Este documento:** creación/gestión de usuarios e índices compartidos, roles, costes, seguridad, temporalidad de la red y contingencias docentes. **No se registra como tercer recurso LMS.**

## 4. Plan B si falla el acceso

- Mantener `USAR_ATLAS=False`; E5 y búsqueda local NumPy se ejecutan con el corpus preparado.
- El expediente distingue `motor_ann_ejecutado: NO EJECUTADO` del ranking NumPy local y marca honestamente la ruta realizada. Ninguna calificación debe hacer pasar el respaldo como prueba de Atlas.
- Si falla la descarga del corpus o del encoder, comprobar internet; el respaldo de seis documentos es **sintético** y debe declararse. No inventar evidencias de contratos reales.

## 5. Checklist de verificación en la clase

- [ ] Abrir la presentación pública desde la diapositiva 21 y el tutorial integrado.
- [ ] Abrir el Colab publicado y guardar copia individual en Drive.
- [ ] Ejecutar ▶ de la celda 0 y observar IP_COLAB real sin errores de instalación.
- [ ] Cargar SECOP, personalizar EQUIPO y obtener embeddings N×384.
- [ ] Con Atlas personal o asignado: obtener host y usuario del lugar correcto, ingresar contraseña solo en el prompt oculto y obtener ping.
- [ ] Insertar exactamente N documentos; ejecutar la celda dos veces y comprobar idempotencia.
- [ ] Reutilizar un índice o crear uno en el clúster propio; comprobar queryable=True.
- [ ] Cambiar la consulta y aplicar un filtro de entidad sobre un resultado observado.
- [ ] Exportar `s09_atlas_evidencia.json` a Drive individual, y en S10 reutilizar contexto cuando exista.
- [ ] Probar también ruta local sin Atlas y comprobar etiqueta inequívoca.

## 6. Referencias oficiales

- [Implementar clúster gratuito](https://www.mongodb.com/es/docs/atlas/tutorial/deploy-free-tier-cluster/)
- [Conectar a Atlas](https://www.mongodb.com/es/docs/atlas/connect-to-database-deployment/)
- [Gestionar índices de búsqueda y privilegios](https://www.mongodb.com/es/docs/search/indexes/manage-indexes/)
- [Network Access](https://www.mongodb.com/docs/atlas/security/ip-access-list/)

**Limitación:** no se declara certificada una conexión real a la instancia privada del docente ni a las cuentas individuales solo porque la prueba automática del código haya pasado. Hay que comprobar esos accesos en los Colab autorizados, sin exponer los secretos.
