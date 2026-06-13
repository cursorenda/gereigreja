// secretaria_navegacao.js
// Script para navegacao entre membros na tela de edicao

(function () {
    function buildTargetUrl(baseUrl, membroId) {
        if (!baseUrl || !membroId) return '';

        // Padrao esperado da rota: .../pessoas/0/editar/
        var replaced = String(baseUrl).replace('/0/', '/' + membroId + '/');
        if (replaced !== baseUrl) return replaced;

        // Fallback seguro: substitui 0 isolado no final do path.
        return String(baseUrl).replace(/0\/?$/, membroId + '/');
    }

    function navigateToSelected(select) {
        if (!select) return;
        var baseUrl = select.getAttribute('data-base-url') || '';
        var membroId = String(select.value || '').replace(/\D/g, '');
        if (!membroId) return;

        var targetUrl = buildTargetUrl(baseUrl, membroId);
        if (!targetUrl) return;
        if (window.location.pathname === targetUrl) return;

        window.location.assign(targetUrl);
    }

    function initNavegacaoPessoa() {
        var select = document.getElementById('navegacao-pessoa-select');
        if (!select) return;

        var btnIr = document.getElementById('btn-ir-editar');
        if (btnIr) {
            btnIr.addEventListener('click', function () {
                navigateToSelected(select);
            });
        }

        select.addEventListener('change', function () {
            navigateToSelected(select);
        });

        // Alguns navegadores/dispositivos disparam input antes do change.
        select.addEventListener('input', function () {
            navigateToSelected(select);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNavegacaoPessoa);
    } else {
        initNavegacaoPessoa();
    }
})();
