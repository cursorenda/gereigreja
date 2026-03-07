"""
Comando para configurar permissões de todos os grupos do sistema.
Baseado em: skills/configuracao/ESTRUTURA_GRUPOS_COMPLETA.md

Uso:
    python manage.py configurar_permissoes_grupos [--reset]

Última atualização: 12/02/2026
Hierarquia: Pastor Presidente → Pastor Regional → Pastor Local → Equipe Administrativa
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from contas.constants import *


class Command(BaseCommand):
    help = 'Configura permissões de todos os 14 grupos do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove todas as permissões antes de configurar',
        )

    def handle(self, *args, **options):
        reset = options.get('reset', False)
        
        self.stdout.write("=" * 60)
        self.stdout.write("CONFIGURAÇÃO DE PERMISSÕES DOS GRUPOS")
        self.stdout.write("=" * 60)
        
        if reset:
            self.stdout.write(self.style.WARNING("\n🔄 Modo RESET: Limpando permissões existentes...\n"))
        
        # 1️⃣ Nível Administrativo
        self.configurar_admin_ministerio(reset)
        
        # 2️⃣-3️⃣ Liderança Ministerial
        self.configurar_lideranca_secretaria(reset)
        self.configurar_lideranca_financeira(reset)
        
        # 4️⃣ Liderança Regional
        self.configurar_pastor_regional(reset)
        
        # 5️⃣ Liderança Local
        self.configurar_pastor_local(reset)
        
        # 6️⃣-8️⃣ Operacional Local
        self.configurar_secretario_local(reset)
        self.configurar_tesoureiro_local(reset)
        self.configurar_superintendente_ebd(reset)
        
        # 8️⃣-🔟 Equipes
        self.configurar_equipe_eventos(reset)
        self.configurar_equipe_midia(reset)
        self.configurar_equipe_recepcao(reset)
        
        # 1️⃣1️⃣-1️⃣2️⃣ Auxiliares EBD
        self.configurar_professor_ebd(reset)
        self.configurar_secretaria_ebd(reset)
        
        # 1️⃣3️⃣ Base
        self.configurar_membro_comum(reset)
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS('✅ PERMISSÕES CONFIGURADAS COM SUCESSO!'))
        self.stdout.write("=" * 60 + "\n")

    def get_permissions(self, codenames):
        """
        Busca permissões pelos codenames no formato 'app.codename'.
        Exemplo: ['secretaria.view_pessoa', 'financeiro.add_transacao']
        """
        permissions = []
        for codename_full in codenames:
            try:
                app_label, codename = codename_full.split('.')
                perm = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=codename
                )
                permissions.append(perm)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠️  Permissão não encontrada: {codename_full}")
                )
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Formato inválido: {codename_full}")
                )
        return permissions

    def configurar_grupo(self, nome_grupo, permissoes_codenames, reset=False):
        """Helper para configurar grupo com lista de permissões."""
        grupo, created = Group.objects.get_or_create(name=nome_grupo)
        
        if reset:
            grupo.permissions.clear()
        
        permissoes = self.get_permissions(permissoes_codenames)
        grupo.permissions.add(*permissoes)
        
        status = "criado" if created else "atualizado"
        self.stdout.write(
            f"  ✅ {nome_grupo}: {len(permissoes)} permissões ({status})"
        )

    # ========================================
    # CONFIGURAÇÕES POR GRUPO
    # ========================================

    def configurar_admin_ministerio(self, reset):
        """Admin tem TODAS as permissões (exceto django.admin interno)."""
        self.stdout.write("\n1️⃣  ADMIN MINISTERIO")
        
        grupo, created = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        
        if reset:
            grupo.permissions.clear()
        
        # Todas exceto admin interno, contenttypes, sessions
        todas = Permission.objects.exclude(
            content_type__app_label__in=['admin', 'contenttypes', 'sessions', 'auth']
        )
        grupo.permissions.set(todas)
        
        status = "criado" if created else "atualizado"
        self.stdout.write(
            f"  ✅ {ADMIN_MINISTERIO}: {grupo.permissions.count()} permissões ({status})"
        )

    def configurar_lideranca_secretaria(self, reset):
        """
        Escopo: Ministerial (todas as igrejas)
        - Gerencia cadastros de membros
        - Apenas VÊ cargos (não gerencia - são locais)
        - Aprova transferências, gera relatórios
        """
        self.stdout.write("\n2️⃣  LIDERANCA SECRETARIA")
        
        permissoes = [
            # Secretaria (completo)
            'secretaria.view_pessoa',
            'secretaria.add_pessoa',
            'secretaria.change_pessoa',
            'secretaria.delete_pessoa',
            'secretaria.view_cargo',  # Apenas visualização
            'secretaria.view_familia',
            'secretaria.add_familia',
            'secretaria.change_familia',
            'secretaria.delete_familia',
            'secretaria.view_tag',
            'secretaria.add_tag',
            'secretaria.change_tag',
            'secretaria.delete_tag',
            # Eventos (visualização)
            'eventos.view_evento',
            'eventos.view_inscricao',
            # Comunicação
            'comunicacao.view_notificacao',
            'comunicacao.add_notificacao',
            'comunicacao.add_mensagem',
            'comunicacao.view_mensagem',
            # EBD (visualização)
            'escola_biblica.view_turma',
            'escola_biblica.view_aluno',
            # Agenda
            'agenda.view_compromisso',
        ]
        
        self.configurar_grupo(LIDERANCA_SECRETARIA, permissoes, reset)

    def configurar_lideranca_financeira(self, reset):
        """
        Escopo: Ministerial (todas as igrejas)
        - APENAS VISUALIZA transações (não lança)
        - Cria categorias globais
        - Audita e consolida
        """
        self.stdout.write("\n3️⃣  LIDERANCA FINANCEIRA")
        
        permissoes = [
            # Financeiro (VIEW + categorias)
            'financeiro.view_transacao',  # Apenas visualização
            'financeiro.view_conta',
            'financeiro.view_categoria',
            'financeiro.add_categoria',
            'financeiro.change_categoria',
            'financeiro.delete_categoria',
            # Secretaria (ver dízimos por membro)
            'secretaria.view_pessoa',
            # Eventos (custos)
            'eventos.view_evento',
            # Comunicação
            'comunicacao.view_notificacao',
            'comunicacao.add_notificacao',
        ]
        
        self.configurar_grupo(LIDERANCA_FINANCEIRA, permissoes, reset)

    def configurar_pastor_regional(self, reset):
        """
        Escopo: Regional (várias igrejas subordinadas)
        - Supervisiona pastores locais
        - VÊ finanças (não lança)
        - VÊ cargos (não gerencia - são locais)
        """
        self.stdout.write("\n4️⃣  PASTOR REGIONAL")
        
        permissoes = [
            # Secretaria
            'secretaria.view_pessoa',
            'secretaria.add_pessoa',
            'secretaria.change_pessoa',
            'secretaria.view_cargo',  # Apenas visualização
            'secretaria.view_familia',
            'secretaria.view_tag',
            # Financeiro (somente visualização)
            'financeiro.view_transacao',
            'financeiro.view_categoria',
            'financeiro.view_conta',
            # Eventos
            'eventos.view_evento',
            'eventos.add_evento',
            'eventos.change_evento',
            'eventos.view_inscricao',
            # Comunicação
            'comunicacao.view_mensagem',
            'comunicacao.add_mensagem',
            'comunicacao.view_notificacao',
            'comunicacao.add_notificacao',
            # EBD
            'escola_biblica.view_turma',
            'escola_biblica.view_aluno',
            'escola_biblica.view_aula',
            # Agenda
            'agenda.view_compromisso',
            'agenda.add_compromisso',
            'agenda.change_compromisso',
        ]
        
        self.configurar_grupo(PASTOR_REGIONAL, permissoes, reset)

    def configurar_pastor_local(self, reset):
        """
        Escopo: Local (UMA igreja específica)
        - Pastor da igreja local (líder espiritual)
        - Gerencia membros e pode aprovar cargos
        - VÊ finanças (não lança - tem tesoureiro)
        - Gerencia eventos da igreja
        """
        self.stdout.write("\n5️⃣  PASTOR LOCAL")
        
        permissoes = [
            # Secretaria (gestão completa da igreja)
            'secretaria.view_pessoa',
            'secretaria.add_pessoa',
            'secretaria.change_pessoa',
            'secretaria.delete_pessoa',
            'secretaria.view_cargo',
            'secretaria.add_cargo',  # Pode aprovar cargos
            'secretaria.change_cargo',
            'secretaria.view_familia',
            'secretaria.add_familia',
            'secretaria.change_familia',
            'secretaria.view_visita',
            'secretaria.add_visita',
            'secretaria.change_visita',
            'secretaria.view_tag',
            # Financeiro (somente visualização)
            'financeiro.view_receita',
            'financeiro.view_despesa',
            'financeiro.view_categoria',
            'financeiro.view_conta',
            # Eventos (pode gerenciar eventos da igreja)
            'eventos.view_evento',
            'eventos.add_evento',
            'eventos.change_evento',
            'eventos.delete_evento',
            'eventos.view_inscricao',
            'eventos.change_inscricao',
            # Comunicação
            'comunicacao.view_aviso',
            'comunicacao.add_aviso',
            'comunicacao.change_aviso',
            'comunicacao.view_notificacao',
            'comunicacao.add_notificacao',
            # EBD (visualização e apoio)
            'escola_biblica.view_turma',
            'escola_biblica.view_aluno',
            'escola_biblica.view_aula',
            'escola_biblica.view_frequencia',
            # Agenda
            'agenda.view_compromisso',
            'agenda.add_compromisso',
            'agenda.change_compromisso',
            'agenda.delete_compromisso',
        ]
        
        self.configurar_grupo(PASTOR_LOCAL, permissoes, reset)

    def configurar_secretario_local(self, reset):
        """
        Escopo: Local (uma igreja)
        - Gestão administrativa de membros e famílias
        - GERENCIA CARGOS LOCAIS (add/change/delete)
        - Apoio ao Pastor Local
        """
        self.stdout.write("\n6️⃣  SECRETARIO LOCAL")
        
        permissoes = [
            # Secretaria (completo incluindo cargos)
            'secretaria.view_pessoa',
            'secretaria.add_pessoa',
            'secretaria.change_pessoa',
            'secretaria.delete_pessoa',
            'secretaria.view_cargo',
            'secretaria.add_cargo',
            'secretaria.change_cargo',
            'secretaria.delete_cargo',
            'secretaria.view_familia',
            'secretaria.add_familia',
            'secretaria.change_familia',
            'secretaria.delete_familia',
            'secretaria.view_tag',
            'secretaria.add_tag',
            # Eventos (visualização)
            'eventos.view_evento',
            'eventos.view_inscricao',
            # Comunicação
            'comunicacao.view_notificacao',
            'comunicacao.add_mensagem',
            # EBD (visualização)
            'escola_biblica.view_turma',
            'escola_biblica.view_aluno',
            # Agenda
            'agenda.view_compromisso',
            'agenda.add_compromisso',
            'agenda.change_compromisso',
        ]
        
        self.configurar_grupo(SECRETARIO_LOCAL, permissoes, reset)

    def configurar_tesoureiro_local(self, reset):
        """
        Escopo: Local (uma igreja)
        - Lança receitas e despesas
        - Gerencia contas bancárias
        - USA categorias (não cria)
        """
        self.stdout.write("\n6️⃣  TESOUREIRO")
        
        permissoes = [
            # Financeiro (completo exceto categorias)
            'financeiro.view_transacao',
            'financeiro.add_transacao',
            'financeiro.change_transacao',
            'financeiro.delete_transacao',
            'financeiro.view_conta',
            'financeiro.add_conta',
            'financeiro.change_conta',
            'financeiro.delete_conta',
            'financeiro.view_categoria',  # Usa, não cria
            # Secretaria (ver dízimos)
            'secretaria.view_pessoa',
            # Comunicação
            'comunicacao.view_notificacao',
            # Agenda
            'agenda.view_compromisso',
        ]
        
        self.configurar_grupo(TESOUREIRO, permissoes, reset)

    def configurar_superintendente_ebd(self, reset):
        """
        Escopo: Local (EBD de uma igreja)
        - Gerencia turmas, professores, aulas
        - Gerencia matrículas e frequência
        """
        self.stdout.write("\n8️⃣  SUPERINTENDENTE EBD")
        
        permissoes = [
            # EBD (completo)
            'escola_biblica.view_turma',
            'escola_biblica.add_turma',
            'escola_biblica.change_turma',
            'escola_biblica.delete_turma',
            'escola_biblica.view_aluno',
            'escola_biblica.add_aluno',
            'escola_biblica.change_aluno',
            'escola_biblica.delete_aluno',
            'escola_biblica.view_aula',
            'escola_biblica.add_aula',
            'escola_biblica.change_aula',
            'escola_biblica.delete_aula',
            'escola_biblica.view_frequencia',
            'escola_biblica.add_frequencia',
            'escola_biblica.change_frequencia',
            'escola_biblica.delete_frequencia',
            # Secretaria (para matricular)
            'secretaria.view_pessoa',
            # Comunicação
            'comunicacao.view_mensagem',
            'comunicacao.add_mensagem',
            # Agenda
            'agenda.view_compromisso',
            'agenda.add_compromisso',
            'agenda.change_compromisso',
        ]
        
        self.configurar_grupo(SUPERINTENDENTE_EBD, permissoes, reset)

    def configurar_equipe_eventos(self, reset):
        """
        Escopo: Local (uma igreja)
        - Cria e edita eventos
        - Gerencia inscrições
        - Não pode deletar (histórico)
        """
        self.stdout.write("\n8️⃣  EQUIPE DE EVENTOS")
        
        permissoes = [
            # Eventos (sem delete)
            'eventos.view_evento',
            'eventos.add_evento',
            'eventos.change_evento',
            'eventos.view_inscricao',
            'eventos.add_inscricao',
            'eventos.change_inscricao',
            # Secretaria (para inscrições)
            'secretaria.view_pessoa',
            # Comunicação
            'comunicacao.add_mensagem',
            # Agenda
            'agenda.view_compromisso',
            'agenda.add_compromisso',
        ]
        
        self.configurar_grupo(EQUIPE_EVENTOS, permissoes, reset)

    def configurar_equipe_midia(self, reset):
        """
        Escopo: Local (uma igreja)
        - Produção audiovisual
        - Upload de mídias
        """
        self.stdout.write("\n9️⃣  EQUIPE DE MIDIA")
        
        permissoes = [
            # Comunicação (mídias)
            'comunicacao.view_mensagem',
            'comunicacao.add_mensagem',
            'comunicacao.change_mensagem',
            # Eventos (programação)
            'eventos.view_evento',
            # Agenda
            'agenda.view_compromisso',
        ]
        
        self.configurar_grupo(EQUIPE_MIDIA, permissoes, reset)

    def configurar_equipe_recepcao(self, reset):
        """
        Escopo: Local (uma igreja)
        - Cadastra visitantes
        - Registra presença
        - Não edita membros batizados
        """
        self.stdout.write("\n🔟 EQUIPE DE RECEPCAO")
        
        permissoes = [
            # Secretaria (limitado a visitantes)
            'secretaria.view_pessoa',
            'secretaria.add_pessoa',  # Apenas visitantes
            # Eventos (inscrições)
            'eventos.view_evento',
            'eventos.view_inscricao',
            'eventos.add_inscricao',
            # Comunicação
            'comunicacao.view_notificacao',
        ]
        
        self.configurar_grupo(EQUIPE_RECEPCAO, permissoes, reset)

    def configurar_professor_ebd(self, reset):
        """
        Escopo: Local (turma específica)
        - Dá aulas da sua turma
        - Registra frequência
        """
        self.stdout.write("\n1️⃣1️⃣ PROFESSORES EBD")
        
        permissoes = [
            # EBD (aulas e frequência)
            'escola_biblica.view_aula',
            'escola_biblica.add_aula',
            'escola_biblica.change_aula',
            'escola_biblica.view_frequencia',
            'escola_biblica.add_frequencia',
            'escola_biblica.change_frequencia',
            'escola_biblica.view_aluno',
            'escola_biblica.view_turma',
            # Secretaria (dados dos alunos)
            'secretaria.view_pessoa',
            # Comunicação
            'comunicacao.view_notificacao',
        ]
        
        self.configurar_grupo(PROFESSOR_EBD, permissoes, reset)

    def configurar_secretaria_ebd(self, reset):
        """
        Escopo: Local (EBD de uma igreja)
        - Registra presença
        - Gera relatórios
        - Não gerencia turmas
        """
        self.stdout.write("\n1️⃣2️⃣ SECRETARIA EBD")
        
        permissoes = [
            # EBD (frequência)
            'escola_biblica.view_frequencia',
            'escola_biblica.add_frequencia',
            'escola_biblica.view_turma',
            'escola_biblica.view_aluno',
            'escola_biblica.view_aula',
            # Secretaria
            'secretaria.view_pessoa',
            # Comunicação
            'comunicacao.view_notificacao',
        ]
        
        self.configurar_grupo(SECRETARIA_EBD, permissoes, reset)

    def configurar_membro_comum(self, reset):
        """
        Escopo: Sistema (próprios dados)
        - Edita próprio perfil
        - Inscreve-se em eventos
        """
        self.stdout.write("\n1️⃣3️⃣ MEMBRO COMUM")
        
        permissoes = [
            # Eventos (próprias inscrições)
            'eventos.view_evento',
            'eventos.add_inscricao',
            # Comunicação
            'comunicacao.view_notificacao',
            # Agenda (visualização pública)
            'agenda.view_compromisso',
        ]
        
        self.configurar_grupo(MEMBRO_COMUM, permissoes, reset)
