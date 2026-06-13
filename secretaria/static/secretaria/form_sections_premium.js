(function () {
  function setExpanded(section, expanded) {
    var header = section.querySelector('.premium-form-section-header');
    var body = section.querySelector('.premium-form-section-body');
    if (!header || !body) return;

    header.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    section.classList.toggle('collapsed', !expanded);

    if (expanded) {
      body.style.maxHeight = body.scrollHeight + 'px';
    } else {
      body.style.maxHeight = '0px';
    }
  }

  function buildSection(section, idx, keyPrefix) {
    section.classList.add('premium-form-section');
    var heading = section.querySelector('h5');
    if (!heading) return;

    var body = document.createElement('div');
    body.className = 'premium-form-section-body';

    var moveNodes = [];
    var foundHeading = false;
    Array.prototype.slice.call(section.childNodes).forEach(function (node) {
      if (!foundHeading) {
        if (node === heading) {
          foundHeading = true;
        }
        return;
      }
      moveNodes.push(node);
    });

    moveNodes.forEach(function (node) {
      body.appendChild(node);
    });
    section.appendChild(body);

    var titleText = (heading.textContent || '').trim();
    heading.innerHTML = '';

    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'premium-form-section-header';
    button.setAttribute('aria-expanded', 'true');
    button.setAttribute('aria-controls', keyPrefix + '-body-' + idx);

    var titleWrap = document.createElement('span');
    titleWrap.className = 'title-wrap';
    titleWrap.textContent = titleText;

    var chevron = document.createElement('span');
    chevron.className = 'chevron';
    chevron.innerHTML = '<i class="fas fa-chevron-down" aria-hidden="true"></i>';

    var status = document.createElement('span');
    status.className = 'status';
    status.textContent = 'Pendente';
    status.setAttribute('aria-hidden', 'true');

    button.appendChild(titleWrap);
    button.appendChild(status);
    button.appendChild(chevron);
    heading.appendChild(button);

    body.id = keyPrefix + '-body-' + idx;

    var hasErrors = section.querySelector('.invalid-feedback.d-block, .alert-danger, .field-invalid');
    var storageKey = keyPrefix + ':section:' + idx;
    var saved = null;
    try {
      saved = localStorage.getItem(storageKey);
    } catch (e) {
      saved = null;
    }

    var expanded = hasErrors ? true : (saved === null ? idx < 2 : saved === '1');
    setExpanded(section, expanded);

    button.addEventListener('click', function () {
      var nowExpanded = button.getAttribute('aria-expanded') !== 'true';
      setExpanded(section, nowExpanded);
      try {
        localStorage.setItem(storageKey, nowExpanded ? '1' : '0');
      } catch (e) {
        // Ignore storage limitations.
      }
    });
  }

  function initPremiumSections() {
    var forms = document.querySelectorAll('form[data-premium-sections="1"]');
    if (!forms.length) return;

    forms.forEach(function (form, formIdx) {
      var progressValue = form.querySelector('#premium-sections-progress-value');
      var keyPrefix = 'gi-premium-form-' + formIdx + '-' + (window.location.pathname || 'page');
      var sections = form.querySelectorAll('div.p-3.mb-4.bg-light.rounded-3[role="region"]');
      if (!sections.length) return;

      function sectionCompleted(section) {
        var controls = section.querySelectorAll('input, select, textarea');
        if (!controls.length) return true;

        var hasFilled = false;
        for (var i = 0; i < controls.length; i += 1) {
          var control = controls[i];
          if (control.disabled || control.type === 'hidden' || control.type === 'file') continue;
          var value = (control.value || '').trim();
          if (value) {
            hasFilled = true;
            break;
          }
        }
        return hasFilled;
      }

      function updateProgress() {
        if (!progressValue) return;
        var total = sections.length;
        var completed = 0;
        sections.forEach(function (section) {
          var isComplete = sectionCompleted(section);
          section.classList.toggle('complete', isComplete);

          var statusEl = section.querySelector('.premium-form-section-header .status');
          if (statusEl) {
            statusEl.textContent = isComplete ? 'Completa ✓' : 'Pendente';
          }

          if (isComplete) completed += 1;
        });
        progressValue.textContent = completed + ' de ' + total + ' seções completas';
      }

      function openAndScrollFirstInvalidSection() {
        var invalidField = form.querySelector('.invalid-feedback.d-block, .field-invalid, [aria-invalid="true"]');
        if (!invalidField) return;

        var targetSection = invalidField.closest('div.p-3.mb-4.bg-light.rounded-3[role="region"]');
        if (!targetSection) return;

        setExpanded(targetSection, true);
        targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }

      sections.forEach(function (section, idx) {
        buildSection(section, idx, keyPrefix);
      });

      form.addEventListener('input', updateProgress);
      form.addEventListener('change', updateProgress);

      window.addEventListener('resize', function () {
        sections.forEach(function (section) {
          var header = section.querySelector('.premium-form-section-header');
          var body = section.querySelector('.premium-form-section-body');
          if (!header || !body) return;
          if (header.getAttribute('aria-expanded') === 'true') {
            body.style.maxHeight = body.scrollHeight + 'px';
          }
        });
      });

      openAndScrollFirstInvalidSection();
      updateProgress();
    });
  }

  document.addEventListener('DOMContentLoaded', initPremiumSections);
})();
