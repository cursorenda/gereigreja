// Bloqueia status 'Em Disciplina' e 'Desligado' para tipos que não sejam 'Membro' ou 'Obreiro'
document.addEventListener('DOMContentLoaded', function() {
    const tipoPessoa = document.getElementById('id_tipo_pessoa');
    const statusPessoa = document.getElementById('id_status_pessoa');
    if (!tipoPessoa || !statusPessoa) return;

    function updateStatusOptions() {
        const tipo = tipoPessoa.options[tipoPessoa.selectedIndex]?.text?.toLowerCase() || '';
        Array.from(statusPessoa.options).forEach(option => {
            const status = option.text.toLowerCase();
            if ((status.includes('disciplina') || status.includes('desligado')) && !(tipo.includes('membro') || tipo.includes('obreiro'))) {
                option.disabled = true;
                option.style.display = 'none';
                if (option.selected) statusPessoa.selectedIndex = 0;
            } else {
                option.disabled = false;
                option.style.display = '';
            }
        });
    }

    tipoPessoa.addEventListener('change', updateStatusOptions);
    // Executa ao carregar
    updateStatusOptions();
});