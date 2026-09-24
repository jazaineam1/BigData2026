/*!
* Start Bootstrap - Creative v7.0.7
* Ajustes BigData2026: tarjetas dinámicas S5-S8 y enlace integral S7.
*/
window.addEventListener('DOMContentLoaded', () => {
    const navbarShrink = () => {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) return;
        navbarCollapsible.classList.toggle('navbar-shrink', window.scrollY !== 0);
    };
    navbarShrink();
    document.addEventListener('scroll', navbarShrink);

    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav && window.bootstrap) {
        new bootstrap.ScrollSpy(document.body, { target: '#mainNav', rootMargin: '0px 0px -40%' });
    }

    const navbarToggler = document.querySelector('.navbar-toggler');
    document.querySelectorAll('#navbarResponsive .nav-link').forEach(item => {
        item.addEventListener('click', () => {
            if (navbarToggler && window.getComputedStyle(navbarToggler).display !== 'none') navbarToggler.click();
        });
    });

    const courseRow = document.querySelector('#portfolio .row.g-4');
    const addCard = (selector, attrs, html) => {
        if (!courseRow || document.querySelector(selector)) return;
        const card = document.createElement('div');
        card.className = 'col-lg-4 col-md-6';
        Object.entries(attrs).forEach(([k, v]) => card.setAttribute(k, v));
        card.innerHTML = html;
        courseRow.appendChild(card);
    };

    addCard('[data-session="5"]', {'data-session': '5'}, `
        <a class="course-card" href="https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/5_Atlas_Cassandra_Query_First.ipynb" target="_blank" rel="noopener noreferrer">
            <div class="course-emoji" aria-hidden="true">🧱</div>
            <div class="course-category">Sesión 5 · Atlas → Cassandra</div>
            <div class="course-title">De la evidencia a la bandeja operacional</div>
            <p class="course-description">Laura transforma el contexto de prensa en una vista, reproduce la priorización y diseña Cassandra desde una consulta repetitiva.</p>
        </a>`);

    addCard('[data-session="6"]', {'data-session': '6'}, `
        <a class="course-card" href="https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/6_Neo4j_Contexto_Relacional.ipynb" target="_blank" rel="noopener noreferrer">
            <div class="course-emoji" aria-hidden="true">🕸️</div>
            <div class="course-category">Sesión 6 · Neo4j</div>
            <div class="course-title">De la fila priorizada al contexto relacional</div>
            <p class="course-description">Laura abre un proceso de S5 y construye su contexto real con Neo4j y Cypher; exporta el texto que abre la S7.</p>
        </a>`);

    addCard('[data-session="7"]', {'data-session': '7'}, `
        <a class="course-card" href="Presentaciones/s07-clase-completa.html">
            <div class="course-emoji" aria-hidden="true">🔎</div>
            <div class="course-category">Sesión 7 · Elasticsearch y BM25</div>
            <div class="course-title">Clase completa: del vecindario al texto</div>
            <p class="course-description">Presentación, cuaderno Colab, guía de despliegue, checklist, ruta BM25 local y Elastic Cloud opcional.</p>
        </a>`);

    addCard('[data-workshop="control-1"]', {'data-workshop': 'control-1'}, `
        <a class="course-card" href="https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/Taller_Control_1.ipynb" target="_blank" rel="noopener noreferrer">
            <div class="course-emoji" aria-hidden="true">🧪</div>
            <div class="course-category">Sesión 8 · Primer taller NoSQL</div>
            <div class="course-title">De 6 CSV a Atlas, Cassandra y Neo4j</div>
            <p class="course-description">Primer taller evaluativo del bloque NoSQL con MongoDB Atlas, Cassandra y Neo4j.</p>
        </a>`);

    // Si S7 ya está escrita de forma estática en index.html, actualiza el destino al hub integral.
    const s7 = document.querySelector('[data-session="7"] a.course-card');
    if (s7) s7.setAttribute('href', 'Presentaciones/s07-clase-completa.html');

    document.querySelectorAll('.masthead p').forEach(p => {
        ['sesiones 1 a 4', 'sesiones 1 a 5', 'sesiones 1 a 6'].forEach(old => {
            if (p.textContent.includes(old)) p.innerHTML = p.innerHTML.replace(old, 'sesiones 1 a 7');
        });
    });
});
