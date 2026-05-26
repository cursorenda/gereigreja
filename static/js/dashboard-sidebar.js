/**
 * dashboard-sidebar.js  —  Toggle parametrizável de menu lateral
 * GereIgreja Dashboard Design System
 *
 * Uso em cada dashboard:
 *
 *   DashboardSidebar.init({
 *     storageKey:    'financeiro.sidebar_visible',  // chave única por dashboard
 *     toggleClass:   'dash-financeiro',             // classe CSS para modo full-width
 *     defaultVisible: false                         // padrão quando localStorage vazio
 *   });
 *
 * A chamada de init() deve ocorrer APÓS o carregamento deste script.
 * O script anti-FOUC (inline no <head>) precisa ser mantido separadamente
 * pois deve rodar de forma síncrona antes do render.
 */
var DashboardSidebar = (function () {
  'use strict';

  var _cfg = {
    storageKey:    'dashboard.sidebar_visible',
    toggleClass:   'dash-fullwidth',
    defaultVisible: false,
    labelAttr:     'data-fp-sidebar-label',
    toggleIds:     ['fp-toggle-sidebar']
  };

  var _buttons = [];

  function _applyState(visible) {
    var cls = _cfg.toggleClass;
    document.documentElement.classList.toggle(cls, !visible);
    document.body.classList.toggle(cls, !visible);

    _buttons.forEach(function (btn) {
      btn.setAttribute('aria-expanded', visible ? 'true' : 'false');
      var lbl = btn.querySelector('[' + _cfg.labelAttr + ']');
      if (lbl) {
        lbl.textContent = visible ? 'Ocultar menu' : 'Abrir menu';
      }
    });
  }

  function _toggle() {
    /* Se a classe está presente no html/body → sidebar oculta → toggle = mostrar */
    var currentlyHidden = document.body.classList.contains(_cfg.toggleClass) ||
      document.documentElement.classList.contains(_cfg.toggleClass);
    _applyState(currentlyHidden);
    try {
      localStorage.setItem(_cfg.storageKey, currentlyHidden ? '1' : '0');
    } catch (e) { /* incognito / storage bloqueado */ }
  }

  function _readStorage() {
    try {
      var val = localStorage.getItem(_cfg.storageKey);
      return val === null ? _cfg.defaultVisible : val === '1';
    } catch (e) {
      return _cfg.defaultVisible;
    }
  }

  function init(options) {
    if (options) {
      Object.keys(options).forEach(function (k) {
        _cfg[k] = options[k];
      });
    }

    function bindHandlers() {
      _buttons = (_cfg.toggleIds || [])
        .map(function (id) { return document.getElementById(id); })
        .filter(Boolean);

      _buttons.forEach(function (btn) {
        btn.addEventListener('click', function (e) {
          e.preventDefault();
          e.stopPropagation();
          _toggle();
        }, true);
      });

      _applyState(_readStorage());
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', bindHandlers);
    } else {
      bindHandlers();
    }
  }

  return { init: init };

}());
