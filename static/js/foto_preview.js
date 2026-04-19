// Preview instantâneo da foto de perfil
// Requer: <input type="file" id="id_foto"> e <img id="foto-preview">
document.addEventListener('DOMContentLoaded', function() {
    // Preview padrão para foto de perfil
    var inputFoto = document.getElementById('id_foto');
    var previewFoto = document.getElementById('foto-preview');
    if (inputFoto && previewFoto) {
        inputFoto.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.match('image.*')) {
                const reader = new FileReader();
                reader.onload = function(ev) {
                    previewFoto.src = ev.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Preview para campo de logo do ministério
    var containerLogo = document.getElementById('logo-preview-container');
    // Busca o input file visível dentro do mesmo bloco do container
    var inputLogo = null;
    if (containerLogo) {
        // Procura pelo input file dentro do mesmo bloco/form
        var parent = containerLogo.parentElement;
        if (parent) {
            inputLogo = parent.querySelector('input[type="file"]');
        }
    }
    if (inputLogo && containerLogo) {
        inputLogo.addEventListener('change', function(e) {
            containerLogo.innerHTML = '';
            const file = e.target.files[0];
            if (file && file.type.match('image.*')) {
                const reader = new FileReader();
                reader.onload = function(ev) {
                    const img = document.createElement('img');
                    img.src = ev.target.result;
                    img.style.maxWidth = '200px';
                    img.style.maxHeight = '120px';
                    img.style.display = 'block';
                    img.style.marginTop = '8px';
                    containerLogo.appendChild(img);
                };
                reader.readAsDataURL(file);
            }
        });
    }
});
