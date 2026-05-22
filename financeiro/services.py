import re
from hashlib import sha256
from datetime import datetime, timedelta
from calendar import monthrange
from decimal import Decimal
from xml.etree import ElementTree as ET

from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone

from .models import (
    ContaPagar,
    Despesas,
    FechamentoCaixa,
    ImportacaoExtratoOFX,
    LancamentoExtratoOFX,
    Receitas,
    RecorrenciaContaPagar,
)
from configuracao.models import PerfilUsuario
from contas.constants import TESOUREIRO
from contas.constants import user_has_permission_level_or_higher
from notificacoes.models import Notificacao


class FechamentoCaixaService:
    def __init__(self, data_inicio, data_fim, igreja=None, observacoes=''):
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.igreja = igreja
        self.observacoes = observacoes

    def buscar_dados(self):
        receitas = Receitas.objects.filter(
            data__gte=self.data_inicio,
            data__lte=self.data_fim,
            fechado=False,
        )
        despesas = Despesas.objects.filter(
            data__gte=self.data_inicio,
            data__lte=self.data_fim,
            fechado=False,
        )
        return receitas, despesas

    def calcular_totais(self, receitas_queryset, despesas_queryset):
        total_entradas = receitas_queryset.aggregate(Sum('valor')).get('valor__sum') or Decimal('0')
        total_saidas = despesas_queryset.aggregate(Sum('valor')).get('valor__sum') or Decimal('0')
        saldo_final = total_entradas - total_saidas
        return total_entradas, total_saidas, saldo_final

    def fechar_caixa(self, total_entradas, total_saidas, saldo_final):
        return FechamentoCaixa.objects.create(
            igreja=self.igreja,
            data_inicio=self.data_inicio,
            data_fim=self.data_fim,
            total_entradas=total_entradas,
            total_saidas=total_saidas,
            saldo_final=saldo_final,
            observacoes=self.observacoes,
            status='fechado',
        )


