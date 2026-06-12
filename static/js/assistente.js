

// assistente.js - Lógica do assistente de ajuda/onboarding

// Array global de etapas do onboarding. Cada etapa pode ter um label e um HTML ou função de renderização.
const etapasOnboarding = [
    {
        label: 'Etapa 1 de 4',
        // Esta etapa usa uma função para renderizar HTML dinâmico com os dados do ministério
        renderHtml: function(dados) {
            return `<p><strong>Bem-vindo ao Gereigreja!</strong></p>
<p>Confira os dados do seu ministério abaixo.<br>Se algo estiver incorreto, clique em <b>Editar dados</b> para corrigir antes de prosseguir.</p>
<div class='onboarding-ministerio-box' style='background:#f8f9fa; border:1px solid #e3e6f0; border-radius:8px; padding:12px 16px; margin-bottom:10px;'>
    <b>Nome fantasia:</b> ${dados.nome_fantasia}<br>
    <b>Razão social:</b> ${dados.razao_social}<br>
    <b>CNPJ:</b> ${dados.cnpj}<br>
    <b>Responsável:</b> ${dados.responsavel}<br>
    <b>E-mail:</b> ${dados.email}<br>
    <b>Telefone:</b> ${dados.telefone}<br>
    <b>Endereço:</b> ${dados.endereco}
</div>
<a href="${dados.url_editar}" class='btn btn-outline-secondary btn-sm mb-2'>Editar dados</a>
<div style='font-size:0.95em; color:#666; margin-bottom:10px;'>
    <b>Exemplo de ministério:</b><br>
    Nome fantasia: Ministério Esperança<br>
    Razão social: Igreja Ministério Esperança Ltda<br>
</div>`;
        }
    },
    {
        label: 'Etapa 2 de 4',
        // Etapa dinâmica: mostra dados da igreja em contexto
        renderHtml: function() {
            // Lê os dados da igreja do bloco oculto
            const el = document.getElementById('onboarding-igreja-dados');
            if (!el) {
                return `<p><strong>Etapa 2: Igreja do Ministério</strong></p><p>Nenhuma igreja cadastrada para este ministério.</p>`;
            }
            const contextoLabel = el.getAttribute('data-contexto-label') || 'Igreja principal do ministério';
            const nome_igreja = el.getAttribute('data-nome-igreja') || '';
            const tipo_igreja = el.getAttribute('data-tipo-igreja') || '';
            const endereco = el.getAttribute('data-endereco') || '';
            const responsavel = el.getAttribute('data-responsavel') || '';
            const telefone = el.getAttribute('data-telefone') || '';
            const email = el.getAttribute('data-email') || '';
            const cnpj = el.getAttribute('data-cnpj') || '';
            const data_fundacao = el.getAttribute('data-data-fundacao') || '';
            return `
<p><strong>Etapa 2: Igreja do Ministério</strong></p>
<p>Confira os dados da igreja atualmente em contexto no sistema.</p>
<div class='onboarding-ministerio-box' style='background:#f8f9fa; border:1px solid #e3e6f0; border-radius:8px; padding:12px 16px; margin-bottom:10px;'>
    <b>Contexto:</b> ${contextoLabel}<br>
    <b>Nome da igreja:</b> ${nome_igreja}<br>
    <b>Tipo:</b> ${tipo_igreja}<br>
    <b>CNPJ:</b> ${cnpj}<br>
    <b>Responsável:</b> ${responsavel}<br>
    <b>E-mail:</b> ${email}<br>
    <b>Telefone:</b> ${telefone}<br>
    <b>Endereço:</b> ${endereco}<br>
    <b>Data de fundação:</b> ${data_fundacao}
</div>
<div style='font-size:0.95em; color:#666; margin-bottom:10px;'>
    <b>Exemplo de igreja:</b><br>
    Nome: Igreja Esperança<br>
    Tipo: Sede<br>
</div>`;
        }
    },
    {
        label: 'Etapa 3 de 4',
        // Etapa dinâmica: mostra resumo das configurações do sistema
        renderHtml: function() {
            // Tenta ler configurações do sistema do DOM (se disponível)
            let config = {};
            const el = document.getElementById('onboarding-configuracao-dados');
            if (el) {
                config = {
                    ebd_dia_semana: el.getAttribute('data-ebd-dia-semana') || '',
                    ebd_periodo: el.getAttribute('data-ebd-periodo') || '',
                    ebd_horario: el.getAttribute('data-ebd-horario') || '',
                    notificar_eventos: el.getAttribute('data-notificar-eventos') === 'True' ? 'Sim' : 'Não',
                    notificar_aniversarios: el.getAttribute('data-notificar-aniversarios') === 'True' ? 'Sim' : 'Não',
                };
            }
            // URL de edição da configuração do sistema (padrão Django)
            const urlEditar = '/configuracao/configuracoes/';
            return `
<p><strong>Etapa 3: Configuração do Sistema</strong></p>
<p>Veja um resumo das principais configurações do sistema para este ministério.</p>
<div class='onboarding-ministerio-box' style='background:#f8f9fa; border:1px solid #e3e6f0; border-radius:8px; padding:12px 16px; margin-bottom:10px;'>
    <b>Dia padrão da EBD:</b> ${config.ebd_dia_semana || 'Não definido'}<br>
    <b>Período da EBD:</b> ${config.ebd_periodo || 'Não definido'}<br>
    <b>Horário da EBD:</b> ${config.ebd_horario || 'Não definido'}<br>
    <b>Notificar eventos:</b> ${config.notificar_eventos || 'Não definido'}<br>
    <b>Notificar aniversários:</b> ${config.notificar_aniversarios || 'Não definido'}
</div>
<a href="${urlEditar}" class='btn btn-outline-secondary btn-sm mb-2'>Editar configuração</a>
<div style='font-size:0.95em; color:#666; margin-bottom:10px;'>
    <b>Exemplo:</b> EBD aos domingos, período trimestral, notificações ativas.<br>
</div>`;
        }
    },
    {
        label: 'Etapa 4 de 4',
        renderHtml: function() {
            // Exemplo de instrução e botões para etapa de membros
            return `
<p><strong>Etapa 4: Cadastro de Membros</strong></p>
<p>Agora é hora de cadastrar os membros da sua igreja no sistema Gereigreja.</p>
<div class='onboarding-ministerio-box' style='background:#f8f9fa; border:1px solid #e3e6f0; border-radius:8px; padding:12px 16px; margin-bottom:10px;'>
    <b>Por que cadastrar membros?</b><br>
    - Permite registrar presença, aniversários, cargos e histórico.<br>
    - Facilita a comunicação e organização da igreja.<br>
    - Habilita recursos como grupos, permissões e notificações personalizadas.<br>
</div>
<div class="d-flex gap-2 mb-2">
    <a href="/secretaria/criar_membro/" class="btn btn-success btn-sm">Cadastrar novo membro</a>
    <a href="/secretaria/lista_membros/" class="btn btn-outline-primary btn-sm">Ver lista de membros</a>
</div>
<div style='font-size:0.95em; color:#666; margin-bottom:10px;'>
    <b>Dica:</b> Você pode importar membros em lote ou cadastrar manualmente.<br>
    Após cadastrar, lembre-se de associar cargos e permissões conforme necessário.
</div>
`;
        }
    }
];

