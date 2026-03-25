// === AUTOCOMPLETE DE NOMES (REUTILIZÁVEL) ===
document.addEventListener('DOMContentLoaded', function() {
    const nomeInput = document.getElementById('id_nome');
    const autocompleteList = document.getElementById('autocomplete-nome-list');
    if (!nomeInput || !autocompleteList) return;
    let timeout = null;
    nomeInput.addEventListener('input', function() {
        clearTimeout(timeout);
        const query = this.value;
        if (query.length < 1) {
            autocompleteList.innerHTML = '';
            autocompleteList.style.display = 'none';
            return;
        }
        timeout = setTimeout(function() {
            fetch(`/sistema/autocomplete_nome/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    autocompleteList.innerHTML = '';
                    if (data.results && data.results.length > 0) {
                        data.results.forEach(function(item) {
                            const div = document.createElement('div');
                            div.className = 'list-group-item list-group-item-action';
                            div.textContent = item.nome + (item.tipo_pessoa ? ' (' + item.tipo_pessoa + ')' : '');
                            div.onclick = function() {
                                nomeInput.value = item.nome;
                                autocompleteList.innerHTML = '';
                                autocompleteList.style.display = 'none';
                            };
                            autocompleteList.appendChild(div);
                        });
                        autocompleteList.style.display = 'block';
                    } else {
                        autocompleteList.style.display = 'none';
                    }
                });
        }, 250);
    });
    document.addEventListener('click', function(e) {
        if (!autocompleteList.contains(e.target) && e.target !== nomeInput) {
            autocompleteList.innerHTML = '';
            autocompleteList.style.display = 'none';
        }
    });
});
