(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var tabButtons = Array.prototype.slice.call(document.querySelectorAll('#membroTab [data-bs-toggle="tab"]'));
    if (!tabButtons.length) return;
    var form = document.querySelector('form[data-premium-sections="1"]');
    var motivoField = document.getElementById('id_motivo_transicao');
    var dataMudancaTipoField = document.getElementById('id_data_mudanca_tipo');
    var dataMudancaStatusField = document.getElementById('id_data_mudanca_status');
    var tipoSelect = document.getElementById('id_tipo_pessoa');
    var statusSelect = document.getElementById('id_status_pessoa');
    var modalRoot = document.getElementById('modalTransitionMeta');
    var modalTipoDate = document.getElementById('modal_data_mudanca_tipo');
    var modalStatusDate = document.getElementById('modal_data_mudanca_status');
    var modalMotivo = document.getElementById('modal_motivo_transicao');
    var btnOpenTransitionModal = document.getElementById('btn-open-transition-modal');
    var btnSaveTransitionMeta = document.getElementById('btn-save-transition-meta');
    var summaryMotivo = document.getElementById('transition-summary-motivo');
    var summaryDataTipo = document.getElementById('transition-summary-data-tipo');
    var summaryDataStatus = document.getElementById('transition-summary-data-status');
    var summaryEmptyHint = document.getElementById('transition-summary-empty-hint');
    var transitionModal = null;
    var transitionMetaSavedThisOpen = false;
    var isRevertingCriticalFields = false;
    var dirty = false;

    function todayIso() {
      var d = new Date();
      var yyyy = d.getFullYear();
      var mm = String(d.getMonth() + 1).padStart(2, '0');
      var dd = String(d.getDate()).padStart(2, '0');
      return yyyy + '-' + mm + '-' + dd;
    }

    function formatIsoDateToBr(isoDate) {
      if (!isoDate || !/^\d{4}-\d{2}-\d{2}$/.test(isoDate)) return '--/--/----';
      var parts = isoDate.split('-');
      return parts[2] + '/' + parts[1] + '/' + parts[0];
    }

    function getSummaryIsoDate(fieldEl, summaryEl) {
      var currentValue = fieldEl ? String(fieldEl.value || '').trim() : '';
      if (currentValue) return currentValue;
      if (!summaryEl) return '';
      return String(summaryEl.getAttribute('data-initial-iso') || '').trim();
    }

    function updateTransitionSummary() {
      if (summaryMotivo && motivoField) {
        var motivoTxt = String(motivoField.value || '').trim();
        summaryMotivo.textContent = motivoTxt || 'Nenhum motivo informado ainda.';
      }
      var hasTipoDate = false;
      var hasStatusDate = false;
      if (summaryDataTipo && dataMudancaTipoField) {
        var isoTipo = getSummaryIsoDate(dataMudancaTipoField, summaryDataTipo);
        hasTipoDate = !!isoTipo;
        summaryDataTipo.textContent = formatIsoDateToBr(isoTipo);
      }
      if (summaryDataStatus && dataMudancaStatusField) {
        var isoStatus = getSummaryIsoDate(dataMudancaStatusField, summaryDataStatus);
        hasStatusDate = !!isoStatus;
        summaryDataStatus.textContent = formatIsoDateToBr(isoStatus);
      }
      if (summaryEmptyHint) {
        summaryEmptyHint.style.display = (hasTipoDate || hasStatusDate) ? 'none' : 'block';
      }
    }

    function syncModalFromHidden() {
      if (modalTipoDate && dataMudancaTipoField) modalTipoDate.value = dataMudancaTipoField.value || todayIso();
      if (modalStatusDate && dataMudancaStatusField) modalStatusDate.value = dataMudancaStatusField.value || todayIso();
      if (modalMotivo && motivoField) modalMotivo.value = motivoField.value || '';
    }

    function syncHiddenFromModal() {
      if (dataMudancaTipoField && modalTipoDate) dataMudancaTipoField.value = modalTipoDate.value || todayIso();
      if (dataMudancaStatusField && modalStatusDate) dataMudancaStatusField.value = modalStatusDate.value || todayIso();
      if (motivoField && modalMotivo) motivoField.value = modalMotivo.value || '';
      updateTransitionSummary();
    }

    function openTransitionModal() {
      if (!modalRoot || typeof bootstrap === 'undefined' || !bootstrap.Modal) return;
      if (!transitionModal) transitionModal = bootstrap.Modal.getOrCreateInstance(modalRoot);
      transitionMetaSavedThisOpen = false;
      syncModalFromHidden();
      transitionModal.show();
      setTimeout(function () {
        if (modalMotivo) modalMotivo.focus();
      }, 150);
    }

    function currentValue(id) {
      var el = document.getElementById(id);
      if (!el) return '';
      if (el.tagName === 'SELECT') return String(el.value || '');
      return String((el.value || '').trim());
    }

    var criticalInitial = {
      tipo: currentValue('id_tipo_pessoa'),
      status: currentValue('id_status_pessoa'),
      igreja: currentValue('id_igreja'),
      grau: currentValue('id_grau_eclesiastico')
    };

    updateTransitionSummary();

    if (btnOpenTransitionModal) {
      btnOpenTransitionModal.addEventListener('click', function () {
        openTransitionModal();
      });
    }

    if (btnSaveTransitionMeta) {
      btnSaveTransitionMeta.addEventListener('click', function () {
        var motivo = modalMotivo ? String(modalMotivo.value || '').trim() : '';
        if (!motivo) {
          alert('Informe o motivo da alteracao para continuar.');
          if (modalMotivo) modalMotivo.focus();
          return;
        }
        syncHiddenFromModal();
        transitionMetaSavedThisOpen = true;
        if (transitionModal) transitionModal.hide();
      });
    }

    function maybeOpenTransitionModalOnCriticalSelectChange() {
      if (isRevertingCriticalFields) return;
      var tipoChanged = currentValue('id_tipo_pessoa') !== criticalInitial.tipo;
      var statusChanged = currentValue('id_status_pessoa') !== criticalInitial.status;
      if (tipoChanged || statusChanged) {
        openTransitionModal();
      }
    }

    if (modalRoot) {
      modalRoot.addEventListener('hidden.bs.modal', function () {
        if (transitionMetaSavedThisOpen) return;

        var tipoChanged = currentValue('id_tipo_pessoa') !== criticalInitial.tipo;
        var statusChanged = currentValue('id_status_pessoa') !== criticalInitial.status;
        if (!tipoChanged && !statusChanged) return;

        isRevertingCriticalFields = true;
        if (tipoSelect) {
          tipoSelect.value = criticalInitial.tipo;
          tipoSelect.dispatchEvent(new Event('change', { bubbles: true }));
        }
        if (statusSelect) {
          statusSelect.value = criticalInitial.status;
          statusSelect.dispatchEvent(new Event('change', { bubbles: true }));
        }
        isRevertingCriticalFields = false;

        updateTransitionSummary();
      });
    }

    if (tipoSelect) tipoSelect.addEventListener('change', maybeOpenTransitionModalOnCriticalSelectChange);
    if (statusSelect) statusSelect.addEventListener('change', maybeOpenTransitionModalOnCriticalSelectChange);

    function setUrlTab(tabId) {
      try {
        var url = new URL(window.location.href);
        url.searchParams.set('tab', tabId);
        window.history.replaceState({}, '', url.toString());
      } catch (e) {
        // Keep navigation resilient even in legacy browsers.
      }
    }

    function activateTabById(tabId) {
      if (!tabId) return;
      var targetBtn = document.querySelector('#membroTab [data-bs-target="#' + tabId + '"]');
      if (!targetBtn || typeof bootstrap === 'undefined' || !bootstrap.Tab) return;
      bootstrap.Tab.getOrCreateInstance(targetBtn).show();
    }

    var initialTab = null;
    try {
      var params = new URLSearchParams(window.location.search);
      initialTab = params.get('tab');
    } catch (e) {
      initialTab = null;
    }
    activateTabById(initialTab);

    tabButtons.forEach(function (btn) {
        btn.addEventListener('show.bs.tab', function (event) {
          if (!dirty) return;
          if (event.target === event.relatedTarget) return;
          var proceed = confirm('Existem alteracoes nao salvas. Deseja realmente trocar de aba?');
          if (!proceed) {
            event.preventDefault();
          }
        });
      btn.addEventListener('shown.bs.tab', function (event) {
        var targetSelector = event.target.getAttribute('data-bs-target') || '';
        var tabId = targetSelector.replace('#', '');
        if (tabId) setUrlTab(tabId);
      });

      btn.addEventListener('keydown', function (event) {
        var currentIndex = tabButtons.indexOf(btn);
        if (currentIndex < 0) return;

        var targetIndex = null;
        if (event.key === 'ArrowRight') targetIndex = (currentIndex + 1) % tabButtons.length;
        if (event.key === 'ArrowLeft') targetIndex = (currentIndex - 1 + tabButtons.length) % tabButtons.length;
        if (event.key === 'Home') targetIndex = 0;
        if (event.key === 'End') targetIndex = tabButtons.length - 1;

        if (targetIndex === null) return;
        event.preventDefault();

        var nextBtn = tabButtons[targetIndex];
        if (!nextBtn) return;
        nextBtn.focus();
        if (typeof bootstrap !== 'undefined' && bootstrap.Tab) {
          bootstrap.Tab.getOrCreateInstance(nextBtn).show();
        }
      });
    });

    if (!form) return;

    form.addEventListener('input', function () {
      dirty = true;
    });

    form.addEventListener('change', function () {
      dirty = true;
    });

    window.addEventListener('beforeunload', function (event) {
      if (!dirty) return;
      event.preventDefault();
      event.returnValue = '';
    });

    form.addEventListener('submit', function (event) {
      var criticalCurrent = {
        tipo: currentValue('id_tipo_pessoa'),
        status: currentValue('id_status_pessoa'),
        igreja: currentValue('id_igreja'),
        grau: currentValue('id_grau_eclesiastico')
      };

      var changedItems = [];
      if (criticalCurrent.tipo !== criticalInitial.tipo) changedItems.push('Tipo');
      if (criticalCurrent.status !== criticalInitial.status) changedItems.push('Status');
      if (criticalCurrent.igreja !== criticalInitial.igreja) changedItems.push('Igreja');
      if (criticalCurrent.grau !== criticalInitial.grau) changedItems.push('Grau Eclesiastico');

      if (changedItems.length) {
        var motivo = motivoField ? String((motivoField.value || '').trim()) : '';
        if (!motivo) {
          event.preventDefault();
          if (modalMotivo) modalMotivo.value = motivo;
          openTransitionModal();
          return;
        }

        var confirmation = confirm('Voce esta alterando campos criticos: ' + changedItems.join(', ') + '.\nDeseja continuar?');
        if (!confirmation) {
          event.preventDefault();
          return;
        }
      }

      dirty = false;
    });
  });
})();
