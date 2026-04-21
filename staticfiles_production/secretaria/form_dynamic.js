// Controle dinâmico do formulário de dados cadastrais

// Exibe ou oculta o campo sub_status_inativo conforme o status selecionado
function toggleSubStatusInativo() {
    var statusField = document.getElementById('id_status_pessoa');
    var row = document.getElementById('row-sub-status-inativo');
    if (!statusField || !row) return;
    var selected = statusField.options[statusField.selectedIndex]?.text || '';
    // Normaliza: remove acentos, espaços extras e caixa
    var normalized = selected.normalize('NFD').replace(/\p{Diacritic}/gu, '').trim().toLowerCase();
    if (normalized === 'inativo') {
        row.style.display = '';
    } else {
        row.style.display = 'none';
        // Limpa seleção se não for inativo
        var subStatus = document.getElementById('id_sub_status_inativo');
        if (subStatus) subStatus.selectedIndex = 0;
    }
}

// Controla destaque visual dos campos de data quando há mudança
let valorInicialTipo = null;
let valorInicialStatus = null;

function setupDataMudancaControls() {
    const tipoField = document.getElementById('id_tipo_pessoa');
    const statusField = document.getElementById('id_status_pessoa');
    const dataTipoField = document.getElementById('id_data_mudanca_tipo');
    const dataStatusField = document.getElementById('id_data_mudanca_status');

    if (!tipoField || !statusField || !dataTipoField || !dataStatusField) return;

    // Armazena valores iniciais ao carregar a página
    valorInicialTipo = tipoField.value;
    valorInicialStatus = statusField.value;

    // Handler para Tipo de Pessoa
    tipoField.addEventListener('change', function() {
        const inputGroup = dataTipoField.closest('.input-group');
        if (this.value !== valorInicialTipo && this.value !== '') {
            dataTipoField.style.backgroundColor = '#fff3cd';
            dataTipoField.style.borderColor = '#ffc107';
            dataTipoField.style.borderWidth = '2px';
            if (inputGroup) {
                inputGroup.style.boxShadow = '0 0 0 0.2rem rgba(255, 193, 7, 0.25)';
                inputGroup.style.borderRadius = '0.375rem';
            }
        } else {
            dataTipoField.style.backgroundColor = '';
            dataTipoField.style.borderColor = '';
            dataTipoField.style.borderWidth = '';
            if (inputGroup) {
                inputGroup.style.boxShadow = '';
            }
        }
    });

    // Handler para Status da Pessoa
    statusField.addEventListener('change', function() {
        const inputGroup = dataStatusField.closest('.input-group');
        if (this.value !== valorInicialStatus && this.value !== '') {
            dataStatusField.style.backgroundColor = '#fff3cd';
            dataStatusField.style.borderColor = '#ffc107';
            dataStatusField.style.borderWidth = '2px';
            if (inputGroup) {
                inputGroup.style.boxShadow = '0 0 0 0.2rem rgba(255, 193, 7, 0.25)';
                inputGroup.style.borderRadius = '0.375rem';
            }
        } else {
            dataStatusField.style.backgroundColor = '';
            dataStatusField.style.borderColor = '';
            dataStatusField.style.borderWidth = '';
            if (inputGroup) {
                inputGroup.style.boxShadow = '';
            }
        }
    });
}

// Inicialização dos controles dinâmicos

document.addEventListener('DOMContentLoaded', function() {
    var statusField = document.getElementById('id_status_pessoa');
    if (statusField) {
        statusField.addEventListener('change', toggleSubStatusInativo);
        toggleSubStatusInativo();
    }
    setupDataMudancaControls();
});