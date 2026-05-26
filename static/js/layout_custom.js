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
    var cycleButton = document.getElementById('fontSizeCycleButton');
    var statusEl = document.getElementById('fontSizeStatus');
    var fontClasses = ['font-size-normal', 'font-size-medium', 'font-size-large', 'font-size-xlarge'];
    var fontClassLabels = {
        'font-size-normal': 'Normal',
        'font-size-medium': 'Médio',
        'font-size-large': 'Grande',
        'font-size-xlarge': 'Extra grande'
    };
    var statusTimer = null;

    function normalizeFontClass(value) {
        return fontClasses.indexOf(value) >= 0 ? value : 'font-size-normal';
    }

    function setStatusVisible(isVisible) {
        if (!statusEl) {
            return;
        }
        if (isVisible) {
            statusEl.classList.add('is-visible');
        } else {
            statusEl.classList.remove('is-visible');
        }
    }

    function showStatusTemporarily() {
        setStatusVisible(true);
        if (statusTimer) {
            clearTimeout(statusTimer);
        }
        statusTimer = setTimeout(function() {
            setStatusVisible(false);
        }, 1500);
    }

    function updateStatusText(fontClass) {
        if (!statusEl) {
            return;
        }
        statusEl.textContent = fontClassLabels[fontClass] || 'Normal';
    }

    function applyFontClass(nextClass) {
        var safeClass = normalizeFontClass(nextClass);
        body.classList.remove(...fontClasses);
        body.classList.add(safeClass);
        localStorage.setItem('fontSizeClass', safeClass);
        if (selector) {
            selector.value = safeClass;
        }
        if (cycleButton) {
            cycleButton.setAttribute('aria-label', 'Tamanho da fonte: ' + (fontClassLabels[safeClass] || 'Normal') + '. Clique para alterar');
            cycleButton.title = 'Tamanho da fonte: ' + (fontClassLabels[safeClass] || 'Normal');
        }
        updateStatusText(safeClass);
        showStatusTemporarily();
    }

    function cycleFontClass(step) {
        var current = normalizeFontClass(localStorage.getItem('fontSizeClass') || body.className.split(' ').find(function(c) {
            return fontClasses.indexOf(c) >= 0;
        }) || 'font-size-normal');
        var currentIndex = fontClasses.indexOf(current);
        var direction = step || 1;
        var nextIndex = (currentIndex + direction + fontClasses.length) % fontClasses.length;
        applyFontClass(fontClasses[nextIndex]);
    }

    // Valor padrão agora é 'font-size-normal'
    var saved = normalizeFontClass(localStorage.getItem('fontSizeClass') || 'font-size-normal');
    applyFontClass(saved);

    if (selector) {
        selector.addEventListener('change', function() {
            applyFontClass(this.value);
        });
    }

    if (cycleButton) {
        cycleButton.addEventListener('click', function(e) {
            e.preventDefault();
            cycleFontClass(e.shiftKey ? -1 : 1);
        });

        cycleButton.addEventListener('mouseenter', function() {
            var current = normalizeFontClass(localStorage.getItem('fontSizeClass') || 'font-size-normal');
            updateStatusText(current);
            setStatusVisible(true);
        });

        cycleButton.addEventListener('mouseleave', function() {
            if (statusTimer) {
                clearTimeout(statusTimer);
                statusTimer = null;
            }
            setStatusVisible(false);
        });

        cycleButton.addEventListener('focus', function() {
            var current = normalizeFontClass(localStorage.getItem('fontSizeClass') || 'font-size-normal');
            updateStatusText(current);
            setStatusVisible(true);
        });

        cycleButton.addEventListener('blur', function() {
            if (statusTimer) {
                clearTimeout(statusTimer);
                statusTimer = null;
            }
            setStatusVisible(false);
        });
    }
});
