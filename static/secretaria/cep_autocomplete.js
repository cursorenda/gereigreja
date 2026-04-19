// === AUTOCOMPLETE DE ENDEREÇO PELO CEP ===
document.addEventListener('DOMContentLoaded', function() {
    const cepInput = document.getElementById('id_cep');
    if (cepInput) {
        cepInput.addEventListener('blur', function() {
            let cep = this.value.replace(/\D/g, '');
            if (cep.length === 8) {
                const originalPlaceholder = this.placeholder;
                this.placeholder = 'Buscando endereço...';
                this.disabled = true;
                fetch(`https://viacep.com.br/ws/${cep}/json/`)
                    .then(response => response.json())
                    .then(data => {
                        if (!data.erro) {
                            if (data.logradouro) {
                                if (document.getElementById('id_rua')) document.getElementById('id_rua').value = data.logradouro;
                            }
                            if (data.bairro) {
                                if (document.getElementById('id_bairro_distrito')) document.getElementById('id_bairro_distrito').value = data.bairro;
                                if (document.getElementById('id_bairro')) document.getElementById('id_bairro').value = data.bairro;
                            }
                            if (data.localidade && document.getElementById('id_cidade')) document.getElementById('id_cidade').value = data.localidade;
                            if (data.uf && document.getElementById('id_estado')) document.getElementById('id_estado').value = data.uf;
                            // Foca no campo de número, seja numero_casa ou numero
                            let numeroInput = document.getElementById('id_numero_casa');
                            if (!numeroInput) numeroInput = document.getElementById('id_numero');
                            if (numeroInput) numeroInput.focus();
                            cepInput.style.borderColor = '#28a745';
                            setTimeout(() => { cepInput.style.borderColor = ''; }, 2000);
                        } else {
                            alert('CEP não encontrado. Verifique o número digitado.');
                            cepInput.style.borderColor = '#dc3545';
                            setTimeout(() => { cepInput.style.borderColor = ''; }, 2000);
                        }
                    })
                    .catch(error => {
                        alert('Erro ao buscar CEP. Verifique sua conexão.');
                    })
                    .finally(() => {
                        this.placeholder = originalPlaceholder;
                        this.disabled = false;
                    });
            }
        });
    }
});
