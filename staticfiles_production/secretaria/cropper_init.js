// === CROP DE IMAGEM (Foto do Membro) ===
document.addEventListener('DOMContentLoaded', function() {
    var inputFoto = document.getElementById('id_foto');
    var cropperImg = document.getElementById('cropperImg');
    var modalCrop = document.getElementById('modalCrop');
    var previewImg = document.getElementById('previewImg');
    var cropper = null;
    if (inputFoto && cropperImg && modalCrop && previewImg) {
        inputFoto.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(ev) {
                    cropperImg.src = ev.target.result;
                    cropperImg.style.display = 'block';
                    // Supondo que modalCrop seja um modal Bootstrap 5
                    var modal = new bootstrap.Modal(modalCrop);
                    modal.show();
                };
                reader.readAsDataURL(file);
            }
        });
        modalCrop.addEventListener('shown.bs.modal', function () {
            if (cropper) cropper.destroy();
            cropper = new Cropper(cropperImg, {
                aspectRatio: 1,
                viewMode: 1,
                autoCropArea: 1,
                movable: true,
                zoomable: true,
                rotatable: false,
                scalable: false
            });
        });
        document.getElementById('btn-crop-confirm').addEventListener('click', function() {
            if (cropper) {
                const canvas = cropper.getCroppedCanvas({width: 300, height: 300, imageSmoothingQuality: 'high'});
                previewImg.src = canvas.toDataURL('image/png');
                // Atualiza o input file para enviar o crop (opcional: pode converter para blob e atualizar input)
                // Aqui, para envio real do crop, seria necessário manipular o input file ou enviar via AJAX
                var modal = bootstrap.Modal.getInstance(modalCrop);
                modal.hide();
            }
        });
        modalCrop.addEventListener('hidden.bs.modal', function () {
            if (cropper) cropper.destroy();
        });
    }
});