class OFXImportService:
    def parse(self, content):
        xml_content = self._normalizar_ofx_para_xml(content)
        root = ET.fromstring(xml_content)

        statement = root.find('.//BANKTRANLIST')
        if statement is None:
            raise ValueError('Arquivo OFX sem bloco BANKTRANLIST.')

        ledger_balance = root.find('.//LEDGERBAL/BALAMT')
        account_id = root.findtext('.//BANKACCTFROM/ACCTID')
        bank_id = root.findtext('.//BANKACCTFROM/BANKID')
        account_type = root.findtext('.//BANKACCTFROM/ACCTTYPE')
        start_date = self._parse_ofx_datetime(statement.findtext('DTSTART'))
        end_date = self._parse_ofx_datetime(statement.findtext('DTEND'))

        transactions = []
        for transaction in statement.findall('STMTTRN'):
            amount = Decimal(transaction.findtext('TRNAMT', '0').strip())
            posted_at = self._parse_ofx_datetime(transaction.findtext('DTPOSTED'))
            transaction_type = (transaction.findtext('TRNTYPE') or '').strip().upper()
            fit_id = (transaction.findtext('FITID') or '').strip()
            memo = (transaction.findtext('MEMO') or '').strip()
            checknum = (transaction.findtext('CHECKNUM') or '').strip()

            transactions.append({
                'tipo': 'entrada' if amount >= 0 else 'saida',
                'trn_type': transaction_type,
                'data': posted_at,
                'valor': amount,
                'fit_id': fit_id,
                'memo': memo,
                'documento': checknum,
            })

        return {
            'banco_id': (bank_id or '').strip(),
            'conta_id': (account_id or '').strip(),
            'tipo_conta': (account_type or '').strip(),
            'data_inicio': start_date,
            'data_fim': end_date,
            'saldo_final': Decimal(ledger_balance.text.strip()) if ledger_balance is not None and ledger_balance.text else Decimal('0.00'),
            'transacoes': transactions,
        }

    def importar_para_banco(self, content, conta_bancaria, usuario=None, arquivo_nome=''):
        parsed = self.parse(content)
        file_hash = sha256(content.encode('utf-8')).hexdigest()

        if ImportacaoExtratoOFX.objects.filter(conta_bancaria=conta_bancaria, hash_arquivo=file_hash).exists():
            raise ValueError('Este arquivo OFX ja foi importado para esta conta.')

        with transaction.atomic():
            importacao = ImportacaoExtratoOFX.objects.create(
                conta_bancaria=conta_bancaria,
                igreja=conta_bancaria.igreja,
                usuario=usuario,
                arquivo_nome=arquivo_nome,
                hash_arquivo=file_hash,
                banco_id=parsed['banco_id'],
                conta_id=parsed['conta_id'],
                tipo_conta=parsed['tipo_conta'],
                data_inicio=parsed['data_inicio'],
                data_fim=parsed['data_fim'],
                saldo_final=parsed['saldo_final'],
            )

            LancamentoExtratoOFX.objects.bulk_create([
                LancamentoExtratoOFX(
                    importacao=importacao,
                    data=transacao['data'],
                    tipo=transacao['tipo'],
                    trn_type=transacao['trn_type'],
                    valor=transacao['valor'],
                    fit_id=transacao['fit_id'],
                    memo=transacao['memo'],
                    documento=transacao['documento'],
                )
                for transacao in parsed['transacoes']
            ])

        return importacao

    def gerar_sugestoes_conciliacao(self, importacao, tolerancia_dias=3, limite_por_lancamento=3):
        lancamentos = importacao.lancamentos.filter(conciliado=False).order_by('data', 'id')
        sugestoes = []

        for lancamento in lancamentos:
            valor_base = abs(lancamento.valor)
            data_base = lancamento.data.date()
            data_inicio = data_base - timedelta(days=tolerancia_dias)
            data_fim = data_base + timedelta(days=tolerancia_dias)

            if lancamento.tipo == 'entrada':
                candidatos = Receitas.objects.filter(
                    igreja=importacao.igreja,
                    data__gte=data_inicio,
                    data__lte=data_fim,
                    valor=valor_base,
                ).order_by('data', 'id')
                tipo_objeto = 'receita'
            else:
                candidatos = Despesas.objects.filter(
                    igreja=importacao.igreja,
                    data__gte=data_inicio,
                    data__lte=data_fim,
                    valor=valor_base,
                ).order_by('data', 'id')
                tipo_objeto = 'despesa'

            candidatos_rankeados = []
            for candidato in candidatos:
                score = self._calcular_score_candidato(lancamento, candidato, importacao.conta_bancaria_id)
                candidatos_rankeados.append((score, candidato))

            candidatos_rankeados.sort(key=lambda item: item[0], reverse=True)
            melhores = [
                {
                    'id': candidato.id,
                    'tipo': tipo_objeto,
                    'data': candidato.data,
                    'valor': candidato.valor,
                    'score': score,
                }
                for score, candidato in candidatos_rankeados[:limite_por_lancamento]
            ]

            sugestoes.append(
                {
                    'lancamento_id': lancamento.id,
                    'fit_id': lancamento.fit_id,
                    'tipo': lancamento.tipo,
                    'valor': lancamento.valor,
                    'data': lancamento.data,
                    'memo': lancamento.memo,
                    'sugestoes': melhores,
                }
            )

        return sugestoes

    def confirmar_conciliacao(self, lancamento_id, tipo, referencia_id, usuario=None):
        tipo = (tipo or '').strip().lower()
        if tipo not in {'receita', 'despesa'}:
            raise ValueError('Tipo de conciliacao invalido. Use receita ou despesa.')

        with transaction.atomic():
            lancamento = (
                LancamentoExtratoOFX.objects
                .select_for_update()
                .select_related('importacao', 'importacao__igreja')
                .get(pk=lancamento_id)
            )

            if lancamento.conciliado:
                raise ValueError('Lancamento OFX ja conciliado.')

            if tipo == 'receita':
                referencia = Receitas.objects.filter(
                    pk=referencia_id,
                    igreja=lancamento.importacao.igreja,
                ).first()
            else:
                referencia = Despesas.objects.filter(
                    pk=referencia_id,
                    igreja=lancamento.importacao.igreja,
                ).first()

            if referencia is None:
                raise ValueError('Lancamento interno nao encontrado para conciliacao.')

            if abs(Decimal(referencia.valor)) != abs(Decimal(lancamento.valor)):
                raise ValueError('Valor do lancamento interno difere do valor OFX.')

            lancamento.conciliado = True
            lancamento.conciliado_tipo = tipo
            lancamento.conciliado_referencia_id = referencia.id
            lancamento.conciliado_por = usuario
            lancamento.conciliado_em = timezone.now()
            lancamento.save(update_fields=[
                'conciliado',
                'conciliado_tipo',
                'conciliado_referencia_id',
                'conciliado_por',
                'conciliado_em',
            ])

        return lancamento

    def desfazer_conciliacao(self, lancamento_id):
        with transaction.atomic():
            lancamento = (
                LancamentoExtratoOFX.objects
                .select_for_update()
                .get(pk=lancamento_id)
            )

            if not lancamento.conciliado:
                raise ValueError('Lancamento OFX ainda nao esta conciliado.')

            lancamento.conciliado = False
            lancamento.conciliado_tipo = ''
            lancamento.conciliado_referencia_id = None
            lancamento.conciliado_por = None
            lancamento.conciliado_em = None
            lancamento.save(update_fields=[
                'conciliado',
                'conciliado_tipo',
                'conciliado_referencia_id',
                'conciliado_por',
                'conciliado_em',
            ])

        return lancamento

    def conciliar_melhores_sugestoes(self, importacao, usuario=None, score_minimo=90, dry_run=False):
        sugestoes = self.gerar_sugestoes_conciliacao(importacao)
        total_conciliados = 0
        total_ignorados_score = 0
        total_erros = 0
        referencias_usadas = set()
        itens_selecionados = []
        quantidade_entradas = 0
        quantidade_saidas = 0
        total_entradas = Decimal('0')
        total_saidas = Decimal('0')

        def registrar_impacto(item_sugestao):
            nonlocal quantidade_entradas, quantidade_saidas, total_entradas, total_saidas
            tipo_ofx = item_sugestao.get('tipo')
            valor_ofx = abs(Decimal(item_sugestao.get('valor') or 0))
            if tipo_ofx == 'entrada':
                quantidade_entradas += 1
                total_entradas += valor_ofx
            else:
                quantidade_saidas += 1
                total_saidas += valor_ofx

        for item in sugestoes:
            candidatos = item.get('sugestoes') or []
            if not candidatos:
                continue

            melhor = candidatos[0]
            if melhor.get('score', 0) < score_minimo:
                total_ignorados_score += 1
                continue

            chave_referencia = (melhor.get('tipo'), melhor.get('id'))
            if chave_referencia in referencias_usadas:
                total_ignorados_score += 1
                continue

            itens_selecionados.append(
                {
                    'lancamento_id': item.get('lancamento_id'),
                    'fit_id': item.get('fit_id'),
                    'tipo_ofx': item.get('tipo'),
                    'data_ofx': item.get('data'),
                    'valor_ofx': item.get('valor'),
                    'memo': item.get('memo'),
                    'tipo_referencia': melhor.get('tipo'),
                    'referencia_id': melhor.get('id'),
                    'data_referencia': melhor.get('data'),
                    'valor_referencia': melhor.get('valor'),
                    'score': melhor.get('score', 0),
                }
            )

            if dry_run:
                referencias_usadas.add(chave_referencia)
                total_conciliados += 1
                registrar_impacto(item)
                continue

            try:
                self.confirmar_conciliacao(
                    lancamento_id=item.get('lancamento_id'),
                    tipo=melhor.get('tipo'),
                    referencia_id=melhor.get('id'),
                    usuario=usuario,
                )
                referencias_usadas.add(chave_referencia)
                total_conciliados += 1
                registrar_impacto(item)
            except Exception:
                total_erros += 1

        return {
            'total_conciliados': total_conciliados,
            'total_ignorados_score': total_ignorados_score,
            'total_erros': total_erros,
            'itens_selecionados': itens_selecionados,
            'resumo_impacto': {
                'quantidade_entradas': quantidade_entradas,
                'quantidade_saidas': quantidade_saidas,
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'total_movimentado': total_entradas + total_saidas,
                'saldo_previsto': total_entradas - total_saidas,
            },
        }

    def _calcular_score_candidato(self, lancamento, candidato, conta_bancaria_id):
        dias_diferenca = abs((lancamento.data.date() - candidato.data).days)
        score = 100 - (dias_diferenca * 10)

        candidato_conta_id = getattr(candidato, 'conta_bancaria_id', None)
        if candidato_conta_id and candidato_conta_id == conta_bancaria_id:
            score += 20

        memo = (lancamento.memo or '').lower()
        texto_candidato = ''
        if hasattr(candidato, 'descricao'):
            texto_candidato = (candidato.descricao or '').lower()
        else:
            texto_candidato = (getattr(candidato, 'observacao', '') or '').lower()

        if memo and texto_candidato and any(token in texto_candidato for token in memo.split() if len(token) >= 4):
            score += 5

        return score

    def _normalizar_ofx_para_xml(self, content):
        if not content or '<OFX>' not in content.upper():
            raise ValueError('Conteudo OFX invalido.')

        start_index = content.upper().find('<OFX>')
        body = content[start_index:]
        normalized_lines = []

        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            match = re.match(r'^<([A-Z0-9_]+)>([^<]+)$', line, flags=re.IGNORECASE)
            if match:
                tag_name = match.group(1)
                value = self._escape_xml(match.group(2).strip())
                normalized_lines.append(f'<{tag_name}>{value}</{tag_name}>')
            else:
                normalized_lines.append(line)

        return '\n'.join(normalized_lines)

    def _parse_ofx_datetime(self, value):
        if not value:
            return None

        digits = re.match(r'^(\d{8})(\d{6})?', value.strip())
        if not digits:
            raise ValueError(f'Data OFX invalida: {value}')

        date_part = digits.group(1)
        time_part = digits.group(2) or '000000'
        return datetime.strptime(f'{date_part}{time_part}', '%Y%m%d%H%M%S')

    def _escape_xml(self, value):
        return (
            value.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
        )