// Função para ler os dados do onboarding do DOM (vindos dos data-attributes do HTML)
function getOnboardingDados() {
    const el = document.getElementById('onboarding-dados');
    if (!el) return {};
    // Retorna um objeto com todos os dados necessários para a etapa 1
    return {
        nome_fantasia: el.getAttribute('data-nome-fantasia') || '',
        razao_social: el.getAttribute('data-razao-social') || '',
        cnpj: el.getAttribute('data-cnpj') || '',
        responsavel: el.getAttribute('data-responsavel') || '',
        email: el.getAttribute('data-email') || '',
        telefone: el.getAttribute('data-telefone') || '',
        endereco: el.getAttribute('data-endereco') || '',
        url_editar: el.getAttribute('data-url-editar') || '#'
    };
}

// Função para renderizar a etapa atual do onboarding no modal
function renderOnboardingEtapa() {
    const conteudo = document.getElementById('onboarding-conteudo-dinamico');
    const label = document.getElementById('onboarding-etapa-label');
    const btnVoltar = document.getElementById('onboarding-voltar');
    const btnAvancar = document.getElementById('onboarding-avancar');
    const dados = getOnboardingDados();
    const etapa = etapasOnboarding[etapaAtual];
    // Se a etapa tem função de renderização, usa ela, senão usa o HTML estático
    if (etapa.renderHtml) {
        conteudo.innerHTML = etapa.renderHtml(dados);
    } else {
        conteudo.innerHTML = etapa.html || '';
    }
    label.textContent = etapa.label;
    btnVoltar.disabled = etapaAtual === 0;
    btnAvancar.disabled = etapaAtual === etapasOnboarding.length - 1;
}

// Função para mostrar o modal do assistente
function showOnboardingModal() {
    document.getElementById('onboarding-assistente').style.display = 'block';
    localStorage.setItem('onboarding_minimizado', '0');
}

// Função para esconder o modal do assistente
function hideOnboardingModal() {
    document.getElementById('onboarding-assistente').style.display = 'none';
    localStorage.setItem('onboarding_minimizado', '1');
}

// Inicialização do assistente: só executa uma vez por página
document.addEventListener('DOMContentLoaded', function() {
    // Só inicializa se o assistente está presente no DOM
    if (!document.getElementById('onboarding-assistente')) return;

    // Protege contra múltiplas inicializações
    if (window._onboardingAssistenteInit) return;
    window._onboardingAssistenteInit = true;

    // Recupera a etapa atual do localStorage ou começa do zero
    window.etapaAtual = parseInt(localStorage.getItem('onboarding_etapa')) || 0;
    if (window.etapaAtual < 0 || window.etapaAtual >= etapasOnboarding.length) window.etapaAtual = 0;

    // Renderiza a etapa inicial
    renderOnboardingEtapa();

    // Botão Voltar: volta uma etapa
    document.getElementById('onboarding-voltar').onclick = function() {
        if (window.etapaAtual > 0) {
            window.etapaAtual--;
            renderOnboardingEtapa();
            localStorage.setItem('onboarding_etapa', window.etapaAtual);
        }
    };
    // Botão Avançar: avança uma etapa
    document.getElementById('onboarding-avancar').onclick = function() {
        if (window.etapaAtual < etapasOnboarding.length - 1) {
            window.etapaAtual++;
            renderOnboardingEtapa();
            localStorage.setItem('onboarding_etapa', window.etapaAtual);
        }
    };
    // Botão de minimizar
    var btnMin = document.getElementById('onboarding-minimizar');
    if (btnMin) btnMin.onclick = hideOnboardingModal;
    // Bolha flutuante para reabrir o assistente
    var bolha = document.getElementById('onboarding-bolha');
    if (bolha) bolha.onclick = showOnboardingModal;

    // Estado inicial: mostra ou esconde o assistente conforme o localStorage
    let minimizado = localStorage.getItem('onboarding_minimizado');
    if (minimizado === '0') {
        showOnboardingModal();
        localStorage.setItem('onboarding_etapa', window.etapaAtual);
    } else if (minimizado === '1') {
        hideOnboardingModal();
    } else {
        showOnboardingModal();
    }
});
