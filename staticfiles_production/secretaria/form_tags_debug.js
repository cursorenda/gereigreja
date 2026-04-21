// Debug para seleção de tags
console.log('DEBUG: form_tags_debug.js carregado');

window.addEventListener('DOMContentLoaded', function() {
    var select = document.getElementById('id_tags');
    var preview = document.getElementById('selected-tags-preview');
    var badges = document.querySelectorAll('.tag-badge-select');
    var allTagsScript = document.getElementById('allTagsData');

    console.log('DEBUG: Campo real id_tags:', select);
    console.log('DEBUG: Preview:', preview);
    console.log('DEBUG: Badges:', badges);
    if (allTagsScript) {
        console.log('DEBUG: allTags JSON:', allTagsScript.textContent);
    } else {
        console.log('DEBUG: allTagsData não encontrado');
    }

    badges.forEach(function(btn) {
        btn.addEventListener('click', function() {
            console.log('DEBUG: Badge clicado:', btn.getAttribute('data-tag-id'), btn.textContent);
        });
    });
});