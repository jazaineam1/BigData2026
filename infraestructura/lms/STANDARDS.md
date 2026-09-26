# Interoperabilidad y estándares del LMS Big Data

## Propósito

Esta capa evita que los datos académicos queden encerrados en una implementación propia. El principio es **exportar primero lo que puede validarse localmente** y activar integraciones bidireccionales solo cuando exista una contraparte institucional real.

Ninguna capacidad descrita aquí implica certificación 1EdTech salvo que en el futuro se complete formalmente el proceso de certificación correspondiente.

## Estado de implementación

| Estándar / formato | Estado | Alcance actual |
| --- | --- | --- |
| QTI 3.0 | Implementado para exportación | Banco activo de preguntas a paquete QTI con `imsmanifest.xml` e ítems XML. |
| OneRoster 1.2.1 CSV | Implementado como perfil de compatibilidad | Cohorte, usuarios, roles, matrículas, curso, clase, categorías, lineItems y resultados cuando existen. |
| iCalendar 2.0 | Implementado | Sesiones y tareas que tengan fecha registrada. |
| Gradebook CSV | Implementado | Matriz docente simple de puntajes. |
| Edu-API | Planeado | Candidato preferido para datos académicos institucionales de educación superior. |
| LTI 1.3 / LTI Advantage | No configurado | Requiere plataforma externa, client/deployment IDs, OIDC endpoints y llaves. |
| OIDC / SSO institucional | No configurado | Requiere proveedor de identidad de la universidad. |
| xAPI / Caliper | No configurado | Requiere LRS o consumidor institucional. |

## QTI 3

Referencia:
- https://www.1edtech.org/standards/qti
- https://www.imsglobal.org/activity/qtiapip

El exportador usa el namespace QTI 3:
`http://www.imsglobal.org/xsd/imsqtiasi_v3p0`

y un paquete con manifest:
`http://www.imsglobal.org/xsd/qti/qtiv3p0/imscp_v1p1`.

### Mapeo implementado

- `single_choice` → `qti-choice-interaction`, cardinalidad simple.
- `multiple_choice` → `qti-choice-interaction`, cardinalidad múltiple.
- `true_false` → selección única con identificadores `TRUE` / `FALSE`.
- `numeric` → entrada de texto con `base-type="float"`; soporta tolerancia absoluta.
- `short_text` → `qti-extended-text-interaction`, sin clave de respuesta automática.

La exportación conserva la versión de cada pregunta activa. No se declara certificación QTI.

## OneRoster 1.2.1 CSV

Referencias:
- https://standards.1edtech.org/oneroster/specifications/standards/v1p2
- https://www.imsglobal.org/node/204216

La exportación usa modo **Bulk**. En este modo los campos `status` y `dateLastModified` se dejan vacíos según el binding CSV.

El paquete puede incluir:
- `manifest.csv`
- `academicSessions.csv`
- `orgs.csv`
- `courses.csv`
- `classes.csv`
- `users.csv`
- `roles.csv`
- `enrollments.csv`
- `categories.csv`
- `lineItems.csv`
- `results.csv`

### Limitación deliberada para educación superior

OneRoster está orientado principalmente a ecosistemas K-12. En Big Data se ofrece como **perfil de compatibilidad** porque puede ser útil para intercambiar roster y Gradebook con herramientas que solo acepten OneRoster.

Para una integración institucional de educación superior debe evaluarse **Edu-API**:
https://www.1edtech.org/standards/edu-api

### PII

La exportación de roster puede contener nombres y correos de estudiantes. Por eso:
- solo docentes/administradores pueden generarla;
- no se publica en GitHub Pages;
- no se guarda automáticamente en Storage;
- no contiene contraseñas ni hashes;
- el archivo se genera en el navegador y queda bajo responsabilidad del docente que lo descarga.

La separación `givenName` / `familyName` se deriva de `display_name` y debe revisarse antes de intercambiar el paquete con un tercero.

## iCalendar

El archivo `.ics` incluye únicamente:
- sesiones con `starts_at`;
- tareas con `due_at`.

El exportador no inventa fechas faltantes. Si no hay eventos fechados, produce un calendario vacío con una advertencia.

## Gradebook CSV

Formato interno sencillo para respaldo o análisis:
- `user_id`
- estudiante
- correo
- una columna por código de tarea
- puntaje de la entrega más reciente

No sustituye un estándar institucional.

## Integraciones que dependen de terceros

### LTI 1.3 / LTI Advantage

No debe activarse con valores ficticios. Requiere como mínimo:
- issuer de la plataforma;
- client ID;
- deployment ID;
- OIDC authentication endpoint;
- JWKS / llaves;
- target link URI;
- alcances de servicios Advantage si se usan AGS, NRPS o Deep Linking.

### SSO OIDC

Requiere un Identity Provider institucional y una política de mapeo entre la identidad externa y `lms_users`.

### xAPI / Caliper

Solo deben habilitarse cuando exista un Learning Record Store o consumidor institucional autorizado. Los eventos deben minimizar PII y documentar retención.

## Archivos privados

Las entregas de archivo del LMS usan:
- bucket privado;
- URL firmada temporal de carga;
- URL firmada temporal de descarga;
- allowlist de MIME;
- límite de tamaño;
- metadatos asociados a usuario, tarea y entrega.

Las URLs privadas no se almacenan como enlaces públicos permanentes.

## Reglas de seguridad de integraciones

1. Nunca poner service-role keys, client secrets o private keys en HTML/JavaScript público.
2. Toda operación que exponga roster, notas o banco con claves de respuesta requiere rol docente/admin en backend.
3. Registrar exportaciones sensibles en `lms_audit_log`.
4. No marcar una integración como “activa” hasta validar su contraparte real.
5. Preferir identificadores estables sobre nombres como llaves de intercambio.
6. Mantener S07 fuera de esta capa de cambios.
