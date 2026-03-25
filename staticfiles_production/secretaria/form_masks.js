// === MÁSCARAS E VALIDAÇÕES ===
function aplicarMascara(input, mascara) {
    input.addEventListener('input', function(e) {
        let valor = e.target.value.replace(/\D/g, '');
        let resultado = '';
        let j = 0;
        for (let i = 0; i < mascara.length && j < valor.length; i++) {
            if (mascara[i] === '#') {
                resultado += valor[j];
                j++;
            } else {
                resultado += mascara[i];
            }
        }
        e.target.value = resultado;
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // CPF: ###.###.###-##
    const cpfInput = document.getElementById('id_cpf');
    if (cpfInput) aplicarMascara(cpfInput, '###.###.###-##');
    // CEP: #####-### (apenas máscara)
    const cepInput = document.getElementById('id_cep');
    if (cepInput) {
        aplicarMascara(cepInput, '#####-###');
    }
    // TELEFONE FIXO: (99) 9999-9999
    const telefoneInput = document.getElementById('id_telefone');
    if (telefoneInput) aplicarMascara(telefoneInput, '(##) ####-####');
    // CELULAR: (99) 99999-9999
    const celularInput = document.getElementById('id_celular');
    if (celularInput) aplicarMascara(celularInput, '(##) #####-####');
    // RG: Apenas números e letras
    const rgInput = document.getElementById('id_rg');
    if (rgInput) {
        rgInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.toUpperCase().replace(/[^0-9A-Z]/g, '');
        });
    }
});
