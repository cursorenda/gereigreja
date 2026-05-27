(function () {
  var rootStyles = window.getComputedStyle ? getComputedStyle(document.documentElement) : null;

  function readCssVar(name, fallback) {
    if (!rootStyles) return fallback;
    var value = rootStyles.getPropertyValue(name);
    return value ? value.trim() : fallback;
  }

  var dsChart = {
    primary: readCssVar('--dp-primary', '#0D8281'),
    primaryDark: readCssVar('--dp-primary-dk', '#0A6665'),
    primaryLight: readCssVar('--dp-primary-lt', '#2AA5A4'),
    success: readCssVar('--dp-success', '#10B981'),
    warning: readCssVar('--dp-warning', '#D97706'),
    danger: readCssVar('--dp-danger', '#EF4444'),
    text: readCssVar('--dp-text', '#1E293B'),
    muted: readCssVar('--dp-muted', '#64748B'),
    border: readCssVar('--dp-border', '#E2E8F0'),
    surface: readCssVar('--dp-surface', '#FFFFFF'),
    palette: [
      readCssVar('--dp-primary', '#0D8281'),
      readCssVar('--dp-success', '#10B981'),
      readCssVar('--dp-warning', '#D97706'),
      readCssVar('--dp-danger', '#EF4444'),
      readCssVar('--dp-primary-lt', '#2AA5A4'),
      readCssVar('--dp-primary-dk', '#0A6665'),
      readCssVar('--dp-text', '#1E293B'),
      readCssVar('--dp-muted', '#64748B'),
      readCssVar('--dp-primary', '#0D8281'),
      readCssVar('--dp-success', '#10B981'),
      readCssVar('--dp-warning', '#D97706'),
      readCssVar('--dp-primary-lt', '#2AA5A4')
    ]
  };

  if (window.Chart) {
    Chart.defaults.responsive = true;
    Chart.defaults.maintainAspectRatio = false;
    Chart.defaults.devicePixelRatio = function () {
      return Math.min(window.devicePixelRatio || 1, 2);
    };
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Arial, sans-serif";
    Chart.defaults.color = dsChart.muted;
  }

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

  function chartOrMessage(canvasId) {
    var el = document.getElementById(canvasId);
    if (!el) return null;
    return el.getContext('2d');
  }

  function hasAnyData(values) {
    if (!Array.isArray(values) || values.length === 0) {
      return false;
    }
    return values.some(function (value) {
      return Number(value) > 0;
    });
  }

  function showChartEmptyState(canvasId, message) {
    var el = document.getElementById(canvasId);
    if (!el || !el.parentNode) return;
    el.parentNode.innerHTML = '<div class="secdash-chart-empty">' + message + '</div>';
  }

  function commonLegendOptions() {
    return {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        boxWidth: 10,
        boxHeight: 10,
        padding: 14,
        font: {
          size: 11,
          weight: '600'
        }
      }
    };
  }

  function commonCartesianOptions(stepSize) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      resizeDelay: 120,
      layout: {
        padding: {
          top: 4,
          right: 8,
          bottom: 2,
          left: 2
        }
      },
      plugins: {
        tooltip: {
          backgroundColor: 'rgba(15,23,42,0.92)',
          titleColor: dsChart.surface,
          bodyColor: dsChart.border,
          cornerRadius: 8,
          padding: 10,
          displayColors: true
        }
      },
      scales: {
        x: {
          ticks: {
            color: dsChart.muted,
            font: {
              size: 11
            },
            maxRotation: 35,
            minRotation: 0
          },
          grid: {
            color: 'rgba(148,163,184,0.18)',
            drawBorder: false
          }
        },
        y: {
          beginAtZero: true,
          ticks: {
            color: dsChart.muted,
            font: {
              size: 11
            },
            stepSize: stepSize || undefined
          },
          grid: {
            color: 'rgba(148,163,184,0.22)',
            drawBorder: false
          }
        }
      }
    };
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
    if (!hasAnyData(membros) && !hasAnyData(congregados) && !hasAnyData(novosConvertidos) && !hasAnyData(visitantes)) {
      showChartEmptyState('evolucaoMembrosChart', 'Sem dados de evolucao no periodo selecionado.');
      evolucaoCtx = null;
    }
    if (evolucaoCtx) {
      new Chart(evolucaoCtx, {
        type: 'line',
        data: {
          labels: mesesLabels,
          datasets: [
            { label: 'Membros', data: membros, borderColor: dsChart.primary, backgroundColor: 'rgba(13,130,129,0.10)', fill: true, tension: 0.3 },
            { label: 'Congregados', data: congregados, borderColor: dsChart.success, backgroundColor: 'rgba(16,185,129,0.10)', fill: true, tension: 0.3 },
            { label: 'Novos Convertidos', data: novosConvertidos, borderColor: dsChart.primaryLight, backgroundColor: 'rgba(42,165,164,0.10)', fill: true, tension: 0.3 },
            { label: 'Visitantes', data: visitantes, borderColor: dsChart.warning, backgroundColor: 'rgba(217,119,6,0.10)', fill: true, tension: 0.3 }
          ]
        },
        options: Object.assign(commonCartesianOptions(), {
          plugins: {
            legend: commonLegendOptions(),
            tooltip: commonCartesianOptions().plugins.tooltip
          }
        })
      });
    }

    var pieValues = readJsonScript('pie-values-data', []);
    var pieCtx = chartOrMessage('grafico2');
    if (!hasAnyData(pieValues)) {
      showChartEmptyState('grafico2', 'Sem distribuicao de tipos para exibir.');
      pieCtx = null;
    }
    if (pieCtx) {
      new Chart(pieCtx, {
        type: 'doughnut',
        data: {
          labels: readJsonScript('pie-labels-data', []),
          datasets: [{
            data: pieValues,
            backgroundColor: dsChart.palette,
            borderColor: dsChart.surface,
            borderWidth: 2,
            hoverOffset: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '40%',
          layout: {
            padding: {
              top: 8,
              right: 8,
              bottom: 0,
              left: 8
            }
          },
          plugins: {
            legend: commonLegendOptions(),
            tooltip: {
              backgroundColor: 'rgba(15,23,42,0.92)',
              titleColor: dsChart.surface,
              bodyColor: dsChart.border,
              cornerRadius: 8,
              padding: 10
            }
          }
        }
      });
    }

    var statusValues = readJsonScript('status-values-data', []);
    var statusCtx = chartOrMessage('graficoStatus');
    if (!hasAnyData(statusValues)) {
      showChartEmptyState('graficoStatus', 'Sem pessoas por status para exibir.');
      statusCtx = null;
    }
    if (statusCtx) {
      new Chart(statusCtx, {
        type: 'bar',
        data: {
          labels: readJsonScript('status-labels-data', []),
          datasets: [{ label: 'Total', data: statusValues, backgroundColor: dsChart.primary, borderColor: dsChart.primaryDark, borderWidth: 2 }]
        },
        options: Object.assign(commonCartesianOptions(), {
          plugins: {
            legend: { display: false },
            tooltip: commonCartesianOptions().plugins.tooltip
          }
        })
      });
    }

    var generoValues = readJsonScript('genero-values-data', []);
    var generoCtx = chartOrMessage('graficoGenero');
    if (!hasAnyData(generoValues)) {
      showChartEmptyState('graficoGenero', 'Sem dados de genero para exibir.');
      generoCtx = null;
    }
    if (generoCtx) {
      new Chart(generoCtx, {
        type: 'bar',
        data: {
          labels: readJsonScript('genero-labels-data', []),
          datasets: [{ label: 'Total', data: generoValues, backgroundColor: dsChart.success, borderColor: dsChart.success, borderWidth: 2 }]
        },
        options: Object.assign(commonCartesianOptions(), {
          plugins: {
            legend: { display: false },
            tooltip: commonCartesianOptions().plugins.tooltip
          }
        })
      });
    }

    var faixaValues = readJsonScript('faixa-values-data', []);
    var faixaCtx = chartOrMessage('graficoFaixaEtaria');
    if (!hasAnyData(faixaValues)) {
      showChartEmptyState('graficoFaixaEtaria', 'Sem dados de faixa etaria para exibir.');
      faixaCtx = null;
    }
    if (faixaCtx) {
      new Chart(faixaCtx, {
        type: 'bar',
        data: {
          labels: readJsonScript('faixa-labels-data', []),
          datasets: [{ label: 'Total', data: faixaValues, backgroundColor: dsChart.primaryLight, borderColor: dsChart.primaryDark, borderWidth: 2 }]
        },
        options: Object.assign(commonCartesianOptions(), {
          plugins: {
            legend: { display: false },
            tooltip: commonCartesianOptions().plugins.tooltip
          }
        })
      });
    }

    var categoriaValues = readJsonScript('categoria-evento-values-data', []);
    var categoriaCtx = chartOrMessage('graficoCategoriaEvento');
    if (!hasAnyData(categoriaValues)) {
      showChartEmptyState('graficoCategoriaEvento', 'Sem participacao por categoria para exibir.');
      categoriaCtx = null;
    }
    if (categoriaCtx) {
      new Chart(categoriaCtx, {
        type: 'bar',
        data: {
          labels: readJsonScript('categoria-evento-labels-data', []),
          datasets: [{ label: 'Participacoes', data: categoriaValues, backgroundColor: dsChart.primaryLight, borderColor: dsChart.primary, borderWidth: 1.5 }]
        },
        options: Object.assign(commonCartesianOptions(1), {
          plugins: {
            legend: { display: false },
            tooltip: commonCartesianOptions(1).plugins.tooltip
          }
        })
      });
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    initBirthdaysPanel();
    initCharts();
  });
})();
