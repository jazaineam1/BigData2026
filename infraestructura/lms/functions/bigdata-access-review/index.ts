import { createClient } from "npm:@supabase/supabase-js@2";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  { auth: { persistSession: false } },
);

const ALLOWED = new Set(["https://jazaineam1.github.io"]);
const COURSE_CODE = "bigdata";
const ACCESS_PAGE = "https://jazaineam1.github.io/BigData2026/lms/access.html";

function origin(req: Request) {
  const o = req.headers.get("origin");
  if (!o) return "";
  if (ALLOWED.has(o) || /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(o)) return o;
  return null;
}

function h(req: Request) {
  const o = origin(req);
  return {
    "Access-Control-Allow-Origin": o || "https://jazaineam1.github.io",
    "Access-Control-Allow-Headers": "authorization, content-type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Vary": "Origin",
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
  };
}

function out(req: Request, body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...h(req), "Content-Type": "application/json" },
  });
}

function bearer(req: Request) {
  const x = req.headers.get("authorization") || "";
  return x.toLowerCase().startsWith("bearer ") ? x.slice(7).trim() : "";
}

async function sha256(s: string) {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function randomToken() {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  return btoa(String.fromCharCode(...bytes)).replaceAll("+", "-").replaceAll("/", "_").replaceAll("=", "");
}

function tempPassword() {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789";
  const bytes = crypto.getRandomValues(new Uint8Array(10));
  let s = "Db7-";
  for (const b of bytes) s += chars[b % chars.length];
  return s;
}

async function current(req: Request) {
  const t = bearer(req);
  if (!t) return null;
  const th = await sha256(t);
  const { data: s } = await supabase
    .from("lms_auth_sessions")
    .select("id,user_id,expires_at,persistent,created_at")
    .eq("token_hash", th)
    .is("revoked_at", null)
    .maybeSingle();
  if (!s) return null;
  const deadline=s.expires_at?new Date(s.expires_at).getTime():(new Date((s as any).created_at||0).getTime()+(s.persistent?30:1)*24*3600_000);
  if (!Number.isFinite(deadline) || deadline <= Date.now()) return null;
  const { data: u } = await supabase
    .from("lms_users")
    .select("id,username,display_name,role,active")
    .eq("id", s.user_id)
    .eq("active", true)
    .maybeSingle();
  return u ? { session: s, user: u } : null;
}

async function makeAccess(userId: string, requestId: string, createdBy: string) {
  const token = randomToken();
  const hash = await sha256(token);
  const now = new Date().toISOString();
  const expires_at = new Date(Date.now() + 7 * 24 * 3600_000).toISOString();
  await supabase.from("lms_access_tokens").update({ expires_at: now }).eq("request_id", requestId).gt("expires_at", now);
  const { error } = await supabase.from("lms_access_tokens").insert({
    token_hash: hash,
    user_id: userId,
    request_id: requestId,
    created_by: createdBy,
    expires_at,
  });
  if (error) throw error;
  return `${ACCESS_PAGE}#token=${encodeURIComponent(token)}`;
}

async function setTemporaryPassword(userId: string) {
  const password = tempPassword();
  const { error } = await supabase.rpc("lms_set_password", { p_user_id: userId, p_password: password });
  if (error) throw error;
  await supabase
    .from("lms_auth_sessions")
    .update({ revoked_at: new Date().toISOString() })
    .eq("user_id", userId)
    .is("revoked_at", null);
  return password;
}

async function ensureRunEnrollment(userId: string, courseCode: string, role = "student") {
  const { data: run } = await supabase
    .from("lms_course_runs")
    .select("id")
    .eq("course_code", courseCode)
    .eq("active", true)
    .order("created_at", { ascending: false })
    .limit(1)
    .maybeSingle();
  if (!run) return;
  await supabase.from("lms_run_enrollments").upsert(
    { user_id: userId, course_run_id: run.id, role, status: "active", enrolled_at: new Date().toISOString() },
    { onConflict: "user_id,course_run_id" },
  );
}

async function audit(actor: string, action: string, entity: string, id: string, metadata: any = {}) {
  await supabase
    .from("lms_audit_log")
    .insert({ actor_user_id: actor, action, entity_type: entity, entity_id: id, metadata })
    .then(() => {})
    .catch(() => {});
}

async function findAuthUser(email: string) {
  const target = email.trim().toLowerCase();
  for (let page = 1; page <= 10; page++) {
    const { data, error } = await supabase.auth.admin.listUsers({ page, perPage: 1000 });
    if (error) return null;
    const user = (data?.users || []).find((x: any) => String(x.email || "").toLowerCase() === target);
    if (user) return user;
    if ((data?.users || []).length < 1000) break;
  }
  return null;
}

async function ensureAuthIdentity(lms: any, email: string, displayName: string, requestId: string) {
  if (lms?.auth_user_id) return String(lms.auth_user_id);

  let authUser: any = null;
  const created = await supabase.auth.admin.createUser({
    email,
    email_confirm: true,
    user_metadata: { display_name: displayName, source: "bigdata" },
  });

  if (created.data?.user) authUser = created.data.user;
  else authUser = await findAuthUser(email);
  if (!authUser?.id) return null;

  await supabase
    .from("lms_users")
    .update({ auth_user_id: authUser.id, updated_at: new Date().toISOString() })
    .eq("id", lms.id);
  await supabase.from("lms_access_requests").update({ auth_user_id: authUser.id }).eq("id", requestId);
  lms.auth_user_id = authUser.id;
  return String(authUser.id);
}

async function prepareManualDelivery(lms: any, requestRow: any, actor: string) {
  try {
    const authId = await ensureAuthIdentity(lms, requestRow.email, requestRow.full_name, requestRow.id);
    await audit(actor, "access.credentials_manual", "user", lms.id, {
      request_id: requestRow.id,
      recipient_email: requestRow.email,
      auth_identity_ready: !!authId,
    });
    return {
      email_sent: false,
      email_mode: "manual_credentials",
      auth_identity_ready: !!authId,
    };
  } catch (e) {
    return {
      email_sent: false,
      email_mode: "manual_credentials",
      auth_identity_ready: false,
      email_error: e instanceof Error ? e.message : "No se pudo preparar la identidad de correo.",
    };
  }
}

Deno.serve(async (req) => {
  if (origin(req) === null) return out(req, { error: "Origen no permitido" }, 403);
  if (req.method === "OPTIONS") return new Response("ok", { headers: h(req) });
  if (req.method !== "POST") return out(req, { error: "Método no permitido" }, 405);

  const ctx = await current(req);
  if (!ctx) return out(req, { error: "Sesión no válida o vencida" }, 401);
  if (!["teacher", "admin"].includes(ctx.user.role)) return out(req, { error: "No autorizado" }, 403);

  let b: any = {};
  try {
    b = await req.json();
  } catch {
    return out(req, { error: "JSON inválido" }, 400);
  }

  const requestId = String(b.request_id || "").trim();
  const action = String(b.action || "").trim();
  const notes = String(b.notes || "").trim().slice(0, 500);
  if (!requestId || !["approve", "reject", "reset_password", "generate_link"].includes(action)) {
    return out(req, { error: "Solicitud o acción inválida" }, 400);
  }

  const { data: r, error: re } = await supabase
    .from("lms_access_requests")
    .select("id,full_name,email,course_code,status,auth_user_id")
    .eq("id", requestId)
    .eq("course_code", COURSE_CODE)
    .maybeSingle();
  if (re || !r) return out(req, { error: "Solicitud no encontrada" }, 404);

  if (action === "reject") {
    if (r.status !== "pending") return out(req, { error: "Solo una solicitud pendiente puede rechazarse" }, 409);
    const { error } = await supabase
      .from("lms_access_requests")
      .update({ status: "rejected", reviewed_at: new Date().toISOString(), reviewed_by: ctx.user.id, notes: notes || null })
      .eq("id", r.id)
      .eq("status", "pending");
    if (error) return out(req, { error: "No se pudo rechazar" }, 500);
    await audit(ctx.user.id, "access.reject", "access_request", r.id, { email: r.email });
    return out(req, { ok: true, status: "rejected" });
  }

  let { data: lms } = await supabase
    .from("lms_users")
    .select("id,username,display_name,role,active,email,auth_user_id")
    .eq("email", String(r.email||"").trim().toLowerCase())
    .maybeSingle();
  if (!lms) {
    const byUser = await supabase
      .from("lms_users")
      .select("id,username,display_name,role,active,email,auth_user_id")
      .eq("username", String(r.email||"").trim().toLowerCase())
      .maybeSingle();
    lms = byUser.data;
  }

  if (action === "generate_link") {
    if (r.status !== "approved") return out(req, { error: "Primero debes aprobar la solicitud" }, 409);
    if (!lms) return out(req, { error: "No se encontró el perfil matriculado" }, 404);
    const link = await makeAccess(lms.id, r.id, ctx.user.id);
    await audit(ctx.user.id, "access.compat_link", "user", lms.id, { request_id: r.id });
    return out(req, {
      ok: true,
      status: "approved",
      manual_link: link,
      recipient_email: r.email,
      recipient_name: r.full_name,
      warning: "Enlace de compatibilidad generado. El acceso recomendado es usuario y contraseña.",
    });
  }

  if (action === "reset_password") {
    if (r.status !== "approved") return out(req, { error: "Primero debes aprobar la solicitud" }, 409);
    if (!lms) return out(req, { error: "No se encontró el perfil matriculado" }, 404);
    await ensureRunEnrollment(lms.id, COURSE_CODE, lms.role || "student");
    try {
      const password = await setTemporaryPassword(lms.id);
      const delivery = await prepareManualDelivery(lms, r, ctx.user.id);
      await audit(ctx.user.id, "password.reset", "user", lms.id, { request_id: r.id, delivery_mode: "manual_credentials" });
      return out(req, {
        ok: true,
        status: "approved",
        username: lms.username,
        password,
        recipient_email: r.email,
        recipient_name: r.full_name,
        ...delivery,
        warning: "Contraseña temporal creada. El envío automático está desactivado para evitar correos vacíos: usa Copiar, Compartir o Enviar por correo desde el panel docente.",
      });
    } catch {
      return out(req, { error: "No se pudo restablecer la contraseña" }, 500);
    }
  }

  if (r.status !== "pending") {
    return out(req, { error: r.status === "approved" ? "Esta solicitud ya está aprobada" : "Esta solicitud ya fue rechazada" }, 409);
  }

  const { data: course } = await supabase
    .from("lms_courses")
    .select("code,status")
    .eq("code", COURSE_CODE)
    .eq("status", "active")
    .maybeSingle();
  if (!course) return out(req, { error: "El curso ya no está disponible" }, 409);

  if (lms) {
    const { data: upd, error } = await supabase
      .from("lms_users")
      .update({ email: r.email, username: r.email, display_name: r.full_name, active: true, updated_at: new Date().toISOString() })
      .eq("id", lms.id)
      .select("id,username,display_name,role,active,email,auth_user_id")
      .single();
    if (error) return out(req, { error: "No se pudo actualizar el estudiante" }, 500);
    lms = upd;
  } else {
    const { data: ins, error } = await supabase
      .from("lms_users")
      .insert({ username: r.email, email: r.email, display_name: r.full_name, password_hash: null, role: "student", active: true })
      .select("id,username,display_name,role,active,email,auth_user_id")
      .single();
    if (error) return out(req, { error: "No se pudo crear el perfil académico" }, 500);
    lms = ins;
  }

  const { error: enrollError } = await supabase.from("lms_enrollments").upsert(
    { user_id: lms.id, course_code: COURSE_CODE, role: "student", status: "active", enrolled_at: new Date().toISOString() },
    { onConflict: "user_id,course_code" },
  );
  if (enrollError) return out(req, { error: "No se pudo matricular al estudiante" }, 500);
  await ensureRunEnrollment(lms.id, COURSE_CODE, "student");

  const now = new Date().toISOString();
  const { error: updateError } = await supabase
    .from("lms_access_requests")
    .update({ status: "approved", reviewed_at: now, reviewed_by: ctx.user.id, notes: notes || null })
    .eq("id", r.id)
    .eq("status", "pending");
  if (updateError) return out(req, { error: "La cuenta se creó, pero no se pudo cerrar la solicitud" }, 500);
  await audit(ctx.user.id, "access.approve", "user", lms.id, { request_id: r.id, course_code: COURSE_CODE });

  try {
    const password = await setTemporaryPassword(lms.id);
    const delivery = await prepareManualDelivery(lms, r, ctx.user.id);
    return out(req, {
      ok: true,
      status: "approved",
      user_id: lms.id,
      username: lms.username,
      password,
      recipient_email: r.email,
      recipient_name: r.full_name,
      ...delivery,
      warning: "Solicitud aprobada y contraseña temporal creada. El envío automático está desactivado para evitar correos vacíos: usa Copiar, Compartir o Enviar por correo desde el panel docente.",
    });
  } catch {
    return out(req, {
      ok: true,
      status: "approved",
      user_id: lms.id,
      warning: "La matrícula quedó aprobada, pero no se pudo crear la contraseña. Usa “Restablecer contraseña”.",
    });
  }
});