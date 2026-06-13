// === MÁSCARA PARA CAMPOS DE DATA ===
function aplicarMascaraData(input) {
    input.addEventListener('input', function(e) {
        let valor = e.target.value.replace(/\D/g, '');
        let resultado = '';
        if (valor.length > 0) resultado += valor.substring(0, 2);
        if (valor.length > 2) resultado += '/' + valor.substring(2, 4);
        if (valor.length > 4) resultado += '/' + valor.substring(4, 8);
        e.target.value = resultado;
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const camposData = [
        'id_nascimento',
        'id_data_casamento',
        'id_data_entrada',
        'id_data_primeira_visita',
        'id_data_mudanca_tipo',
        'id_data_mudanca_status',
        'id_data_batismo',
        'id_data_consagracao'
    ];
    camposData.forEach(function(id) {
        const input = document.getElementById(id);
        if (input) aplicarMascaraData(input);
    });
});
