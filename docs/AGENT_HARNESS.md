# Agent Harness V1 · BigData2026

Este harness coordina agentes de ingeniería con un **DAG de tareas**, scopes de escritura, worktrees aislados, revisores independientes y gates deterministas. No reemplaza `AGENTS.md`: lo convierte en una de las fuentes de invariantes del trabajo.

## Arquitectura

```text
user goal
   │
requirements + research
   │
   ├── writer A (worktree/branch)
   └── writer B (worktree/branch)
              │
           integrate
              │
      QA + a11y + security
              │
            repair
              │
          final gates
```

Los agentes read-only también corren en worktrees detached. Si un revisor modifica archivos, la tarea falla y sus cambios se descartan. Los writers no controlan Git: si un proveedor crea commits, el harness los aplana, inspecciona el diff real y vuelve a crear el commit solo después de comprobar scope y gates.

## Comandos básicos

```bash
python -m utils.harness.cli doctor
python -m utils.harness.cli validate
python -m utils.harness.cli plan repo-audit.yaml --goal "Auditar S09"
python -m utils.harness.cli plan session-improvement.yaml --goal "Mejorar S10"
```

Simulación sin modelos:

```bash
python -m utils.harness.cli run repo-audit.yaml \
  --goal "Auditar el repo" \
  --provider dry_run \
  --approval L1 \
  --cleanup
```

Una corrida real que cree commits e integre ramas candidatas usa `--approval L2`. L2 **no autoriza push ni merge a main**.

## Proveedores

La V1 no guarda claves ni fija SDKs. Los agentes se conectan mediante comandos locales que leen el prompt por stdin. El subprocess recibe un entorno mínimo y solo las credenciales del proveedor declaradas en `pass_env`; no hereda indiscriminadamente variables como AWS, bases de datos u otros tokens:

- `HARNESS_OPENAI_CMD`
- `HARNESS_CLAUDE_CMD`
- `HARNESS_GEMINI_CMD`

El comando debería devolver un JSON:

```json
{
  "status": "pass",
  "summary": "Qué hizo o encontró",
  "findings": [
    {"severity": "warning", "message": "Hallazgo", "files": ["lms/x.html"]}
  ],
  "requested_actions": []
}
```

Esto permite usar Codex, Claude Code, Gemini CLI o wrappers propios sin acoplar la orquestación a un proveedor. `doctor` informa qué conectores locales están configurados.

## Niveles de aprobación

| Nivel | Alcance |
|---|---|
| L0 | lectura y checks no mutantes |
| L1 | escritura dentro de worktrees aislados |
| L2 | commits/ramas locales e integración de candidatas |
| L3 | acción externa/destructiva; la V1 no la ejecuta automáticamente |

Nunca se automatizan merge/push a `main`, migraciones de producción, despliegues, rotación de credenciales, reescritura de historia o borrado remoto.

## Scopes

Hay dos barreras de escritura:

1. scope máximo del rol en `.harness/policies/write-scopes.yaml`;
2. scope declarado por la tarea.

Un archivo cambiado debe pertenecer a ambos. El harness calcula el diff real; no confía en la lista que reporte el modelo.

Archivos como `AGENTS.md`, `.harness/**`, workflows y `course.json` requieren L2. `.local-docente/**` requiere L3 y no debe publicarse. El requirements agent puede recibir `.local-docente/Estado_del_curso.md` como contexto privado cuando exista, sin copiarlo al worktree.

## Pipelines incluidos

- `repo-audit.yaml`: requirements, QA/arquitectura, seguridad y accesibilidad en paralelo; solo lectura.
- `session-improvement.yaml`: carriles de pedagogía y frontend aislados, integración, tres revisores, reparación y gates.
- `backend-change.yaml`: backend aislado con revisión QA/seguridad; nunca despliega.
- `harness-self-check.yaml`: validación determinista sin LLM.

Ver el DAG antes de ejecutar:

```bash
python -m utils.harness.cli plan session-improvement.yaml --goal "..."
```

## Gates

`.harness/policies/quality-gates.yaml` reutiliza las guardias reales del repo: higiene, secretos/PII, ausencia de respuestas abiertas, calendario/index y enlaces estáticos.

```bash
python -m utils.harness.cli gate harness_validate harness_unit
```

## Evidencia

Cada corrida deja:

```text
.agent-runs/<run-id>/
  run.json
  tasks/<task>/input.json
  tasks/<task>/provider.json
  tasks/<task>/output.json
  final.json
```

Los handoffs son resultados estructurados, no chats infinitos. Los worktrees y locks viven en `.agent-worktrees/` y `.agent-locks/`; las tres carpetas están ignoradas por Git.

## Flujo recomendado

1. `doctor`.
2. `plan`.
3. `run ... --provider dry_run`.
4. Configurar los comandos locales de los proveedores.
5. Ejecutar con L2 solo cuando quieras commits locales.
6. Revisar `.agent-runs/<id>/final.json` y la rama de integración.
7. Crear/pushear PR como una acción separada y consciente.

La siguiente evolución natural es añadir un adaptador nativo por proveedor y métricas de costo/latencia/calidad; la V1 separa primero la orquestación, seguridad e integración de la elección del modelo.

## Límite de aislamiento V1

Los worktrees aíslan el **estado Git**, no el sistema operativo. Un CLI local sigue ejecutándose con los permisos del usuario y puede tener acceso a red o archivos fuera del repo según su propia configuración. Para tareas de mayor riesgo, la siguiente capa debe ser un sandbox/contenedor por agente.