class RecorrenciaContaPagarService:
    """Gera contas a pagar a partir de recorrências de forma idempotente."""

    @staticmethod
    def _parse_competencia(competencia=None):
        if competencia:
            try:
                ano_str, mes_str = competencia.split('-')
                ano = int(ano_str)
                mes = int(mes_str)
            except (ValueError, TypeError):
                raise ValueError("Competencia invalida. Use o formato AAAA-MM.")
        else:
            hoje = timezone.localdate()
            ano = hoje.year
            mes = hoje.month

        if mes < 1 or mes > 12:
            raise ValueError("Mes da competencia invalido. Use um valor entre 01 e 12.")

        return ano, mes, f"{ano:04d}-{mes:02d}"

    @staticmethod
    def _calcular_data_vencimento(ano, mes, dia_vencimento):
        ultimo_dia_mes = monthrange(ano, mes)[1]
        dia_ajustado = min(dia_vencimento, ultimo_dia_mes)
        return datetime(ano, mes, dia_ajustado).date()

    def gerar_competencia(self, competencia=None, ministerio_id=None, igreja_id=None, dry_run=False):
        ano, mes, competencia_str = self._parse_competencia(competencia)
        recorrencias = RecorrenciaContaPagar.objects.filter(
            ativo=True,
            gerar_automaticamente=True,
        ).select_related('ministerio', 'igreja', 'fornecedor', 'categoria', 'conta_debito_padrao')

        if ministerio_id:
            recorrencias = recorrencias.filter(ministerio_id=ministerio_id)
        if igreja_id:
            recorrencias = recorrencias.filter(igreja_id=igreja_id)

        recorrencias = recorrencias.order_by('id')

        total_avaliadas = 0
        total_geradas = 0
        total_existentes = 0
        total_ignoradas = 0
        erros = []

        for recorrencia in recorrencias:
            total_avaliadas += 1
            try:
                if recorrencia.data_inicio and competencia_str < recorrencia.data_inicio.strftime('%Y-%m'):
                    total_ignoradas += 1
                    continue

                if recorrencia.data_fim and competencia_str > recorrencia.data_fim.strftime('%Y-%m'):
                    total_ignoradas += 1
                    continue

                data_vencimento = self._calcular_data_vencimento(ano, mes, recorrencia.dia_vencimento)
                data_emissao = datetime(ano, mes, 1).date()

                ja_existe = ContaPagar.objects.filter(
                    recorrencia_origem=recorrencia,
                    competencia=competencia_str,
                ).exists()

                if ja_existe:
                    total_existentes += 1
                    continue

                if dry_run:
                    total_geradas += 1
                    continue

                with transaction.atomic():
                    try:
                        ContaPagar.objects.create(
                            ministerio=recorrencia.ministerio,
                            igreja=recorrencia.igreja,
                            fornecedor=recorrencia.fornecedor,
                            categoria=recorrencia.categoria,
                            descricao=recorrencia.descricao,
                            valor=recorrencia.valor,
                            data_emissao=data_emissao,
                            data_vencimento=data_vencimento,
                            status='PEN',
                            conta_debito=recorrencia.conta_debito_padrao,
                            forma_pagamento=recorrencia.forma_pagamento_padrao,
                            recorrencia_origem=recorrencia,
                            competencia=competencia_str,
                            criado_automaticamente=True,
                            observacoes=recorrencia.observacoes,
                            usuario_criacao=recorrencia.usuario_criacao,
                        )
                        recorrencia.ultima_competencia_gerada = competencia_str
                        recorrencia.save(update_fields=['ultima_competencia_gerada', 'data_atualizacao'])
                        total_geradas += 1
                    except IntegrityError:
                        total_existentes += 1
            except Exception as exc:
                erros.append(f"Recorrencia {recorrencia.id}: {exc}")

        return {
            'competencia': competencia_str,
            'total_avaliadas': total_avaliadas,
            'total_geradas': total_geradas,
            'total_existentes': total_existentes,
            'total_ignoradas': total_ignoradas,
            'total_erros': len(erros),
            'erros': erros,
            'dry_run': dry_run,
        }


