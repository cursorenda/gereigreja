// recepcao.js - módulo mínimo para abrir o modal de criar visitante e registrar presença
// Export a global init function: initRecepcaoModal()
(function(window){
    function _fetchPartial(q, container) {
        var url = '/sistema/visitantes/criar-parcial/';
        if (q) url += '?q=' + encodeURIComponent(q);
        return fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}}).then(function(r){ return r.text(); });
    }

    function injectHtmlWithScripts(container, html) {
        if (!container) return;
        container.innerHTML = html;
        var scripts = Array.from(container.querySelectorAll('script'));
        scripts.forEach(function(old){
            var s = document.createElement('script');
            if (old.src) {
                s.src = old.src;
                if (old.async) s.async = true;
                if (old.defer) s.defer = true;
            } else {
                try { s.appendChild(document.createTextNode(old.innerHTML)); } catch(e){ s.text = old.innerHTML; }
            }
            old.parentNode.replaceChild(s, old);
        });
    }

    function registerModalOpeners() {
        // Buttons with class registrar-presenca-btn should open the modal
        document.querySelectorAll('.registrar-presenca-btn').forEach(function(btn){
            btn.addEventListener('click', function(e){
                var eventoId = btn.dataset.evento || btn.getAttribute('data-evento');
                var sessaoId = btn.dataset.sessao || btn.getAttribute('data-sessao') || '';
                var modalEl = document.getElementById('modalCriarVisitante');
                if (!modalEl) return;
                // store context
                var ctx = document.getElementById('recepcao-modal-context');
                if (ctx) { ctx.dataset.evento = eventoId || ''; ctx.dataset.sessao = sessaoId || ''; }
                var modal = new bootstrap.Modal(modalEl);
                modal.show();
                // fetch partial into modal body
                var body = document.getElementById('modalCriarVisitanteBody');
                if (!body) return;
                // prefill q with empty
                _fetchPartial('').then(function(html){
                    injectHtmlWithScripts(body, html);
                    // attach simple submit handler
                    try {
                        var form = body.querySelector('#form-criar-visitante-modal');
                        if (form) {
                            form.addEventListener('submit', function(ev){
                                ev.preventDefault();
                                // send form via AJAX
                                var fd = new FormData(form);
                                fetch('/sistema/visitantes/criar-parcial/', {method:'POST', body: fd, headers: {'X-Requested-With':'XMLHttpRequest'}})
                                    .then(function(r){ return r.json(); })
                                    .then(function(data){
                                        if (data.visitante) {
                                            // register presence
                                            var membroId = data.visitante.id || data.visitante.chave || '';
                                            var ctx = document.getElementById('recepcao-modal-context');
                                            var evento = ctx ? ctx.dataset.evento : '';
                                            var sessao = ctx ? ctx.dataset.sessao : '';
                                            var presencaFD = new FormData();
                                            presencaFD.append('evento', evento);
                                            presencaFD.append('membro', membroId);
                                            if (sessao) presencaFD.append('sessao', sessao);
                                            // include csrf if present in form
                                            var csrf = form.querySelector('input[name="csrfmiddlewaretoken"]');
                                            if (csrf) presencaFD.append('csrfmiddlewaretoken', csrf.value);
                                            fetch('/sistema/visitantes/ajax-registrar-presenca-evento/', {method:'POST', body: presencaFD, headers: {'X-Requested-With':'XMLHttpRequest'}})
                                                .then(function(r){ return r.json(); })
                                                .then(function(j){
                                                    if (j.presenca) {
                                                        // if page has visitantes-presentes-list, insert
                                                        var list = document.getElementById('visitantes-presentes-list');
                                                        if (list && j.presenca_html) list.insertAdjacentHTML('afterbegin', j.presenca_html);
                                                        // hide modal
                                                        try { var modalInst = bootstrap.Modal.getInstance(modalEl); if (modalInst) modalInst.hide(); } catch(e){}
                                                        // optional toast
                                                    } else if (j.exists) {
                                                        try { var modalInst = bootstrap.Modal.getInstance(modalEl); if (modalInst) modalInst.hide(); } catch(e){}
                                                    } else if (j.error) {
                                                        console.error('Erro registrando presença:', j.error);
                                                    }
                                                }).catch(function(err){ console.error('Erro registrar presenca fetch', err); });
                                        } else if (data.errors) {
                                            // render errors into modal body if provided
                                            if (data.errors_html && body) body.innerHTML = data.errors_html;
                                        } else if (data.error) {
                                            console.error('Erro criar visitante:', data.error);
                                        }
                                    }).catch(function(err){ console.error('Erro criar visitante json', err); });
                            }, {once:true});
                        }
                    } catch(e){ console.error('attach form handler failed', e); }
                }).catch(function(err){ console.error('Erro carregando partial', err); if (body) body.innerHTML = '<div class="alert alert-danger">Erro ao carregar formulário.</div>'; });
            });
        });
    }

    function initRecepcaoModal() {
        // register openers on DOMContentLoaded or immediately if loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', registerModalOpeners);
        } else {
            registerModalOpeners();
        }
    }

    // expose
    window.initRecepcaoModal = initRecepcaoModal;
})(window);
