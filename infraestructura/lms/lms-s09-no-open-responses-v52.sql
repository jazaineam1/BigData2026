-- S09 V52 · experiencia estudiantil sin respuestas abiertas ni muro obligatorio.
-- Conserva el historial existente, pero LAB3/LAB4/LAB8 vuelven a completarse
-- únicamente con autocomprobaciones objetivas (choice / numeric).

update public.bd_activity_catalog
set config = coalesce(config,'{}'::jsonb)
             - 'requires_transfer'
             - 'transfer_fields'
             - 'transfer_requires_review',
    version = greatest(version,4) + 1,
    updated_at = now()
where code in ('bd-s09-lab3','bd-s09-lab4','bd-s09-lab8');

update public.bd_lms_activities
set metadata = coalesce(metadata,'{}'::jsonb)
               - 'self_check_role'
               - 'transfer_required'
               - 'transfer_rule'
where code in ('bd-s09-lab3','bd-s09-lab4','bd-s09-lab8');

-- Si alguien ya había aprobado la autocomprobación antes de V52, no se le
-- obliga a escribir una transferencia. No se borra ninguna evidencia histórica.
update public.bd_lms_activity_progress p
set status = case
      when coalesce((p.metadata->>'self_check_verified')::boolean,false) then 'completed'
      else p.status
    end,
    completed_at = case
      when coalesce((p.metadata->>'self_check_verified')::boolean,false)
        then coalesce(p.completed_at,now())
      else p.completed_at
    end,
    updated_at = now(),
    metadata = (
      coalesce(p.metadata,'{}'::jsonb)
      - 'transfer_required'
      - 'transfer_pending'
      - 'transfer_verified'
      - 'completion_semantics'
    )
    || jsonb_build_object('completion_semantics','objective_self_check')
    || case
         when coalesce((p.metadata->>'self_check_verified')::boolean,false)
           then jsonb_build_object('evidence_verified',true)
         else '{}'::jsonb
       end
where p.activity_code in ('bd-s09-lab3','bd-s09-lab4','bd-s09-lab8');

comment on column public.bd_evidence.step_id is
  'submission = evidencia/autocomprobación normal; transfer = evidencia histórica de versiones anteriores de S09.';
