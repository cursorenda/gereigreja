(function(){
    // Expõe uma função de attach imediata para que chamadores possam acionar a anexação após injeção por AJAX.
    function tryAttachOnce() {
        try {
            var badge = document.getElementById('gcp-js-status');
            var testBtn = document.getElementById('gcp-test-buscar-btn');
            var busca = document.getElementById('busca-membro');
            var dbg = document.getElementById('gcp-buscar-debug');
            var membroHidden = document.getElementById('membro-id');
            // Note: make the test button optional so autocomplete still attaches
            // when the UI has the button removed. Only require the essential elements.
            if (busca && dbg && membroHidden) {
                if (!testBtn.dataset.gcpAttached) {
                    testBtn.dataset.gcpAttached = '1';
                    testBtn.addEventListener('click', function(){
                        var q = (busca.value || '').trim();
                        var eventoVal = '';
                        try {
                            var ev = document.getElementById('evento');
                            if (ev && ev.value) eventoVal = ev.value; else { var eh = document.getElementById('evento-hidden'); if (eh && eh.value) eventoVal = eh.value; }
                        } catch(e) {}
                        var url = (function(){ try { return window.__gcp_buscar_url || '/sistema/ajax/buscar_visitantes/'; } catch(e){ return '/sistema/ajax/buscar_visitantes/'; } })();
                        url = url + '?q=' + encodeURIComponent(q) + (eventoVal ? '&evento=' + encodeURIComponent(eventoVal) : '');
                        if (dbg) { dbg.style.display='block'; dbg.textContent = 'Carregando...'; }
                        fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest','Accept':'application/json'}}).then(function(r){ if (!r.ok) throw new Error('HTTP '+r.status); return r.text(); }).then(function(text){
                            try { var json = text ? JSON.parse(text) : []; if (dbg) dbg.textContent = JSON.stringify(json, null, 2); } catch(e) { if (dbg) dbg.textContent = text || '(empty)'; }
                            try {
                                var parsed = [];
                                try { parsed = text ? JSON.parse(text) : []; } catch(e){ parsed = []; }
                                if (Array.isArray(parsed) && parsed.length === 1) {
                                    var v = parsed[0];
                                    membroHidden.value = v.id || v.chave || '';
                                    busca.value = v.nome + (v.apelido ? ' ('+v.apelido+')' : '');
                                    if (dbg) dbg.textContent += '\n\n(Automático) membro-id preenchido: ' + membroHidden.value;
                                }
                            } catch(e){ console.warn('gcp bootstrap parse failed', e); }
                        }).catch(function(err){ if (dbg) dbg.textContent = 'Erro: '+String(err); console.error('gcp bootstrap error', err); });
                    });
                }
                // Também anexar um handler de entrada leve para o campo de busca para que formulários injetados por AJAX tenham autocomplete funcional
                try {
                    if (busca && !busca.dataset.gcpInputAttached) {
                        busca.dataset.gcpInputAttached = '1';
                        var _gcp_input_timer = null;
                            busca.addEventListener('input', function() {
                            var q = (this.value || '');
                            if (_gcp_input_timer) clearTimeout(_gcp_input_timer);
                            _gcp_input_timer = setTimeout(function() {
                                try {
                                    var lista = document.getElementById('sugestoes-membro');
                                    if (!lista) return;
                                    if (!q || q.length === 0) { lista.style.display = 'none'; lista.innerHTML = ''; return; }
                                    var eventoVal = '';
                                    try { var ev = document.getElementById('evento') || document.getElementById('evento-hidden'); if (ev && ev.value) eventoVal = ev.value; } catch(e) {}
                                    var url = (function(){ try { return window.__gcp_buscar_url || '/sistema/ajax/buscar_visitantes/'; } catch(e){ return '/sistema/ajax/buscar_visitantes/'; } })();
                                    url = url + '?q=' + encodeURIComponent(q) + (eventoVal ? '&evento=' + encodeURIComponent(eventoVal) : '') + '&recepcao=1';
                                    if (dbg) { try { dbg.style.display='block'; dbg.textContent = 'Carregando...'; } catch(e){} }
                                    fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest','Accept':'application/json'}})
                                        .then(function(r){ if (!r.ok) throw new Error('HTTP ' + r.status); return r.json().catch(function(){ return null; }); })
                                        .then(function(json){
                                            var data = [];
                                            try { if (Array.isArray(json)) data = json; else if (json && Array.isArray(json.visitantes)) data = json.visitantes; else if (json && Array.isArray(json.results)) data = json.results; else data = json || []; } catch(e) { data = []; }
                                            lista.innerHTML = '';
                                            lista.style.display = 'block';
                                            if (!Array.isArray(data) || data.length === 0) {
                                                var li = document.createElement('li'); li.className = 'list-group-item text-muted'; li.textContent = 'Nenhuma pessoa encontrada'; lista.appendChild(li); return;
                                            }
                                            data.forEach(function(v){
                                                try {
                                                    var li = document.createElement('li'); li.className = 'list-group-item'; li.textContent = v.nome + (v.apelido ? ' (' + v.apelido + ')' : ''); li.style.cursor = 'pointer';
                                                    li.addEventListener('pointerdown', function(){ try { busca.value = v.nome + (v.apelido ? ' (' + v.apelido + ')' : ''); var mid = document.getElementById('membro-id'); if (mid) mid.value = v.id || v.chave || ''; lista.innerHTML=''; lista.style.display='none'; } catch(e){} });
                                                    lista.appendChild(li);
                                                } catch(e) { console.warn('gcp input populate error', e); }
                                            });
                                        }).catch(function(err){ console.error('gcp input fetch error', err); if (dbg) try { dbg.textContent = 'Erro: ' + String(err); } catch(e){} });
                                } catch(e) { console.warn('gcp input handler error', e); }
                            }, 180);
                        }, false);
                            // evitar duplicar handlers pesados; apenas disparar um evento simples para que o código do template anexe o listener pesado
                            busca.addEventListener('input', function(){
                                var ev = new Event('gcp-busca-input');
                                busca.dispatchEvent(ev);
                            });
                            // Também expor um helper global para reanexar o handler quando necessário (usado pelos templates)
                            if (!window.gcpReattachHelpers) window.gcpReattachHelpers = {};
                            window.gcpReattachHelpers.attachGcpInput = function() {
                                try {
                                    if (!document.querySelector('#busca-membro')) return;
                                    var existing = document.querySelector('#busca-membro').dataset.gcpHeavyAttached;
                                    if (existing) return;
                                    // simular um input para forçar o código do template a anexar seu handler
                                    var el = document.querySelector('#busca-membro');
                                    el.dispatchEvent(new Event('input'));
                                    el.dataset.gcpHeavyAttached = '1';
                                } catch(e) { console.warn('gcpReattachHelpers.attachGcpInput error', e); }
                            };
                    }
                } catch(e) { console.warn('gcp bootstrap attach input handler failed', e); }
                try { badge.className = 'badge bg-success'; badge.textContent = 'JS: OK'; } catch(e){}
                return true;
            }
        } catch(e) { console.warn('gcp bootstrap tryAttachOnce error', e); }
        return false;
    }

    // Expõe globalmente para que outros scripts possam chamar após injetar fragmentos
    try { window.gcpEnsureAttached = tryAttachOnce; } catch(e) { /* ignore */ }

    // Poll como fallback caso chamadores não invoquem gcpEnsureAttached
    var attempts = 0;
    var maxAttempts = 60;
    var intervalMs = 200;
    var poll = setInterval(function(){
        attempts++;
        var ok = tryAttachOnce();
        if (ok) { clearInterval(poll); return; }
        if (attempts >= maxAttempts) {
            clearInterval(poll);
            try {
                var badge2 = document.getElementById('gcp-js-status');
                if (badge2) {
                    // Não forçar exibição do badge em produção; apenas atualizar dataset para diagnóstico.
                    try { badge2.dataset.gcpStatus = 'absent'; } catch(e){}
                    // Se o debug explícito for solicitado via console, mostre a indicação; caso contrário, mantenha oculto.
                    try {
                        if (window.__gcp_show_debug) {
                            badge2.className = 'badge bg-warning';
                            badge2.textContent = 'JS: ausente';
                            badge2.style.display = '';
                        } else {
                            badge2.style.display = 'none';
                        }
                    } catch(e) { badge2.style.display = 'none'; }
                }
            } catch(e){}
        }
    }, intervalMs);

})();
