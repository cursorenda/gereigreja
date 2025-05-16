document.addEventListener("DOMContentLoaded", function() {
    // Gráfico de Status dos Membros
    var ctxStatus = document.getElementById("statusChart").getContext("2d");
    var statusChart = new Chart(ctxStatus, {
        type: 'pie',
        data: {
            labels: ["Membros", "Congregados", "Disciplina"],
            datasets: [{
                data: [
                    statusData.membros_count,
                    statusData.congregados_count,
                    statusData.disciplina_count
                ],
                backgroundColor: ['#007bff', '#dc3545', '#ffc107'],
            }],
        },
        options: {
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });

    // Gráfico de Gênero dos Membros
    var ctxGenero = document.getElementById("generoChart").getContext("2d");
    var generoChart = new Chart(ctxGenero, {
        type: 'pie',
        data: {
            labels: ["Homens", "Mulheres"],
            datasets: [{
                data: [
                    generoData.homens_count,
                    generoData.mulheres_count
                ],
                backgroundColor: ['#007bff', '#dc3545'],
            }],
        },
        options: {
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });

    // Gráfico de Faixa Etária dos Membros
    var ctxFaixaEtaria = document.getElementById("faixaEtariaChart").getContext("2d");
    var faixaEtariaChart = new Chart(ctxFaixaEtaria, {
        type: 'pie',
        data: {
            labels: ["Idosos", "Jovens", "Adolescentes", "Crianças", "Bebês"],
            datasets: [{
                data: [
                    faixaEtariaData.idosos_count,
                    faixaEtariaData.jovens_count,
                    faixaEtariaData.adolescentes_count,
                    faixaEtariaData.criancas_count,
                    faixaEtariaData.bebes_count
                ],
                backgroundColor: ['#007bff', '#dc3545', '#ffc107', '#28a745', '#17a2b8'],
            }],
        },
        options: {
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
});