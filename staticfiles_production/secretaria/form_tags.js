// Controle visual de seleção de tags no formulário de dados cadastrais


// Estado centralizado das tags selecionadas
var selectedTagsArr = [];

function updateSelectFromState() {
    var select = document.getElementById('id_tags');
    if (!select) return;
    for (var i = 0; i < select.options.length; i++) {
        select.options[i].selected = selectedTagsArr.includes(parseInt(select.options[i].value));
    }
}

function updateBadgesFromState() {
    var preview = document.getElementById('selected-tags-preview');
    if (!preview) return;
    preview.innerHTML = '';
    allTags.forEach(function(tag){
        if (selectedTagsArr.includes(tag.id)) {
            var badge = document.createElement('span');
            badge.className = 'badge tag-badge-selected';
            badge.style.backgroundColor = tag.cor;
            badge.style.color = '#fff';
            badge.style.fontSize = '1em';
            badge.style.marginRight = '4px';
            badge.textContent = tag.nome;
            badge.setAttribute('data-tag-id', tag.id);
            badge.onclick = function(){
                // Remover tag do estado
                selectedTagsArr = selectedTagsArr.filter(function(tid){return tid !== tag.id;});
                updateSelectFromState();
                updateBadgesFromState();
            };
            preview.appendChild(badge);
        }
    });
}

function syncStateFromSelect() {
    var select = document.getElementById('id_tags');
    if (!select) return;
    var arr = [];
    for (var i = 0; i < select.options.length; i++) {
        if (select.options[i].selected) arr.push(parseInt(select.options[i].value));
    }
    selectedTagsArr = arr;
}

function setupTagSelection() {
    // Inicializa estado a partir do <select> (caso já haja seleção)
    syncStateFromSelect();
    updateSelectFromState();
    updateBadgesFromState();

    document.querySelectorAll('.tag-badge-select').forEach(function(btn){
        btn.onclick = function(){
            var tagId = parseInt(btn.getAttribute('data-tag-id'));
            if (!selectedTagsArr.includes(tagId)) selectedTagsArr.push(tagId);
            updateSelectFromState();
            updateBadgesFromState();
        };
    });

    // Garante sincronização robusta antes do submit
    var form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function() {
            updateSelectFromState();
        });
    }
}

document.addEventListener('DOMContentLoaded', setupTagSelection);
