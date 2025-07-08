# c:\Gereigreja\secretaria\management\commands\converter_dump.py
import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from secretaria.models import TipoPessoa, StatusPessoa

class Command(BaseCommand):
    help = 'Converte um arquivo de dump JSON antigo para a nova estrutura de TipoPessoa e StatusPessoa, usando os dados existentes no banco de dados.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- Iniciando a conversão inteligente do arquivo de dump ---"))

        # --- MAPEAMENTO (Como os nomes antigos se relacionam com os novos) ---
        MAPA_STATUS_PARA_TIPO_E_STATUS = {
            "MEMBRO ATIVO": ("Membro", "Ativo"),
            "MEMBRO INATIVO": ("Membro", "Inativo"),
            "MEMBRO DISCIPLINA": ("Membro", "Em Disciplina"),
            "VISITANTE": ("Visitante", "Ativo"),
            "CONGREGADO": ("Congregado", "Ativo"),
            "Novo Convertido": ("Novo Convertido", "Ativo"),
            "DESLIGADO": ("Membro", "Desligado"),
            "MUDOU": ("Membro", "Transferido"),
            "Obreiro": ("Obreiro", "Ativo"),
            "Falecido": ("Membro", "Falecido"),
        }

        arquivo_antigo = os.path.join(settings.BASE_DIR, 'datadump.json')
        arquivo_novo = os.path.join(settings.BASE_DIR, 'datadump_final.json')

        if not os.path.exists(arquivo_antigo):
            self.stderr.write(self.style.ERROR(f"ERRO: O arquivo '{arquivo_antigo}' não foi encontrado."))
            return

        # 1. Carregar os dados do banco de dados (que foram criados pelo 'migrate')
        self.stdout.write(self.style.HTTP_INFO("Buscando Tipos e Status do banco de dados atual..."))
        tipos_db = {tp.nome: tp.pk for tp in TipoPessoa.objects.all()}
        status_db = {sp.nome: sp.pk for sp in StatusPessoa.objects.all()}

        # 1.5 GARANTIR QUE OS TIPOS E STATUS EXISTEM NO BANCO DE DADOS
        self.stdout.write(self.style.HTTP_INFO("Verificando e criando Tipos e Status necessários..."))
        tipos_e_status_necessarios = set(MAPA_STATUS_PARA_TIPO_E_STATUS.values())

        for nome_tipo, nome_status in tipos_e_status_necessarios:
            if nome_tipo not in tipos_db:
                tipo_obj, created = TipoPessoa.objects.get_or_create(nome=nome_tipo)
                if created:
                    self.stdout.write(f" -> Criado novo TipoPessoa: '{nome_tipo}'")
                tipos_db[nome_tipo] = tipo_obj.pk
            
            if nome_status not in status_db:
                # Define um padrão para 'considerar_ativo_relatorios'
                ativo_para_relatorios = nome_status in ['Ativo', 'Obreiro', 'Novo Convertido', 'Congregado']
                status_obj, created = StatusPessoa.objects.get_or_create(
                    nome=nome_status, 
                    defaults={'considerar_ativo_relatorios': ativo_para_relatorios}
                )
                if created:
                    self.stdout.write(f" -> Criado novo StatusPessoa: '{nome_status}'")
                status_db[nome_status] = status_obj.pk

        # Carrega o dump antigo
        with open(arquivo_antigo, 'r', encoding='utf-8') as f:
            dados_antigos = json.load(f)
        self.stdout.write(f"Arquivo '{os.path.basename(arquivo_antigo)}' lido com sucesso. {len(dados_antigos)} objetos encontrados.")

        # Estruturas para armazenar os novos dados
        dados_finais = []
        mapa_pk_status_antigo = {}

        # 2. Mapear os PKs dos status antigos do arquivo de dump
        for obj in dados_antigos:
            if obj['model'] == 'secretaria.tiposstatus':
                pk_antigo = obj['pk']
                nome_status_antigo = obj['fields'].get('nome') or obj['fields'].get('status')
                if nome_status_antigo:
                    mapa_pk_status_antigo[pk_antigo] = nome_status_antigo

        # 3. Converter os membros e coletar outros objetos
        for obj in dados_antigos:
            if obj['model'] == 'secretaria.membro':
                pk_status_antigo_do_membro = obj['fields'].pop('status', None)
                if pk_status_antigo_do_membro:
                    nome_status_antigo = mapa_pk_status_antigo.get(pk_status_antigo_do_membro)
                    if nome_status_antigo and nome_status_antigo in MAPA_STATUS_PARA_TIPO_E_STATUS:
                        nome_tipo_novo, nome_status_novo = MAPA_STATUS_PARA_TIPO_E_STATUS[nome_status_antigo]
                        
                        # Obter os novos PKs DO BANCO DE DADOS
                        pk_tipo_novo = tipos_db.get(nome_tipo_novo)
                        pk_status_novo = status_db.get(nome_status_novo)
                        
                        if pk_tipo_novo and pk_status_novo:
                            obj['fields']['tipo_pessoa'] = pk_tipo_novo
                            obj['fields']['status_pessoa'] = pk_status_novo
                        else:
                            self.stdout.write(self.style.WARNING(f"AVISO: Tipo '{nome_tipo_novo}' ou Status '{nome_status_novo}' não encontrado no DB para o membro PK={obj['pk']}. Será deixado sem tipo/status."))
                            obj['fields']['tipo_pessoa'] = None
                            obj['fields']['status_pessoa'] = None
                    else:
                        self.stdout.write(self.style.WARNING(f"AVISO: Status antigo '{nome_status_antigo}' do membro PK={obj['pk']} não encontrado no mapa. Será deixado sem tipo/status."))
                        obj['fields']['tipo_pessoa'] = None
                        obj['fields']['status_pessoa'] = None
                else:
                    # Se o membro não tinha status, definir um padrão
                    obj['fields']['tipo_pessoa'] = tipos_db.get("Membro")
                    obj['fields']['status_pessoa'] = status_db.get("Ativo")
                
                dados_finais.append(obj)

            # --- ADICIONAR ESTE BLOCO ---
            elif obj['model'] == 'configuracao.plano':
                self.stdout.write(f"Convertendo objeto Plano (PK={obj['pk']})...")
                # Pega o valor do campo 'preco' antigo e o remove do dicionário
                preco_antigo = obj['fields'].pop('preco', None)
                # Remove o campo obsoleto 'duracao_dias' se ele existir
                obj['fields'].pop('duracao_dias', None)
                # Remove o campo obsoleto 'codigo_referencia_gateway' se ele existir
                obj['fields'].pop('codigo_referencia_gateway', None)
                if preco_antigo is not None:
                    # Adiciona o valor ao novo campo 'preco_mensal'
                    obj['fields']['preco_mensal'] = preco_antigo
                    # Garante que o campo 'preco_anual' exista com um valor padrão, se não estiver presente
                    if 'preco_anual' not in obj['fields']:
                        obj['fields']['preco_anual'] = "0.00" # Usar string para consistência com JSON
                dados_finais.append(obj)
            # --- FIM DO BLOCO ADICIONADO ---

            elif obj['model'] not in ['secretaria.tiposstatus', 'secretaria.tipopessoa', 'secretaria.statuspessoa']:
                # Adiciona todos os outros objetos que não são os tipos/status que já estão no DB
                dados_finais.append(obj)

        # 4. Salvar o novo arquivo (sem os Tipos e Status, pois já estão no DB)
        with open(arquivo_novo, 'w', encoding='utf-8') as f:
            json.dump(dados_finais, f, indent=2, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f"\n--- Conversão concluída! ---"))
        self.stdout.write(self.style.SUCCESS(f"Arquivo '{os.path.basename(arquivo_novo)}' criado com sucesso com {len(dados_finais)} objetos."))
        self.stdout.write(self.style.SUCCESS("Próximo passo: execute 'python manage.py loaddata datadump_final.json'"))
