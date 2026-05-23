const activarMensajes = () => {
    const mensajes = document.querySelectorAll('.mensaje');
    mensajes.forEach((mensaje) => {
        window.setTimeout(() => {
            mensaje.style.opacity = '0';
            mensaje.style.transform = 'translateY(-8px)';
        }, 3400);
    });
};

const activarSuperficiesPrivadas = () => {
    const superficiesInteractivas = document.querySelectorAll(
        '.tarjeta-registro, .tarjeta-indicador, .panel-contenido'
    );

    superficiesInteractivas.forEach((superficie) => {
        superficie.addEventListener('pointermove', (evento) => {
            const rectangulo = superficie.getBoundingClientRect();
            const posicionHorizontal = evento.clientX - rectangulo.left;
            const posicionVertical = evento.clientY - rectangulo.top;
            superficie.style.setProperty('--posicion-horizontal', `${posicionHorizontal}px`);
            superficie.style.setProperty('--posicion-vertical', `${posicionVertical}px`);
        });
    });
};

const activarCabeceraPublica = () => {
    const cabeceraPublica = document.querySelector('.cabecera-publica');
    if (!cabeceraPublica) return;

    const revisarDesplazamiento = () => {
        cabeceraPublica.classList.toggle('cabecera-publica-activa', window.scrollY > 12);
    };

    revisarDesplazamiento();
    window.addEventListener('scroll', revisarDesplazamiento, { passive: true });
};

const activarAnimacionesPublicas = () => {
    if (!window.AOS) return;

    window.AOS.init({
        duration: 720,
        easing: 'ease-out-cubic',
        once: true,
        offset: 80,
    });
};

const activarContadoresPublicos = () => {
    const numeros = document.querySelectorAll('.numero-publico[data-valor]');
    if (!numeros.length || !window.IntersectionObserver) return;

    const pintarNumero = (elemento, progreso) => {
        const valorFinal = Number(elemento.dataset.valor || 0);
        const valorActual = Math.round(valorFinal * progreso);
        elemento.textContent = valorFinal === 100 ? `${valorActual}%` : valorActual;
    };

    const animarNumero = (elemento) => {
        const inicio = performance.now();
        const duracion = 900;

        const avanzar = (momento) => {
            const progreso = Math.min((momento - inicio) / duracion, 1);
            const progresoSuave = 1 - Math.pow(1 - progreso, 3);
            pintarNumero(elemento, progresoSuave);

            if (progreso < 1) {
                window.requestAnimationFrame(avanzar);
            }
        };

        window.requestAnimationFrame(avanzar);
    };

    const observador = new IntersectionObserver((entradas) => {
        entradas.forEach((entrada) => {
            if (!entrada.isIntersecting) return;
            animarNumero(entrada.target);
            observador.unobserve(entrada.target);
        });
    }, { threshold: .45 });

    numeros.forEach((numero) => observador.observe(numero));
};

const activarMovimientoPublico = () => {
    const tarjetas = document.querySelectorAll(
        '.tarjeta-servicio-publica, .paso-publico, .imagen-portada-publica, .imagen-seccion-publica'
    );

    tarjetas.forEach((tarjeta) => {
        tarjeta.addEventListener('pointermove', (evento) => {
            const rectangulo = tarjeta.getBoundingClientRect();
            const posicionHorizontal = (evento.clientX - rectangulo.left) / rectangulo.width - .5;
            const posicionVertical = (evento.clientY - rectangulo.top) / rectangulo.height - .5;
            tarjeta.style.transform = `translateY(-4px) rotateX(${posicionVertical * -2}deg) rotateY(${posicionHorizontal * 2}deg)`;
        });

        tarjeta.addEventListener('pointerleave', () => {
            tarjeta.style.transform = '';
        });
    });
};

const activarSelectoresAutocompletables = () => {
    if (!window.TomSelect) return;

    const selectores = document.querySelectorAll('select.selector-autocomplete');
    selectores.forEach((selector) => {
        if (selector.tomselect) return;

        const placeholder = selector.dataset.placeholder || 'Buscar opcion...';
        new window.TomSelect(selector, {
            allowEmptyOption: true,
            create: false,
            maxOptions: 200,
            placeholder,
            searchField: ['text'],
            sortField: {
                field: 'text',
                direction: 'asc',
            },
            render: {
                no_results: () => '<div class="no-results">Sin resultados</div>',
            },
        });
    });
};

document.addEventListener('DOMContentLoaded', () => {
    activarMensajes();
    activarSuperficiesPrivadas();
    activarCabeceraPublica();
    activarAnimacionesPublicas();
    activarContadoresPublicos();
    activarMovimientoPublico();
    activarSelectoresAutocompletables();
});
