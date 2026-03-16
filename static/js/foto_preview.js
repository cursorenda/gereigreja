// Preview instantâneo da foto de perfil
// Requer: <input type="file" id="id_foto"> e <img id="foto-preview">
document.addEventListener('DOMContentLoaded', function() {
    var input = document.getElementById('id_foto');
    var preview = document.getElementById('foto-preview');
    if (input && preview) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.match('image.*')) {
                const reader = new FileReader();
                reader.onload = function(ev) {
                    preview.src = ev.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }
});
