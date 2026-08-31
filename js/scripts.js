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

    // Shrink the navbar
    navbarShrink();

    // Shrink the navbar when page is scrolled
    document.addEventListener('scroll', navbarShrink);

    // Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            rootMargin: '0px 0px -40%',
        });
    };

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

    // Sesión 5: se agrega aquí para no alterar el bloque histórico oculto
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
                <div class="course-title">De la priorización a una consulta operacional</div>
                <p class="course-description">
                    Termina pipelines y vistas en Atlas, reproduce 1.000 → 163 → 77 y el límite 0/77;
                    después diseña Cassandra desde la consulta con tutorial visual de Astra, CQL y CRUD en Python.
                </p>
            </a>`;
        courseRow.appendChild(card);
    }

    // Actualiza el mensaje visible sin reescribir el index histórico.
    document.querySelectorAll('.masthead p').forEach(p => {
        if (p.textContent.includes('sesiones 1 a 4')) {
            p.innerHTML = p.innerHTML.replace('sesiones 1 a 4', 'sesiones 1 a 5');
        }
    });

});
