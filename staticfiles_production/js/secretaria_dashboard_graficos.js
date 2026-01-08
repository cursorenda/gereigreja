// Chart.js - Inicialização dos gráficos do dashboard da Secretaria Gereigreja
// Certifique-se de que este script é incluído após os scripts JSON e após o Chart.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('JS carregado: secretaria_dashboard_graficos.js');
    function getJsonData(id) {
        const el = document.getElementById(id);
        if (!el) return [];
        try {
            return JSON.parse(el.textContent);
        } catch {
            return [];
        }
    }

    // Gráfico de Linha: Evolução de Pessoas (12 meses)
    const ctxEvolucao = document.getElementById('evolucaoMembrosChart');
    if (ctxEvolucao) {
        new Chart(ctxEvolucao.getContext('2d'), {
            type: 'line',
            data: {
                labels: getJsonData('evolucao-meses-labels'),
                datasets: [
                    {
                        label: 'Membros',
                        data: getJsonData('evolucao-membros'),
                        borderColor: '#4e73df',
                        backgroundColor: 'rgba(78,115,223,0.12)',
                        fill: true,
                        tension: 0.3
                    },
                    {
                        label: 'Congregados',
                        data: getJsonData('evolucao-congregados'),
                        borderColor: '#36b9cc',
                        backgroundColor: 'rgba(54,185,204,0.12)',
                        fill: true,
                        tension: 0.3
                    },
                    {
                        label: 'Novos Convertidos',
                        data: getJsonData('evolucao-novos-convertidos'),
                        borderColor: '#f953c6',
                        backgroundColor: 'rgba(249,83,198,0.12)',
                        fill: true,
                        tension: 0.3
                    },
                    {
                        label: 'Visitantes',
                        data: getJsonData('evolucao-visitantes'),
                        borderColor: '#f6c23e',
                        backgroundColor: 'rgba(246,194,62,0.12)',
                        fill: true,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' },
                    title: { display: false }
                },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // Gráfico de Pizza: Distribuição de Pessoas por Tipo
    const ctxPie = document.getElementById('grafico2');
    if (ctxPie) {
        new Chart(ctxPie.getContext('2d'), {
            type: 'pie',
            data: {
                labels: getJsonData('pie-labels-data'),
                datasets: [{
                    data: getJsonData('pie-values-data'),
                    backgroundColor: [
                        '#4e73df', '#36b9cc', '#f953c6', '#f6c23e', '#1cc88a', '#e74a3b', '#858796', '#fd7e14', '#20c997'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' },
                    title: { display: false }
                }
            }
        });
    }

    // Gráfico de Barras: Pessoas por Status
    const ctxStatus = document.getElementById('statusChart');
    if (ctxStatus) {
        new Chart(ctxStatus.getContext('2d'), {
            type: 'bar',
            data: {
                labels: getJsonData('status-labels-data'),
                datasets: [{
                    label: 'Quantidade',
                    data: getJsonData('status-values-data'),
                    backgroundColor: '#4e73df'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: { display: false }
                },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // Gráfico de Barras: Pessoas por Gênero
    const ctxGenero = document.getElementById('generoChart');
    if (ctxGenero) {
        new Chart(ctxGenero.getContext('2d'), {
            type: 'bar',
            data: {
                labels: getJsonData('genero-labels-data'),
                datasets: [{
                    label: 'Quantidade',
                    data: getJsonData('genero-values-data'),
                    backgroundColor: '#1cc88a'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: { display: false }
                },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // Gráfico de Barras: Pessoas por Faixa Etária
    const ctxFaixa = document.getElementById('faixaEtariaChart');
    if (ctxFaixa) {
        new Chart(ctxFaixa.getContext('2d'), {
            type: 'bar',
            data: {
                labels: getJsonData('faixa-labels-data'),
                datasets: [{
                    label: 'Quantidade',
                    data: getJsonData('faixa-values-data'),
                    backgroundColor: '#f6c23e'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: { display: false }
                },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // Gráfico de Barras: Participação por Categoria de Evento
    const ctxCategoria = document.getElementById('categoriaEventoChart');
    if (ctxCategoria) {
        new Chart(ctxCategoria.getContext('2d'), {
            type: 'bar',
            data: {
                labels: getJsonData('categoria-evento-labels-data'),
                datasets: [{
                    label: 'Quantidade',
                    data: getJsonData('categoria-evento-values-data'),
                    backgroundColor: '#6f42c1'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: { display: false }
                },
                scales: { y: { beginAtZero: true } }
            }
        });
    }
});
