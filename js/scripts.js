/*!
* Start Bootstrap - Creative v7.0.7 (https://startbootstrap.com/theme/creative)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-creative/blob/master/LICENSE)
*/
//
// Scripts
//

window.addEventListener('DOMContentLoaded', event => {

    // Navbar shrink function
    var navbarShrink = function () {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) {
            return;
        }
        if (window.scrollY === 0) {
            navbarCollapsible.classList.remove('navbar-shrink')
        } else {
            navbarCollapsible.classList.add('navbar-shrink')
        }

    };

    navbarShrink();
    document.addEventListener('scroll', navbarShrink);

    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            rootMargin: '0px 0px -40%',
        });
    }

    const navbarToggler = document.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(document.querySelectorAll('#navbarResponsive .nav-link'));
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (navbarToggler && window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

    // Las sesiones 5 y 6 se agregan aquí para no alterar el bloque histórico
    // de sesiones futuras que conserva index.html.
    const courseRow = document.querySelector('#portfolio .row.g-4');

    if (courseRow && !document.querySelector('[data-session="5"]')) {
        const card = document.createElement('div');
        card.className = 'col-lg-4 col-md-6';
        card.setAttribute('data-session', '5');
        card.innerHTML = `
            <a class="course-card"
               href="https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/5_Atlas_Cassandra_Query_First.ipynb"
               target="_blank" rel="noopener noreferrer">
                <div class="course-emoji" aria-hidden="true">🧱</div>
                <div class="course-category">Sesión 5 · Atlas → Cassandra</div>
                <div class="course-title">De la evidencia a la bandeja operacional</div>
                <p class="course-description">
                    Laura transforma el contexto de prensa en una vista, reproduce 1.000 → 163 → 77 y
                    contrasta una hipótesis para precisar qué evidencia aporta realmente la prensa.
                    Luego diseña Cassandra desde una consulta repetitiva y deja el proceso que abrirá S6.
                </p>
            </a>`;
        courseRow.appendChild(card);
    }

    if (courseRow && !document.querySelector('[data-session="6"]')) {
        const card = document.createElement('div');
        card.className = 'col-lg-4 col-md-6';
        card.setAttribute('data-session', '6');
        card.innerHTML = `
            <a class="course-card"
               href="https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/6_Neo4j_Contexto_Relacional.ipynb"
               target="_blank" rel="noopener noreferrer">
                <div class="course-emoji" aria-hidden="true">🕸️</div>
                <div class="course-category">Sesión 6 · Neo4j</div>
                <div class="course-title">De la fila priorizada al contexto relacional</div>
                <p class="course-description">
                    Laura abre un proceso de S5 y construye su contexto real: entidad, procesos históricos
                    y proveedores. Compara pandas con Neo4j, documenta el límite y exporta texto para la siguiente sesión.
                </p>
            </a>`;
        courseRow.appendChild(card);
    }

    // Actualiza el mensaje visible sin reescribir el index histórico.
    document.querySelectorAll('.masthead p').forEach(p => {
        if (p.textContent.includes('sesiones 1 a 4')) {
            p.innerHTML = p.innerHTML.replace('sesiones 1 a 4', 'sesiones 1 a 6');
        } else if (p.textContent.includes('sesiones 1 a 5')) {
            p.innerHTML = p.innerHTML.replace('sesiones 1 a 5', 'sesiones 1 a 6');
        }
    });

});
