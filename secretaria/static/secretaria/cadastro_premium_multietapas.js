(function () {
  function normalizeText(value) {
    if (!value) return '';
    return value
      .toString()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .trim()
      .toLowerCase();
  }

  function selectedText(selectEl) {
    if (!selectEl || selectEl.selectedIndex < 0) return '';
    var option = selectEl.options[selectEl.selectedIndex];
    return option ? option.text : '';
  }

  function isWorkerRank(value) {
    return value && value !== 'membro_comum';
  }

  function setupPhotoPreview() {
    var photoInput = document.getElementById('id_foto');
    var preview = document.getElementById('premium-photo-preview');
    if (!photoInput || !preview) return;

    photoInput.addEventListener('change', function (event) {
      var file = event.target.files && event.target.files[0];
      if (!file) return;

      var reader = new FileReader();
      reader.onload = function (e) {
        if (e && e.target && e.target.result) {
          preview.src = e.target.result;
        }
      };
      reader.readAsDataURL(file);
    });
  }

  function setupCountriesDatalist() {
    var paisInput = document.getElementById('id_pais');
    var datalist = document.getElementById('lista-paises');
    if (!paisInput || !datalist) return;

    var paises = [
      'Brasil', 'Portugal', 'Espanha', 'Franca', 'Italia', 'Alemanha', 'Reino Unido',
      'Estados Unidos', 'Canada', 'Mexico', 'Argentina', 'Chile', 'Colombia',
      'Paraguai', 'Uruguai', 'Peru', 'Bolivia', 'Venezuela', 'Angola', 'Mocambique',
      'Cabo Verde', 'Guine-Bissau', 'Sao Tome e Principe', 'Timor-Leste', 'Japao',
      'China', 'Coreia do Sul', 'India', 'Australia', 'Africa do Sul'
    ];

    datalist.innerHTML = '';
    paises.forEach(function (pais) {
      var option = document.createElement('option');
      option.value = pais;
      datalist.appendChild(option);
    });
    paisInput.setAttribute('autocomplete', 'on');
  }

  function isTipoVisitante(tipo) {
    return tipo.indexOf('visitante') !== -1;
  }

  function isTipoCongregado(tipo) {
    return tipo.indexOf('congregado') !== -1;
  }

  function isTipoNovoConvertido(tipo) {
    return tipo.indexOf('novo convertido') !== -1 || tipo.indexOf('novoconvertido') !== -1 || tipo.indexOf('novo_convertido') !== -1;
  }

  function isTipoMembro(tipo) {
    return tipo === 'membro';
  }

  function isStatusInativo(status) {
    return status.indexOf('inativo') !== -1;
  }

  function fieldValue(id) {
    var el = document.getElementById(id);
    if (!el) return '';
    if (el.tagName === 'SELECT') {
      return selectedText(el) || '';
    }
    return (el.value || '').trim();
  }

  document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('cadastro-premium-form');
    if (!form) return;

    var stepCards = Array.prototype.slice.call(document.querySelectorAll('.premium-step-card'));
    var indicators = Array.prototype.slice.call(document.querySelectorAll('.premium-step-indicator'));

    var tipoSelect = document.getElementById('id_tipo_pessoa');
    var grauSelect = document.getElementById('id_grau_eclesiastico');
    var statusSelect = document.getElementById('id_status_pessoa');
    var estadoCivilSelect = document.getElementById('id_estado_civil');
    var conjugeInput = document.getElementById('id_conjuge');
    var dataCasamentoInput = document.getElementById('id_data_casamento');
    var subStatusSelect = document.getElementById('id_sub_status_inativo');
    var rowGrau = document.getElementById('row-grau-eclesiastico-premium');
    var rowSubStatus = document.getElementById('row-sub-status-inativo-premium');
    var rowConjuge = document.getElementById('row-conjuge-premium');
    var rowDataCasamento = document.getElementById('row-data-casamento-premium');

    var prevBtn = document.getElementById('btn-step-prev');
    var nextBtn = document.getElementById('btn-step-next');
    var submitBtn = document.getElementById('btn-step-submit');

    var rowStep3 = document.getElementById('step-gate-3');
    var rowStep4 = document.getElementById('step-gate-4');
    var rowStep5 = document.getElementById('step-gate-5');
    var progressBar = document.getElementById('premium-progress');
    var progressFill = document.getElementById('premium-progress-fill');
    var progressText = document.getElementById('premium-progress-text');
    var progressCount = document.getElementById('premium-progress-count');
    var progressStatus = document.getElementById('premium-progress-status');
    var stepAlert = document.getElementById('premium-step-alert');
    var a11yStatus = document.getElementById('premium-a11y-status');

    var summaryNome = document.getElementById('summary-nome');
    var summaryTipo = document.getElementById('summary-tipo');
    var summaryStatus = document.getElementById('summary-status');
    var summaryIgreja = document.getElementById('summary-igreja');
    var summaryStep = document.getElementById('summary-step');
    var summaryFluxo = document.getElementById('summary-fluxo');

    var currentStep = 1;

    var statusCatalog = Array.prototype.slice.call(statusSelect ? statusSelect.options : []).map(function (opt) {
      return { value: opt.value, label: opt.text };
    });

    function toggleGrauEclesiastico() {
      if (!grauSelect || !rowGrau) return;
      var isMembro = isTipoMembro(currentTipoName());
      rowGrau.style.display = isMembro ? '' : 'none';
      rowGrau.setAttribute('aria-hidden', isMembro ? 'false' : 'true');
      grauSelect.disabled = !isMembro;
      if (!isMembro) {
        grauSelect.value = '';
      }
    }

    function toggleSubStatusInativo() {
      if (!statusSelect || !subStatusSelect || !rowSubStatus) return;
      var status = normalizeText(selectedText(statusSelect));
      var isInativo = isStatusInativo(status);
      rowSubStatus.style.display = isInativo ? '' : 'none';
      rowSubStatus.setAttribute('aria-hidden', isInativo ? 'false' : 'true');
      subStatusSelect.disabled = !isInativo;
      if (!isInativo) {
        subStatusSelect.value = '';
      }
    }

    function toggleCamposCasamento() {
      if (!estadoCivilSelect || !rowConjuge || !rowDataCasamento || !conjugeInput || !dataCasamentoInput) return;

      var estadoCivil = normalizeText(selectedText(estadoCivilSelect));
      var isCasado = estadoCivil === 'casado';

      rowConjuge.style.display = isCasado ? '' : 'none';
      rowDataCasamento.style.display = isCasado ? '' : 'none';
      rowConjuge.setAttribute('aria-hidden', isCasado ? 'false' : 'true');
      rowDataCasamento.setAttribute('aria-hidden', isCasado ? 'false' : 'true');

      conjugeInput.disabled = !isCasado;
      dataCasamentoInput.disabled = !isCasado;

      if (!isCasado) {
        conjugeInput.value = '';
        dataCasamentoInput.value = '';
        clearFieldError(conjugeInput);
        clearFieldError(dataCasamentoInput);
      }
    }

    function getFieldLabel(el) {
      if (!el) return '';
      var container = el.closest('.col-md-4, .col-md-6, .col-md-3, .col-md-8, .col-12');
      var label = container ? container.querySelector('label') : null;
      return label ? normalizeText(label.textContent).replace(/\s+/g, ' ').trim() : (el.id || '').replace('id_', '');
    }

    function clearFieldError(el) {
      if (!el || !el.id) return;
      var errorId = el.id + '-premium-error';
      var errorEl = document.getElementById(errorId);
      if (errorEl) errorEl.remove();
      el.classList.remove('field-invalid');
      el.removeAttribute('aria-invalid');
      var describedBy = (el.getAttribute('aria-describedby') || '').split(' ').filter(Boolean).filter(function (id) {
        return id !== errorId;
      });
      if (describedBy.length) {
        el.setAttribute('aria-describedby', describedBy.join(' '));
      } else {
        el.removeAttribute('aria-describedby');
      }
    }

    function setFieldError(el, message) {
      if (!el || !el.id) return;
      clearFieldError(el);
      el.classList.add('field-invalid');
      el.setAttribute('aria-invalid', 'true');
      var errorId = el.id + '-premium-error';
      var errorEl = document.createElement('div');
      errorEl.id = errorId;
      errorEl.className = 'invalid-feedback d-block';
      errorEl.textContent = message;
      var container = el.closest('.col-md-4, .col-md-6, .col-md-3, .col-md-8, .col-12') || el.parentElement;
      container.appendChild(errorEl);
      var describedBy = (el.getAttribute('aria-describedby') || '').split(' ').filter(Boolean);
      describedBy.push(errorId);
      el.setAttribute('aria-describedby', Array.from(new Set(describedBy)).join(' '));
    }

    function announce(message) {
      if (!a11yStatus) return;
      a11yStatus.textContent = message;
    }

    function setStepAlert(message) {
      if (!stepAlert) return;
      if (!message) {
        stepAlert.textContent = '';
        stepAlert.classList.remove('show');
        return;
      }
      stepAlert.textContent = message;
      stepAlert.classList.add('show');
    }

    function updateProgress() {
      var maxStep = maxStepByRules();
      var percentage = Math.max(1, Math.round((currentStep / maxStep) * 100));
      var completed = completedStepsCount(maxStep);

      if (progressFill) {
        progressFill.style.width = percentage + '%';
      }
      if (progressText) {
        progressText.textContent = percentage + '% concluido';
      }
      if (progressCount) {
        progressCount.textContent = completed + ' de ' + maxStep + ' etapas concluidas';
      }
      if (progressStatus) {
        progressStatus.textContent = completed >= maxStep
          ? 'Fluxo completo. Pronto para finalizar o cadastro.'
          : 'Etapa ' + currentStep + ' em andamento.';
      }
      if (progressBar) {
        progressBar.setAttribute('aria-valuenow', String(percentage));
        progressBar.setAttribute('aria-valuetext', percentage + '% concluido');
      }
    }

    function isStepComplete(step) {
      var ids = requiredIdsForStep(step);
      if (!ids.length) return true;
      return ids.every(function (id) {
        var el = document.getElementById(id);
        return el && (el.value || '').trim();
      });
    }

    function completedStepsCount(maxStep) {
      var count = 0;
      for (var step = 1; step <= maxStep; step += 1) {
        if (isStepComplete(step)) count += 1;
      }
      return count;
    }

    function updateCompletionVisuals() {
      var maxStep = maxStepByRules();

      indicators.forEach(function (indicator) {
        var step = parseInt(indicator.getAttribute('data-step'), 10);
        indicator.classList.toggle('complete', step <= maxStep && isStepComplete(step));
      });

      stepCards.forEach(function (card) {
        var step = parseInt(card.getAttribute('data-step'), 10);
        card.classList.toggle('step-complete', step <= maxStep && isStepComplete(step));
      });
    }

    function currentTipoName() {
      return normalizeText(selectedText(tipoSelect));
    }

    function maxStepByRules() {
      var tipo = currentTipoName();
      if (isTipoVisitante(tipo)) return 2;
      if (isTipoCongregado(tipo)) return 3;
      if (isTipoNovoConvertido(tipo)) return 3;
      if (isTipoMembro(tipo)) {
        if (isWorkerRank(grauSelect ? grauSelect.value : '')) return 5;
        return 4;
      }
      return 2;
    }

    function updateStatusOptions() {
      if (!statusSelect) return;
      var tipo = currentTipoName();
      var allowDiscipline = isTipoMembro(tipo);

      var allowedLabels = allowDiscipline
        ? ['ativo', 'inativo', 'em disciplina', 'desligado']
        : ['ativo', 'inativo'];

      var previous = statusSelect.value;
      statusSelect.innerHTML = '';

      statusCatalog.forEach(function (item) {
        var normalized = normalizeText(item.label);
        if (allowedLabels.indexOf(normalized) !== -1) {
          var opt = document.createElement('option');
          opt.value = item.value;
          opt.textContent = item.label;
          statusSelect.appendChild(opt);
        }
      });

      var hasPrevious = Array.prototype.some.call(statusSelect.options, function (opt) {
        return opt.value === previous;
      });
      if (hasPrevious) {
        statusSelect.value = previous;
      } else if (statusSelect.options.length > 0) {
        statusSelect.selectedIndex = 0;
      }

      toggleSubStatusInativo();
    }

    function showStep(step) {
      stepCards.forEach(function (card) {
        var cardStep = parseInt(card.getAttribute('data-step'), 10);
        card.style.display = cardStep === step ? 'block' : 'none';
      });

      indicators.forEach(function (indicator) {
        var indStep = parseInt(indicator.getAttribute('data-step'), 10);
        indicator.classList.toggle('active', indStep === step);
        indicator.classList.toggle('done', indStep < step);
        indicator.setAttribute('aria-selected', indStep === step ? 'true' : 'false');
        indicator.setAttribute('aria-current', indStep === step ? 'step' : 'false');
      });

      stepCards.forEach(function (card) {
        var cardStep = parseInt(card.getAttribute('data-step'), 10);
        card.setAttribute('aria-hidden', cardStep === step ? 'false' : 'true');
      });

      prevBtn.style.display = step > 1 ? 'inline-flex' : 'none';
      var maxStep = maxStepByRules();
      var isFinal = step >= maxStep;
      nextBtn.style.display = isFinal ? 'none' : 'inline-flex';
      submitBtn.style.display = isFinal ? 'inline-flex' : 'none';

      var tipo = currentTipoName();
      if (isTipoVisitante(tipo)) {
        submitBtn.textContent = 'Salvar Visitante';
      } else if (isTipoCongregado(tipo) || isTipoNovoConvertido(tipo)) {
        submitBtn.textContent = 'Salvar Cadastro';
      } else if (isTipoMembro(tipo) && maxStep === 4) {
        submitBtn.textContent = 'Salvar Membro';
      } else if (isTipoMembro(tipo) && maxStep === 5) {
        submitBtn.textContent = 'Salvar Obreiro';
      } else {
        submitBtn.textContent = 'Finalizar Cadastro';
      }

      if (summaryStep) summaryStep.textContent = String(step);
      setStepAlert('');
      updateCompletionVisuals();
      updateProgress();
      updateSummary();

      var activeCard = stepCards.find(function (card) {
        return parseInt(card.getAttribute('data-step'), 10) === step;
      });
      var firstField = activeCard ? activeCard.querySelector('input:not([type="hidden"]):not([disabled]), select:not([disabled]), textarea:not([disabled])') : null;
      if (firstField) firstField.focus();
      announce('Etapa ' + step + ' ativa.');
    }

    function clearStepValidation() {
      stepCards.forEach(function (card) {
        var fields = card.querySelectorAll('input, select, textarea');
        fields.forEach(function (f) { clearFieldError(f); });
      });
    }

    function requiredIdsForStep(step) {
      if (step === 1) {
        var required = ['id_nome', 'id_tipo_pessoa', 'id_status_pessoa', 'id_genero'];
        if (isStatusInativo(normalizeText(selectedText(statusSelect)))) {
          required.push('id_sub_status_inativo');
        }
        return required;
      }
      if (step === 2) return ['id_igreja'];
      if (step === 4 && isTipoMembro(currentTipoName())) return ['id_tipo_entrada'];
      if (step === 5 && isTipoMembro(currentTipoName()) && isWorkerRank(grauSelect ? grauSelect.value : '')) return ['id_numero_credencial'];
      return [];
    }

    function validateCurrentStep() {
      clearStepValidation();
      var ids = requiredIdsForStep(currentStep);
      var invalid = [];
      var invalidLabels = [];

      ids.forEach(function (id) {
        var el = document.getElementById(id);
        if (!el) return;
        var value = (el.value || '').trim();
        if (!value) {
          invalid.push(el);
          var label = getFieldLabel(el);
          invalidLabels.push(label);
          setFieldError(el, 'Campo obrigatorio: ' + label + '.');
        } else {
          clearFieldError(el);
        }
      });

      if (invalid.length > 0) {
        setStepAlert('Preencha os campos obrigatorios desta etapa: ' + invalidLabels.join(', ') + '.');
        invalid[0].focus();
        invalid[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
        announce('Existem campos obrigatorios pendentes na etapa ' + currentStep + '.');
        return false;
      }
      setStepAlert('');
      announce('Etapa ' + currentStep + ' validada com sucesso.');
      return true;
    }

    function updateSummary() {
      if (summaryNome) summaryNome.textContent = fieldValue('id_nome') || '-';
      if (summaryTipo) summaryTipo.textContent = fieldValue('id_tipo_pessoa') || '-';
      if (summaryStatus) summaryStatus.textContent = fieldValue('id_status_pessoa') || '-';
      if (summaryIgreja) summaryIgreja.textContent = fieldValue('id_igreja') || '-';

      var tipo = currentTipoName();
      if (!summaryFluxo) return;
      if (isTipoVisitante(tipo)) {
        summaryFluxo.textContent = 'Visitante ate Etapa 2';
      } else if (isTipoCongregado(tipo) || isTipoNovoConvertido(tipo)) {
        summaryFluxo.textContent = 'Congregado/Novo Convertido ate Etapa 3';
      } else if (isTipoMembro(tipo) && isWorkerRank(grauSelect ? grauSelect.value : '')) {
        summaryFluxo.textContent = 'Membro obreiro ate Etapa 5';
      } else if (isTipoMembro(tipo)) {
        summaryFluxo.textContent = 'Membro comum ate Etapa 4';
      } else {
        summaryFluxo.textContent = 'Fluxo minimo ate Etapa 2';
      }
    }

    function applyStepGates() {
      var maxStep = maxStepByRules();
      rowStep3.style.display = maxStep >= 3 ? 'block' : 'none';
      rowStep4.style.display = maxStep >= 4 ? 'block' : 'none';
      rowStep5.style.display = maxStep >= 5 ? 'block' : 'none';

      indicators.forEach(function (indicator) {
        var step = parseInt(indicator.getAttribute('data-step'), 10);
        var enabled = step <= maxStep;
        indicator.setAttribute('aria-disabled', enabled ? 'false' : 'true');
      });

      if (currentStep > maxStep) {
        currentStep = maxStep;
      }
      showStep(currentStep);
    }

    function goNext() {
      if (!validateCurrentStep()) return;
      var maxStep = maxStepByRules();
      if (currentStep < maxStep) {
        currentStep += 1;
        showStep(currentStep);
      }
    }

    function goPrev() {
      if (currentStep > 1) {
        currentStep -= 1;
        showStep(currentStep);
      }
    }

    indicators.forEach(function (indicator) {
      indicator.addEventListener('click', function () {
        var step = parseInt(indicator.getAttribute('data-step'), 10);
        if (step <= maxStepByRules()) {
          if (step > currentStep && !validateCurrentStep()) return;
          currentStep = step;
          showStep(currentStep);
        } else {
          setStepAlert('Esta etapa sera liberada automaticamente conforme Tipo de Pessoa e Grau Eclesiastico.');
        }
      });
    });

    if (nextBtn) nextBtn.addEventListener('click', goNext);
    if (prevBtn) prevBtn.addEventListener('click', goPrev);

    if (tipoSelect) {
      tipoSelect.addEventListener('change', function () {
        toggleGrauEclesiastico();
        updateStatusOptions();
        applyStepGates();
        updateSummary();
      });
    }

    if (grauSelect) {
      grauSelect.addEventListener('change', function () {
        applyStepGates();
        updateSummary();
      });
    }

    if (statusSelect) {
      statusSelect.addEventListener('change', function () {
        toggleSubStatusInativo();
        updateSummary();
      });
    }

    if (estadoCivilSelect) {
      estadoCivilSelect.addEventListener('change', function () {
        toggleCamposCasamento();
        updateSummary();
      });
    }

    ['id_nome', 'id_status_pessoa', 'id_igreja'].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.addEventListener('input', updateSummary);
      if (el) el.addEventListener('change', updateSummary);
    });

    ['id_nome', 'id_tipo_pessoa', 'id_status_pessoa', 'id_sub_status_inativo', 'id_genero', 'id_igreja', 'id_tipo_entrada', 'id_numero_credencial']
      .forEach(function (id) {
        var el = document.getElementById(id);
        if (!el) return;
        el.addEventListener('input', updateCompletionVisuals);
        el.addEventListener('change', updateCompletionVisuals);
      });

    if (subStatusSelect) {
      subStatusSelect.addEventListener('change', updateSummary);
    }

    form.addEventListener('submit', function (event) {
      if (!validateCurrentStep()) {
        event.preventDefault();
        setStepAlert('Revise os campos obrigatorios antes de finalizar o cadastro.');
      } else {
        announce('Formulario validado. Enviando cadastro.');
      }
    });

    updateStatusOptions();
    toggleGrauEclesiastico();
    toggleSubStatusInativo();
    toggleCamposCasamento();
    applyStepGates();
    setupPhotoPreview();
    setupCountriesDatalist();
    updateCompletionVisuals();
    updateSummary();
  });
})();
