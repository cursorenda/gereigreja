from django.shortcuts import render, redirect
from django.contrib import messages
from .forms_importacao import ImportacaoPessoasForm
from openpyxl import load_workbook
from .models import Pessoa, Igreja, StatusPessoa, TipoPessoa
from django.contrib.auth.decorators import permission_required

@permission_required('secretaria.add_pessoa', raise_exception=True)
def importar_pessoas(request):
    if request.method == 'POST':
        form = ImportacaoPessoasForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = form.cleaned_data['arquivo']
            wb = load_workbook(arquivo)
            ws = wb.active
            linhas_planilha = list(ws.iter_rows(min_row=2, values_only=True))
            wb.close()
            erros = []
            pessoas_criadas = 0
            for idx, row in enumerate(linhas_planilha, start=2):
                # Novo modelo: CPF, Nome, Nome do Pai, Nome da Mãe, Data de Nascimento, Gênero, Igreja, Status, Tipo, Rua, Número, Bairro, Cidade, Estado, Telefone, E-mail
                cpf, nome, nome_pai, nome_mae, nascimento, genero, igreja_nome, status_nome, tipo_nome, rua, numero, bairro, cidade, estado, telefone, email = row[:16]
                linha_erros = []
                import datetime
                # Validação básica
                if not nome:
                    linha_erros.append('Nome obrigatório')
                # Data de nascimento: garantir sempre date
                nascimento_dt = None
                if not nascimento:
                    linha_erros.append('Data de nascimento obrigatória')
                else:
                    try:
                        if isinstance(nascimento, str):
                            nascimento_dt = datetime.datetime.strptime(nascimento.strip(), "%d/%m/%Y").date()
                        elif isinstance(nascimento, datetime.date):
                            nascimento_dt = nascimento
                        else:
                            raise ValueError()
                    except Exception:
                        linha_erros.append('Data de nascimento deve estar no formato dd/mm/aaaa')
                if not genero or genero not in ['M', 'F']:
                    linha_erros.append('Gênero deve ser M ou F')
                if not cpf:
                    linha_erros.append('CPF obrigatório')
                else:
                    from secretaria.forms import validar_cpf
                    try:
                        cpf_validado = validar_cpf(str(cpf))
                    except Exception as e:
                        linha_erros.append(f'CPF inválido: {e}')
                igreja = Igreja.objects.filter(nome_igreja__iexact=igreja_nome).first() if igreja_nome else None
                if not igreja:
                    linha_erros.append('Igreja não encontrada')
                status = StatusPessoa.objects.filter(nome__iexact=status_nome).first() if status_nome else None
                tipo = TipoPessoa.objects.filter(nome__iexact=tipo_nome).first() if tipo_nome else None
                if not tipo:
                    linha_erros.append('Tipo obrigatório ou não encontrado')
                if not status:
                    linha_erros.append('Status obrigatório ou não encontrado')
                if linha_erros:
                    erros.append({'linha': idx, 'erros': linha_erros})
                    continue
                # Criação/atualização protegida por try/except para capturar ValidationError
                try:
                    cpf_bruto = str(cpf).strip()
                    cpf_mascarado = f"{cpf_validado[:3]}.{cpf_validado[3:6]}.{cpf_validado[6:9]}-{cpf_validado[9:]}"
                    pessoa_obj = Pessoa.objects.filter(cpf__in=[cpf_validado, cpf_mascarado, cpf_bruto]).first()

                    if not pessoa_obj:
                        pessoa_obj = Pessoa(cpf=cpf_mascarado)

                    pessoa_obj.nome = nome
                    pessoa_obj.nome_pai = nome_pai
                    pessoa_obj.nome_mae = nome_mae
                    pessoa_obj.nascimento = nascimento_dt
                    pessoa_obj.genero = genero
                    pessoa_obj.igreja = igreja
                    pessoa_obj.status_pessoa = status
                    pessoa_obj.tipo_pessoa = tipo
                    pessoa_obj.rua = rua
                    pessoa_obj.numero_casa = numero
                    pessoa_obj.bairro_distrito = bairro
                    pessoa_obj.cidade = cidade
                    pessoa_obj.estado = estado
                    pessoa_obj.telefone = telefone
                    pessoa_obj.email = email
                    pessoa_obj.save()
                    pessoas_criadas += 1
                except Exception as e:
                    # Captura ValidationError e outros erros de modelo
                    linha_erros.append(f'Erro ao salvar pessoa: {e}')
                    erros.append({'linha': idx, 'erros': linha_erros})
                    continue
            if erros:
                messages.warning(request, f"{pessoas_criadas} pessoas importadas, {len(erros)} linhas com erro.")
                # Log de importação
                try:
                    from datetime import datetime
                    usuario = request.user.username if request.user.is_authenticated else 'anônimo'
                    with open('importacao_pessoas.log', 'a', encoding='utf-8') as log:
                        log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Usuário: {usuario} - {pessoas_criadas} pessoas importadas, {len(erros)} linhas com erro.\n")
                except Exception as e:
                    pass
                return render(request, 'secretaria/importar_pessoas.html', {'form': form, 'erros': erros})
            messages.success(request, f"Importação concluída! {pessoas_criadas} pessoas cadastradas.")
            # Log de importação
            try:
                from datetime import datetime
                usuario = request.user.username if request.user.is_authenticated else 'anônimo'
                with open('importacao_pessoas.log', 'a', encoding='utf-8') as log:
                    log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Usuário: {usuario} - {pessoas_criadas} pessoas importadas, 0 linhas com erro.\n")
            except Exception as e:
                pass
            return redirect('secretaria:lista_membros')
    else:
        form = ImportacaoPessoasForm()
    return render(request, 'secretaria/importar_pessoas.html', {'form': form})