class AlertaVencimentoContaPagarService:
    """Gera notificações de alerta para contas a pagar próximas do vencimento ou vencidas."""

    @staticmethod
    def _tipo_alerta(dias_restantes):
        if dias_restantes < 0:
            return 'VENCIDA'
        if dias_restantes == 7:
            return 'D-7'
        if dias_restantes == 3:
            return 'D-3'
        if dias_restantes == 1:
            return 'D-1'
        return None

    @staticmethod
    def _usuarios_destino(conta):
        from financeiro.utils import get_allowed_churches_for_user

        perfis = PerfilUsuario.objects.filter(
            ministerio=conta.ministerio,
            user__is_active=True,
        ).select_related('user').distinct()

        usuarios = []
        for perfil in perfis:
            user = perfil.user
            if not user_has_permission_level_or_higher(user, TESOUREIRO):
                continue

            igrejas_permitidas = get_allowed_churches_for_user(user)
            if igrejas_permitidas.filter(pk=conta.igreja_id).exists():
                usuarios.append(user)

        return usuarios

    def enviar_alertas(self, dias_alerta=(7, 3, 1), incluir_vencidas=True, ministerio_id=None, igreja_id=None, dry_run=False):
        hoje = timezone.localdate()
        dias_alerta = tuple(sorted({int(d) for d in dias_alerta if int(d) >= 0}, reverse=True))
        limite_dias = max(dias_alerta) if dias_alerta else 0

        contas = ContaPagar.objects.filter(status__in=['PEN', 'VEN']).select_related(
            'ministerio', 'igreja', 'fornecedor'
        )

        if ministerio_id:
            contas = contas.filter(ministerio_id=ministerio_id)
        if igreja_id:
            contas = contas.filter(igreja_id=igreja_id)

        if incluir_vencidas:
            contas = contas.filter(data_vencimento__lte=hoje + timedelta(days=limite_dias))
        else:
            contas = contas.filter(data_vencimento__gte=hoje, data_vencimento__lte=hoje + timedelta(days=limite_dias))

        total_contas_avaliadas = 0
        total_notificacoes_criadas = 0
        total_notificacoes_existentes = 0
        total_contas_sem_destinatario = 0
        total_contas_fora_regra = 0
        erros = []

        for conta in contas.order_by('data_vencimento', 'id'):
            total_contas_avaliadas += 1
            try:
                dias_restantes = (conta.data_vencimento - hoje).days
                tipo_alerta = self._tipo_alerta(dias_restantes)

                if not tipo_alerta:
                    total_contas_fora_regra += 1
                    continue
                if tipo_alerta == 'VENCIDA' and not incluir_vencidas:
                    total_contas_fora_regra += 1
                    continue
                if tipo_alerta != 'VENCIDA' and dias_restantes not in dias_alerta:
                    total_contas_fora_regra += 1
                    continue

                usuarios_destino = self._usuarios_destino(conta)
                if not usuarios_destino:
                    total_contas_sem_destinatario += 1
                    continue

                marcador = f"[ALERTA-CP:{conta.id}:{tipo_alerta}]"
                for user in usuarios_destino:
                    ja_existe = Notificacao.objects.filter(
                        user=user,
                        ministerio=conta.ministerio,
                        notification_type='financeiro',
                        message__contains=marcador,
                    ).exists()

                    if ja_existe:
                        total_notificacoes_existentes += 1
                        continue

                    if dry_run:
                        total_notificacoes_criadas += 1
                        continue

                    Notificacao.objects.create(
                        user=user,
                        ministerio=conta.ministerio,
                        notification_type='financeiro',
                        message=(
                            f"{marcador} Conta a pagar '{conta.descricao}' ({conta.fornecedor.nome}) "
                            f"vence em {conta.data_vencimento.strftime('%d/%m/%Y')} "
                            f"(status: {conta.get_status_display()})."
                        ),
                        url=reverse('financeiro:lista_contas_pagar'),
                    )
                    total_notificacoes_criadas += 1
            except Exception as exc:
                erros.append(f"Conta {conta.id}: {exc}")

        return {
            'total_contas_avaliadas': total_contas_avaliadas,
            'total_notificacoes_criadas': total_notificacoes_criadas,
            'total_notificacoes_existentes': total_notificacoes_existentes,
            'total_contas_sem_destinatario': total_contas_sem_destinatario,
            'total_contas_fora_regra': total_contas_fora_regra,
            'total_erros': len(erros),
            'erros': erros,
            'dry_run': dry_run,
            'dias_alerta': dias_alerta,
            'incluir_vencidas': incluir_vencidas,
        }
