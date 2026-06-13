// Controle dinâmico do formulário de dados cadastrais

function normalizeText(text) {
    if (!text) return '';
    return text
        .toString()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .trim()
        .toLowerCase();
}

// Exibe ou oculta o campo sub_status_inativo conforme o status selecionado
function toggleSubStatusInativo() {
    var statusField = document.getElementById('id_status_pessoa');
    var row = document.getElementById('row-sub-status-inativo');
    if (!statusField || !row) return;
    var selected = '';
    if (statusField.selectedIndex >= 0 && statusField.options[statusField.selectedIndex]) {
        selected = statusField.options[statusField.selectedIndex].text || '';
    }
    // Normaliza: remove acentos, espaços extras e caixa
    var normalized = normalizeText(selected);
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

function toggleGrauEclesiastico() {
    var tipoField = document.getElementById('id_tipo_pessoa');
    var row = document.getElementById('row-grau-eclesiastico');
    var grauField = document.getElementById('id_grau_eclesiastico');
    if (!tipoField || !row || !grauField) return;

    var selected = '';
    if (tipoField.selectedIndex >= 0 && tipoField.options[tipoField.selectedIndex]) {
        selected = tipoField.options[tipoField.selectedIndex].text || '';
    }
    var normalized = normalizeText(selected);
    var isMembro = normalized.indexOf('membro') !== -1;

    if (isMembro) {
        row.style.display = '';
        grauField.disabled = false;
    } else {
        row.style.display = 'none';
        grauField.value = '';
        grauField.disabled = true;
    }
}

function toggleCamposCasamentoCadastro() {
    var estadoCivilField = document.getElementById('id_estado_civil');
    var conjugeField = document.getElementById('id_conjuge');
    var dataCasamentoField = document.getElementById('id_data_casamento');
    var rowConjuge = document.getElementById('row-conjuge-cadastro');
    var rowDataCasamento = document.getElementById('row-data-casamento-cadastro');

    if (!estadoCivilField || !conjugeField || !dataCasamentoField || !rowConjuge || !rowDataCasamento) return;

    var selected = '';
    if (estadoCivilField.selectedIndex >= 0 && estadoCivilField.options[estadoCivilField.selectedIndex]) {
        selected = estadoCivilField.options[estadoCivilField.selectedIndex].text || '';
    }
    var normalized = normalizeText(selected);
    var isCasado = normalized === 'casado';

    rowConjuge.style.display = isCasado ? '' : 'none';
    rowDataCasamento.style.display = isCasado ? '' : 'none';

    conjugeField.disabled = !isCasado;
    dataCasamentoField.disabled = !isCasado;

    if (!isCasado) {
        conjugeField.value = '';
        dataCasamentoField.value = '';
    }
}

function toggleCamposPremiumMinisteriais() {
    var tipoField = document.getElementById('id_tipo_pessoa');
    var grauField = document.getElementById('id_grau_eclesiastico');
    var premiumBlock = document.getElementById('bloco-premium-ministerio');
    var rowDadosMinisteriais = document.getElementById('row-dados-ministeriais-premium');
    var stateBadge = document.getElementById('premium-ministerial-state');
    var flowSummary = document.getElementById('premium-ministerial-summary-flow');
    var credencialSummary = document.getElementById('premium-ministerial-summary-credencial');
    var convencaoSummary = document.getElementById('premium-ministerial-summary-convencao');
    var numeroCredencial = document.getElementById('id_numero_credencial');
    var dataConsagracao = document.getElementById('id_data_consagracao');
    var convencao = document.getElementById('id_convencao');
    var observacoesMinisteriais = document.getElementById('id_observacoes_ministeriais');

    if (!tipoField || !premiumBlock) return;

    var tipoSelecionado = '';
    if (tipoField.selectedIndex >= 0 && tipoField.options[tipoField.selectedIndex]) {
        tipoSelecionado = tipoField.options[tipoField.selectedIndex].text || '';
    }
    var tipoNormalizado = normalizeText(tipoSelecionado);
    var isMembro = tipoNormalizado.indexOf('membro') !== -1;

    premiumBlock.style.display = isMembro ? '' : 'none';
    premiumBlock.setAttribute('aria-hidden', isMembro ? 'false' : 'true');
    if (isMembro) {
        premiumBlock.classList.remove('premium-ministerial-reveal');
        void premiumBlock.offsetWidth;
        premiumBlock.classList.add('premium-ministerial-reveal');
    }

    var premiumFields = premiumBlock.querySelectorAll('input, select, textarea');
    premiumFields.forEach(function (field) {
        field.disabled = !isMembro;
    });

    if (!rowDadosMinisteriais) return;
    var isObreiro = isMembro && grauField && grauField.value && grauField.value !== 'membro_comum';
    rowDadosMinisteriais.style.display = isObreiro ? '' : 'none';
    rowDadosMinisteriais.setAttribute('aria-hidden', isObreiro ? 'false' : 'true');

    [numeroCredencial, dataConsagracao, convencao, observacoesMinisteriais].forEach(function (field) {
        if (field) field.disabled = !isObreiro;
    });

    if (stateBadge) {
        stateBadge.classList.remove('state-member', 'state-worker');
        if (!isMembro) {
            stateBadge.textContent = 'Nao aplicavel';
        } else if (isObreiro) {
            stateBadge.textContent = 'Membro obreiro';
            stateBadge.classList.add('state-worker');
        } else {
            stateBadge.textContent = 'Membro comum';
            stateBadge.classList.add('state-member');
        }
    }

    if (flowSummary) {
        flowSummary.textContent = !isMembro
            ? 'Fluxo: Nao aplicavel'
            : (isObreiro ? 'Fluxo: Membresia + ministerio completo' : 'Fluxo: Membresia basica');
    }

    if (credencialSummary) {
        var credencialValue = numeroCredencial ? String(numeroCredencial.value || '').trim() : '';
        credencialSummary.textContent = 'Credencial: ' + (credencialValue || '--');
    }

    if (convencaoSummary) {
        var convencaoValue = convencao ? String(convencao.value || '').trim() : '';
        convencaoSummary.textContent = 'Convencao: ' + (convencaoValue || '--');
    }
}

// Inicialização dos controles dinâmicos

document.addEventListener('DOMContentLoaded', function() {
    var statusField = document.getElementById('id_status_pessoa');
    var tipoField = document.getElementById('id_tipo_pessoa');
    var estadoCivilField = document.getElementById('id_estado_civil');
    if (statusField) {
        statusField.addEventListener('change', toggleSubStatusInativo);
        toggleSubStatusInativo();
    }
    if (tipoField) {
        tipoField.addEventListener('change', toggleGrauEclesiastico);
        tipoField.addEventListener('change', toggleCamposPremiumMinisteriais);
        toggleGrauEclesiastico();
    }
    var grauField = document.getElementById('id_grau_eclesiastico');
    if (grauField) {
        grauField.addEventListener('change', toggleCamposPremiumMinisteriais);
    }
    var numeroCredencial = document.getElementById('id_numero_credencial');
    if (numeroCredencial) {
        numeroCredencial.addEventListener('input', toggleCamposPremiumMinisteriais);
    }
    var convencao = document.getElementById('id_convencao');
    if (convencao) {
        convencao.addEventListener('input', toggleCamposPremiumMinisteriais);
    }
    if (estadoCivilField) {
        estadoCivilField.addEventListener('change', toggleCamposCasamentoCadastro);
        toggleCamposCasamentoCadastro();
    }
    setupDataMudancaControls();
    toggleCamposPremiumMinisteriais();
});