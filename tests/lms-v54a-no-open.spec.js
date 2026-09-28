const { test, expect } = require('@playwright/test');

// V54-A · El estudiante no escribe respuestas abiertas. Estas pruebas ejecutan las páginas de
// verdad (navegador + backend simulado) y miran lo que el estudiante ve y lo que se envía.

const STUDENT = { id: 'u-self', username: 'estudiante.qa', display_name: 'Estudiante QA', role: 'student' };
const TEACHER = { id: 'u-doc', username: 'docente.qa', display_name: 'Docente QA', role: 'teacher' };
const RUN = { id: 'run-1', title: 'Big Data 2026-2S' };

async function seedAuth(page, user) {
  await page.addInitScript(u => {
    const auth = { token: 'v54a-qa', expires_at: '2099-12-31T23:59:59Z', auth_session_id: 'qa', user: u };
    localStorage.setItem('lms.bigdata.v2', JSON.stringify(auth));
    sessionStorage.setItem('lms.bigdata.v2', JSON.stringify(auth));
  }, user);
}

// Simula las Edge Functions. `core` responde por acción y guarda cada POST en `sent`.
async function mockBackend(page, user, core) {
  const sent = [];
  await page.route('**/functions/v1/**', async route => {
    const req = route.request(), u = new URL(req.url());
    if (u.pathname.endsWith('/bigdata-lms-core')) {
      const body = req.method() === 'POST' ? (req.postDataJSON() || {}) : { action: u.searchParams.get('action') };
      if (req.method() === 'POST') sent.push(body);
      const out = core[body.action];
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(out ? out : { ok: true }) });
    }
    return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ ok: true, viewer: user, run: RUN }) });
  });
  return sent;
}

const collaborationModel = () => ({
  viewer: STUDENT, run: RUN,
  groups: [{ id: 'g1', name: 'Equipo 1', description: '' }],
  members: [{ group_id: 'g1', user_id: 'u-self', role: 'member' }],
  users: [{ id: 'u-self', display_name: 'Estudiante QA' }],
  settings: [{ assignment_id: 'a1' }, { assignment_id: 'a2' }],
  assignments: [
    { id: 'a1', code: 'bd-entrega', title: 'Entrega del equipo', max_score: 100, due_at: null },
    { id: 'a2', code: 'bd-s08-control', title: 'Taller de control', max_score: 100, due_at: null }
  ],
  group_submissions: [{ id: 's1', assignment_id: 'a1', group_id: 'g1', attempt: 1, status: 'submitted', score: null, submitted_at: '2026-10-01T23:30:00Z' }],
  threads: [], posts: [], mentions: [],
  peer_targets: [{
    id: 'p1', assignment: { title: 'Evidencia de otro equipo' }, artifact_type: 'url', artifact: { url: 'https://example.com/e' },
    peer_setting: { peer_rubric: [{ code: 'c1', title: 'Claridad', max: 5 }, { code: 'c2', title: 'Rigor', max: 5 }] }
  }]
});

test('colaboración: el estudiante no tiene campos de texto y envía solo opciones', async ({ page }) => {
  await seedAuth(page, STUDENT);
  const sent = await mockBackend(page, STUDENT, { collaboration: collaborationModel() });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/lms/collaboration.html');
  await expect(page.getByText('Equipo 1').first()).toBeVisible();

  await page.getByRole('button', { name: 'Entregas grupales' }).click();
  await expect(page.locator('textarea')).toHaveCount(0);
  await expect(page.getByText('Enviado').first()).toBeVisible();           // estado en español
  await expect(page.getByText('Este taller no se entrega aquí')).toBeVisible(); // el TC1 no tiene formulario
  await expect(page.locator('[data-group-submit^="a2|"]')).toHaveCount(0);

  const form = page.locator('[data-group-submit^="a1|"]');
  await form.locator('input[name=url]').fill('https://drive.google.com/x');
  await form.locator('select[name=contribution_role]').selectOption('code');
  page.once('dialog', d => d.accept());
  await form.getByRole('button', { name: /Enviar nuevo intento/ }).click();
  await expect.poll(() => sent.some(b => b.action === 'group_submit')).toBeTruthy();
  const g = sent.find(b => b.action === 'group_submit');
  expect(g).toMatchObject({ artifact_type: 'url', url: 'https://drive.google.com/x', contribution_role: 'code' });
  expect(g).not.toHaveProperty('text');
  expect(g).not.toHaveProperty('contribution_text');

  await page.getByRole('button', { name: 'Revisión por pares' }).click();
  await expect(page.locator('textarea')).toHaveCount(0);
  // El envío grupal recarga la página y redibuja este formulario: se reintenta si quedó vacío.
  const peer = page.locator('[data-peer="p1"]');
  await expect(async () => {
    await peer.locator('[data-peer-code=c1]').fill('4');
    await peer.locator('[data-peer-code=c2]').fill('3');
    await peer.locator('select[name=weakest_criterion]').selectOption('c2');
    await peer.getByRole('button', { name: 'Enviar revisión' }).click();
    expect(sent.some(b => b.action === 'submit_peer_review')).toBeTruthy();
  }).toPass({ timeout: 10000 });
  const r = sent.find(b => b.action === 'submit_peer_review');
  expect(r).toMatchObject({ weakest_criterion: 'c2', rubric_scores: { c1: 4, c2: 3 } });
  expect(r).not.toHaveProperty('feedback');

  await page.getByRole('button', { name: 'Comunicados del docente' }).click();
  await expect(page.getByText('Solo lectura')).toBeVisible();
  await expect(page.locator('#threadForm, [data-post]')).toHaveCount(0);
  await expect(page.locator('textarea')).toHaveCount(0);
});

