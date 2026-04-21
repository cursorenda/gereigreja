// Script para lógica dinâmica do campo Pastor Regional
// Exibe/oculta o campo e preenche automaticamente conforme o tipo de igreja

document.addEventListener('DOMContentLoaded', function() {
    const tipoIgreja = document.getElementById('id_tipo_igreja');
    const divPastorRegional = document.getElementById('div_pastor_regional');
    const pastorRegionalInput = document.getElementById('id_pastor_regional');
    const pastorRegionalSelector = document.getElementById('pastor_regional_selector');
    const pastorRegionalPadrao = document.getElementById('pastor_regional_padrao');

    function isCongregacao(value) {
        if (!value) return false;
        value = value.toLowerCase();
        return value.includes('congreg') || value === 'congregação' || value === 'congregacao';
    }

    function atualizarVisibilidadePastorRegional() {
        if (!tipoIgreja || !divPastorRegional) return;
        if (isCongregacao(tipoIgreja.value)) {
            divPastorRegional.style.display = '';
            if (pastorRegionalSelector && pastorRegionalSelector.value === 'regional' && pastorRegionalPadrao) {
                pastorRegionalInput.value = pastorRegionalPadrao.textContent.trim();
                pastorRegionalInput.setAttribute('readonly', 'readonly');
            } else {
                pastorRegionalInput.removeAttribute('readonly');
            }
        } else {
            divPastorRegional.style.display = 'none';
        }
    }

    if (tipoIgreja) {
        tipoIgreja.addEventListener('change', atualizarVisibilidadePastorRegional);
    }
    if (pastorRegionalSelector) {
        pastorRegionalSelector.addEventListener('change', atualizarVisibilidadePastorRegional);
    }

    // Inicialização
    atualizarVisibilidadePastorRegional();
});
