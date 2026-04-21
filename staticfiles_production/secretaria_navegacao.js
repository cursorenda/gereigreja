// secretaria_navegacao.js
// Script para navegação entre membros na tela de edição

document.addEventListener('DOMContentLoaded', function() {
    var select = document.getElementById('navegacao-pessoa-select');
    if (select) {
        select.addEventListener('change', function() {
            if (this.value) {
                var baseUrl = select.getAttribute('data-base-url');
                if (!baseUrl) {
                    // fallback para url padrão
                    baseUrl = '/secretaria/editar_membro/';
                }
                window.location.href = baseUrl + this.value + '/';
            }
        });
    }
});
