// static/js/layout_custom.js
// JS para menu offcanvas mobile e seletor de tamanho de fonte

document.addEventListener('DOMContentLoaded', function() {
    // Abrir o offcanvas ao clicar no botão do menu no mobile
    var sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            if (window.innerWidth < 992) { // lg breakpoint
                e.preventDefault();
                var offcanvasSidebar = document.getElementById('offcanvasSidebar');
                if (offcanvasSidebar) {
                    var bsOffcanvas = new bootstrap.Offcanvas(offcanvasSidebar);
                    bsOffcanvas.toggle();
                }
            }
        });
    }

    // Seletor de tamanho de fonte/tela (Acessibilidade)
    var body = document.body;
    var selector = document.getElementById('fontSizeSelector');
    var fontClasses = ['font-size-normal', 'font-size-medium', 'font-size-large', 'font-size-xlarge'];
    // Valor padrão agora é 'font-size-normal'
    var saved = localStorage.getItem('fontSizeClass') || 'font-size-normal';
    body.classList.remove(...fontClasses);
    body.classList.add(saved);
    if (selector) selector.value = saved;
    if (selector) selector.addEventListener('change', function() {
        body.classList.remove(...fontClasses);
        body.classList.add(this.value);
        localStorage.setItem('fontSizeClass', this.value);
    });
});
