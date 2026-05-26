(function () {
  function readJsonScript(id, fallback) {
    var el = document.getElementById(id);
    if (!el) return fallback;
    try {
      var parsed = JSON.parse(el.textContent);
      if (typeof parsed === 'string') {
        try {
          parsed = JSON.parse(parsed);
        } catch (ignore) {
          return fallback;
        }
      }
      return parsed;
    } catch (error) {
      return fallback;
    }
  }

  function chartOrMessage(canvasId, message) {
    var el = document.getElementById(canvasId);
    if (!el) return null;
    return el.getContext('2d');
  }

  function initBirthdaysPanel() {
    var btn = document.getElementById('btnAniversariantes');
    var panel = document.getElementById('cardAniversariantes');
    var closeBtn = document.getElementById('closeAniversariantes');

    if (!btn || !panel || !closeBtn) return;

    function hidePanel() {
      panel.hidden = true;
    }

    function togglePanel() {
      panel.hidden = !panel.hidden;
    }

    btn.addEventListener('click', function (event) {
      event.stopPropagation();
      togglePanel();
    });

    closeBtn.addEventListener('click', function (event) {
      event.stopPropagation();
      hidePanel();
    });

    document.addEventListener('click', function (event) {
      if (!panel.hidden && !panel.contains(event.target) && !btn.contains(event.target)) {
        hidePanel();
      }
    });
  }

  function initCharts() {
    var mesesLabels = readJsonScript('evolucao-meses-labels', []);
    var membros = readJsonScript('evolucao-membros', []);
    var congregados = readJsonScript('evolucao-congregados', []);
    var novosConvertidos = readJsonScript('evolucao-novos-convertidos', []);
    var visitantes = readJsonScript('evolucao-visitantes', []);

    var evolucaoCtx = chartOrMessage('evolucaoMembrosChart');
    if (evolucaoCtx) {
      new Chart(evolucaoCtx, {
        type: 'line',
        data: {
          labels: mesesLabels,
          datasets: [
            { label: 'Membros', data: membros, borderColor: '#0d8281', backgroundColor: 'rgba(13,130,129,0.12)', fill: true, tension: 0.3 },
            { label: 'Congregados', data: congregados, borderColor: '#0f766e', backgroundColor: 'rgba(15,118,110,0.12)', fill: true, tension: 0.3 },
            { label: 'Novos Convertidos', data: novosConvertidos, borderColor: '#0e7490', backgroundColor: 'rgba(14,116,144,0.12)', fill: true, tension: 0.3 },
            { label: 'Visitantes', data: visitantes, borderColor: '#155e75', backgroundColor: 'rgba(21,94,117,0.12)', fill: true, tension: 0.3 }
          ]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
      });
    }

    var pieCtx = chartOrMessage('grafico2');
    if (pieCtx) {
      new Chart(pieCtx, {
        type: 'pie',
        data: {
          labels: readJsonScript('pie-labels-data', []),
          datasets: [{
            data: readJsonScript('pie-values-data', []),
            backgroundColor: ['#0d8281', '#0f766e', '#0e7490', '#155e75', '#0891b2', '#334155', '#1e293b', '#14b8a6']
          }]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
      });
    }

    var statusCtx = chartOrMessage('graficoStatus');
    if (statusCtx) {
      new Chart(statusCtx, {
        type: 'bar',
        data: {
          labels: readJsonScript('status-labels-data', []),
          datasets: [{ label: 'Total', data: readJsonScript('status-values-data', []), backgroundColor: '#0d8281', borderColor: '#0a6665', borderWidth: 2 }]
        },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
      });
    }

    var generoCtx = chartOrMessage('graficoGenero');
    if (generoCtx) {
      new Chart(generoCtx, {
        type: 'bar',
        data: {
          labels: readJsonScript('genero-labels-data', []),
          datasets: [{ label: 'Total', data: readJsonScript('genero-values-data', []), backgroundColor: '#0f766e', borderColor: '#115e59', borderWidth: 2 }]
        },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
      });
    }

    var faixaCtx = chartOrMessage('graficoFaixaEtaria');
    if (faixaCtx) {
      new Chart(faixaCtx, {
        type: 'bar',
        data: {
          labels: readJsonScript('faixa-labels-data', []),
          datasets: [{ label: 'Total', data: readJsonScript('faixa-values-data', []), backgroundColor: '#0e7490', borderColor: '#155e75', borderWidth: 2 }]
        },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
      });
    }

    var categoriaCtx = chartOrMessage('graficoCategoriaEvento');
    if (categoriaCtx) {
      new Chart(categoriaCtx, {
        type: 'bar',
        data: {
          labels: readJsonScript('categoria-evento-labels-data', []),
          datasets: [{ label: 'Participacoes', data: readJsonScript('categoria-evento-values-data', []), backgroundColor: '#0f766e' }]
        },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
      });
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    initBirthdaysPanel();
    initCharts();
  });
})();
