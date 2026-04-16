// secretaria/cnpj_igreja.js
// Alterna entre usar o CNPJ do ministério ou informar um CNPJ próprio para a igreja

document.addEventListener('DOMContentLoaded', function() {
    var checkbox = document.getElementById('usar_cnpj_ministerio');
    var cnpjInput = document.getElementById('id_cnpj');
    var cnpjMinisterio = document.getElementById('cnpj_ministerio_valor');
    if (!checkbox || !cnpjInput || !cnpjMinisterio) return;

    function toggleCnpj() {
        if (checkbox.checked) {
            cnpjInput.value = cnpjMinisterio.textContent.trim();
            cnpjInput.readOnly = true;
            cnpjInput.classList.add('bg-light');
        } else {
            cnpjInput.readOnly = false;
            cnpjInput.classList.remove('bg-light');
        }
    }
    checkbox.addEventListener('change', toggleCnpj);
    toggleCnpj(); // Executa ao carregar
});
