document.addEventListener('DOMContentLoaded', () => {
    const mensajes = document.querySelectorAll('.mensaje');
    mensajes.forEach((mensaje) => {
        window.setTimeout(() => {
            mensaje.style.opacity = '0';
            mensaje.style.transform = 'translateY(-8px)';
        }, 3400);
    });

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
});
