// secretaria/cnpj_igreja.js
// Alterna entre usar o CNPJ do ministério ou informar um CNPJ próprio para a igreja


// secretaria/cnpj_igreja.js
// Alterna entre usar o CNPJ do ministério ou informar um CNPJ próprio para a igreja (usando o seletor)
document.addEventListener('DOMContentLoaded', function() {
    const cnpjSelector = document.getElementById('cnpj_selector');
    const cnpjMinisterioValor = document.getElementById('cnpj_ministerio_valor');
    const cnpjInput = document.getElementById('id_cnpj');
    if (!cnpjSelector || !cnpjInput) return;

    function toggleCnpjField() {
        if (cnpjSelector.value === 'ministerio') {
            cnpjInput.value = cnpjMinisterioValor ? cnpjMinisterioValor.textContent.trim() : '';
            cnpjInput.setAttribute('readonly', 'readonly');
        } else {
            cnpjInput.value = '';
            cnpjInput.removeAttribute('readonly');
        }
        // Dispara o evento input para garantir a máscara
        cnpjInput.dispatchEvent(new Event('input'));
    }
    cnpjSelector.addEventListener('change', toggleCnpjField);
    toggleCnpjField(); // Inicializa corretamente
});