test('entregas: no hay opción de texto y los quizzes no muestran una falsa alarma', async ({ page }) => {
  await seedAuth(page, STUDENT);
  await mockBackend(page, STUDENT, {
    assignments: {
      viewer: STUDENT, run: RUN,
      assignments: [
        { id: 'a1', code: 'bd-tarea', title: 'Tarea con URL', session_number: 5, allowed_types: ['text', 'url'], can_submit: true, attempts: [], attempts_used: 0, effective_max_attempts: 1, max_score: 100 },
        { id: 'a2', code: 'bd-quiz', title: 'Quiz de la sesión', session_number: 7, allowed_types: ['evidence'], can_submit: true, attempts: [], attempts_used: 0, effective_max_attempts: 1, max_score: 10 }
      ]
    }
  });
  await page.goto('/lms/assignments.html');
  await expect(page.getByText('Tarea con URL')).toBeVisible();
  await expect(page.locator('textarea')).toHaveCount(0);
  await expect(page.locator('option', { hasText: 'Texto' })).toHaveCount(0);
  await expect(page.locator('form[data-submit="a1"] input[name=url]')).toHaveAttribute('type', 'url');
  await expect(page.getByText('Se registra automáticamente')).toBeVisible();
  await expect(page.getByText('Avisa a tu docente')).toHaveCount(0);
});

test('colaboración docente: publica comunicados y responde con texto', async ({ page }) => {
  await seedAuth(page, TEACHER);
  const sent = await mockBackend(page, TEACHER, {
    teacher_collaboration: {
      viewer: TEACHER, run: RUN, groups: [], members: [], settings: [], assignments: [], group_submissions: [], students: [],
      users: [], reviews: [], contributions: [], posts: [],
      threads: [{ id: 't1', title: 'Aviso previo', pinned: false, locked: false, session_number: 8 }]
    }
  });
  await page.goto('/lms/teacher-collaboration.html');
  await page.getByRole('button', { name: 'Discusión' }).click();
  const announce = page.locator('#announceForm');
  await announce.locator('input[name=title]').fill('Traigan su manifest');
  await announce.locator('textarea[name=body]').fill('Validen el manifest antes de la clase.');
  await announce.locator('select[name=session_number]').selectOption('8');
  await announce.getByRole('button', { name: 'Publicar comunicado' }).click();
  await expect.poll(() => sent.some(b => b.action === 'create_thread')).toBeTruthy();
  expect(sent.find(b => b.action === 'create_thread')).toMatchObject({ title: 'Traigan su manifest', session_number: '8' });

  // Tras publicar, la página recarga y vuelve a dibujar las conversaciones: si eso ocurre entre
  // escribir y enviar, el campo nuevo queda vacío y el navegador bloquea el envío (required).
  // Por eso se reintenta escribir y enviar hasta que el envío realmente ocurre.
  const reply = page.locator('[data-post="t1"]');
  await expect(async () => {
    await reply.locator('textarea[name=body]').fill('Sí, hasta el miércoles.');
    await reply.getByRole('button', { name: 'Responder' }).click();
    expect(sent.some(b => b.action === 'post_discussion')).toBeTruthy();
  }).toPass({ timeout: 10000 });
  expect(sent.find(b => b.action === 'post_discussion')).toMatchObject({ thread_id: 't1' });
});
