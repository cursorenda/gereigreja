// secretaria/oculta_igreja_superior.js
// Oculta o campo 'Igreja Superior' se o tipo de igreja for 'Sede' ou 'Independente'
document.addEventListener('DOMContentLoaded', function() {
    function toggleIgrejaSuperior() {
        var tipoIgreja = document.getElementById('id_tipo_igreja');
        var igrejaSuperiorDiv = document.getElementById('div_igreja_superior');
        if (!tipoIgreja || !igrejaSuperiorDiv) return;
        var valor = tipoIgreja.value ? tipoIgreja.value.toLowerCase() : '';
        if (valor === 'sede' || valor === 'independente') {
            igrejaSuperiorDiv.style.display = 'none';
            // Opcional: desabilitar o campo para não enviar no POST
            var input = igrejaSuperiorDiv.querySelector('select, input');
            if (input) input.disabled = true;
        } else {
            igrejaSuperiorDiv.style.display = '';
            var input = igrejaSuperiorDiv.querySelector('select, input');
            if (input) input.disabled = false;
        }
    }
    var tipoIgreja = document.getElementById('id_tipo_igreja');
    if (tipoIgreja) {
        tipoIgreja.addEventListener('change', toggleIgrejaSuperior);
        toggleIgrejaSuperior(); // Executa ao carregar
    }
});
