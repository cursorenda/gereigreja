// secretaria_navegacao.js
// Script para navegação entre membros na tela de edição

document.addEventListener('DOMContentLoaded', function() {
    var select = document.getElementById('navegacao-pessoa-select');
    var btnIr = document.getElementById('btn-ir-editar');
    if (btnIr && select) {
        btnIr.addEventListener('click', function() {
            var baseUrl = select.getAttribute('data-base-url');
            var membroId = select.value;
            if (membroId) {
                window.location.href = baseUrl.replace('0', membroId);
            }
        });
    }
    if (select) {
        select.addEventListener('change', function() {
            var baseUrl = select.getAttribute('data-base-url');
            var membroId = select.value;
            if (membroId) {
                window.location.href = baseUrl.replace('0', membroId);
            }
        });
    }
});
