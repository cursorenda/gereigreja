"""
Comando para sincronizar grupos com permissões apropriadas.
Garante que a estrutura de grupos e permissions está alinhada com a hierarquia definida.

Uso:
    python manage.py sync_groups_permissions
    
    Flags:
    --dry-run: Mostra o que seria feito sem aplicar mudanças
    --force: Sobrescreve permissions existentes sem perguntar
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from contas.constants import (
    ADMIN_MINISTERIO,
    LIDERANCA_SECRETARIA,
    LIDERANCA_FINANCEIRA,
    PASTOR_REGIONAL,
    PASTOR_LOCAL,
    SECRETARIO_LOCAL,
    TESOUREIRO,
    SUPERINTENDENTE_EBD,
    PROFESSOR_EBD,
    SECRETARIA_EBD,
    EQUIPE_EVENTOS,
    EQUIPE_MIDIA,
    EQUIPE_RECEPCAO,
    MEMBRO_COMUM,
)


class Command(BaseCommand):
    help = 'Sincroniza grupos com permissions apropriadas baseado na hierarquia do sistema'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem aplicar mudanças',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Sobrescreve permissions sem perguntar',
        )
    
    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.force = options['force']
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODO DRY-RUN: Nenhuma mudança será aplicada\n'))
        
        self.stdout.write(self.style.HTTP_INFO('🔄 Sincronizando grupos e permissions...\n'))
        
        # Nível 1: Administrativo
        self.stdout.write(self.style.HTTP_INFO('📊 NÍVEL 1: ADMINISTRATIVO'))
        self.configurar_admin_ministerio()
        
        # Nível 2: Liderança Ministerial
        self.stdout.write(self.style.HTTP_INFO('\n📊 NÍVEL 2: LIDERANÇA MINISTERIAL'))
        self.configurar_lideranca_secretaria()
        self.configurar_lideranca_financeira()
        
        # Nível 3: Liderança Regional
        self.stdout.write(self.style.HTTP_INFO('\n📊 NÍVEL 3: LIDERANÇA REGIONAL'))
        self.configurar_pastor_regional()
        
        # Nível 4: Operacional Local
        self.stdout.write(self.style.HTTP_INFO('\n📊 NÍVEL 4: OPERACIONAL LOCAL'))
        self.configurar_pastor_local()
        self.configurar_secretario_local()
        self.configurar_tesoureiro()
        self.configurar_superintendente_ebd()
        
        # Nível 5: Equipes e Auxiliares
        self.stdout.write(self.style.HTTP_INFO('\n📊 NÍVEL 5: EQUIPES E AUXILIARES'))
        self.configurar_professor_ebd()
        self.configurar_secretaria_ebd()
        self.configurar_equipe_eventos()
        self.configurar_equipe_midia()
        self.configurar_equipe_recepcao()
        
        # Nível 6: Base
        self.stdout.write(self.style.HTTP_INFO('\n📊 NÍVEL 6: BASE'))
        self.configurar_membro_comum()
        
        if not self.dry_run:
            self.stdout.write(self.style.SUCCESS('\n✅ Sincronização concluída com sucesso!'))
        else:
            self.stdout.write(self.style.WARNING('\n✅ Simulação concluída. Use sem --dry-run para aplicar.'))
    
    def configurar_admin_ministerio(self):
        """Admin Ministerio: TODAS as permissions"""
        grupo, created = self._get_or_create_group(ADMIN_MINISTERIO)
        
        # Todas exceto admin, contenttypes, sessions
        todas = Permission.objects.exclude(
            content_type__app_label__in=['admin', 'contenttypes', 'sessions']
        )
        
        self._set_permissions(grupo, list(todas), created)
    
    def configurar_lideranca_secretaria(self):
        """Liderança Secretaria: Gestão de pessoas e comunicação (todas igrejas)"""
        grupo, created = self._get_or_create_group(LIDERANCA_SECRETARIA)
        
        permissoes = self._get_permissions([
            # Secretaria - acesso completo
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
            'secretaria.change_tag',
            
            # Eventos - visualização
            'eventos.view_evento',
            'eventos.view_inscricao',
            'eventos.view_presenca',
            
            # Comunicação - completo
            'comunicacao.view_notificacao',
            'comunicacao.add_notificacao',
            'comunicacao.change_notificacao',
            'comunicacao.delete_notificacao',
            'comunicacao.view_mensagem',
            'comunicacao.add_mensagem',
            
            # EBD - visualização
            'escola_biblica.view_turma',
            'escola_biblica.view_aluno',
            'escola_biblica.view_professor',
        ])
        
        self._set_permissions(grupo, permissoes, created)
    
    def configurar_lideranca_financeira(self):
        """Liderança Financeira: Gestão financeira consolidada (todas igrejas)"""
        grupo, created = self._get_or_create_group(LIDERANCA_FINANCEIRA)
        
        permissoes = self._get_permissions([
            # Financeiro - acesso completo
            'financeiro.view_lancamento',
            'financeiro.add_lancamento',
            'financeiro.change_lancamento',
            'financeiro.delete_lancamento',
            'financeiro.view_categoria',
            'financeiro.add_categoria',
            'financeiro.change_categoria',
            'financeiro.delete_categoria',
            'financeiro.view_conta',
            'financeiro.add_conta',
            'financeiro.change_conta',
            'financeiro.delete_conta',
            
            # Secretaria - visualização (para vincular dizimistas)
            'secretaria.view_pessoa',
            'secretaria.view_familia',
            
            # Eventos - visualização (para custos)
            'eventos.view_evento',
            
            # Comunicação - notificações
            'comunicacao.view_notificacao',
            'comunicacao.add_notificacao',
        ])
        
        self._set_permissions(grupo, permissoes, created)
    
    def configurar_pastor_regional(self):
        """Pastor Regional: Supervisiona várias igrejas (acesso amplo)"""
        grupo, created = self._get_or_create_group(PASTOR_REGIONAL)
        
        # Similar ao Liderança Secretaria + Liderança Financeira combinados
        permissoes = self._get_permissions([
            # Secretaria
            'secretaria.view_pessoa',
            'secretaria.add_pessoa',
            'secretaria.change_pessoa',
            'secretaria.view_cargo',
            'secretaria.view_familia',
            'secretaria.view_tag',
            
            # Financeiro - visualização
            'financeiro.view_lancamento',
            'financeiro.view_categoria',
            'financeiro.view_conta',
            
            # Eventos
            'eventos.view_evento',
            'eventos.add_evento',
            'eventos.change_evento',
            'eventos.view_inscricao',
            
            # Comunicação
            'comunicacao.view_notificacao',
            'comunicacao.add_notificacao',
            'comunicacao.add_mensagem',
            
            # EBD
            'escola_biblica.view_turma',
            'escola_biblica.view_aluno',
            'escola_biblica.view_professor',
        ])
        
        self._set_permissions(grupo, permissoes, created)
    
    def configurar_pastor_local(self):
        """Pastor Local: Gestão completa de UMA igreja"""
        grupo, created = self._get_or_create_group(PASTOR_LOCAL)
        
        permissoes = self._get_permissions([
            # Secretaria - quase completo (sem delete críticos)
            'secretaria.view_pessoa',
            'secretaria.add_pessoa',
            'secretaria.change_pessoa',
            'secretaria.view_cargo',
            'secretaria.add_cargo',
            'secretaria.change_cargo',
            'secretaria.view_familia',
            'secretaria.add_familia',
            'secretaria.change_familia',
            'secretaria.view_tag',
            
            # Financeiro - visualização + aprovação
            'financeiro.view_lancamento',
            'financeiro.view_categoria',
            'financeiro.view_conta',
            
            # Eventos - completo
            'eventos.view_evento',
            'eventos.add_evento',
            'eventos.change_evento',
            'eventos.delete_evento',
            'eventos.view_inscricao',
            'eventos.add_inscricao',
            
            # Comunicação - completo
            'comunicacao.view_notificacao',
            'comunicacao.add_notificacao',
            'comunicacao.change_notificacao',
            'comunicacao.add_mensagem',
            
            # EBD - visualização
            'escola_biblica.view_turma',
            'escola_biblica.view_aluno',
            'escola_biblica.view_professor',
            'escola_biblica.view_presenca',
        ])
        
        self._set_permissions(grupo, permissoes, created)
    
    def configurar_secretario_local(self):
        """Secretário Local: CRUD de membros e famílias"""
        grupo, created = self._get_or_create_group(SECRETARIO_LOCAL)
        
        permissoes = self._get_permissions([
            # Secretaria - acesso completo
            'secretaria.view_pessoa',
            'secretaria.add_pessoa',
            'secretaria.change_pessoa',
            'secretaria.delete_pessoa',
            'secretaria.view_cargo',
            'secretaria.add_cargo',
            'secretaria.change_cargo',
            'secretaria.view_familia',
            'secretaria.add_familia',
            'secretaria.change_familia',
            'secretaria.delete_familia',
            'secretaria.view_tag',
            'secretaria.add_tag',
            'secretaria.change_tag',
            
            # Eventos - visualização
            'eventos.view_evento',
            'eventos.view_inscricao',
            
            # Comunicação - envio
            'comunicacao.view_notificacao',
            'comunicacao.add_notificacao',
            'comunicacao.add_mensagem',
        ])
        
        self._set_permissions(grupo, permissoes, created)
    
    def configurar_tesoureiro(self):
        """Tesoureiro: Gestão financeira local"""
        grupo, created = self._get_or_create_group(TESOUREIRO)
        
        permissoes = self._get_permissions([
            # Financeiro - acesso completo
            'financeiro.view_lancamento',
            'financeiro.add_lancamento',
            'financeiro.change_lancamento',
            'financeiro.delete_lancamento',
            'financeiro.view_categoria',
            'financeiro.add_categoria',
            'financeiro.change_categoria',
            'financeiro.view_conta',
            'financeiro.add_conta',
            'financeiro.change_conta',
            
            # Secretaria - visualização (dizimistas)
            'secretaria.view_pessoa',
            'secretaria.view_familia',
            
            # Comunicação - notificações
            'comunicacao.view_notificacao',
            'comunicacao.add_notificacao',
        ])
        
        self._set_permissions(grupo, permissoes, created)
    
    def configurar_superintendente_ebd(self):
        """Superintendente EBD: Gestão completa da escola bíblica"""
        grupo, created = self._get_or_create_group(SUPERINTENDENTE_EBD)
        
        permissoes = self._get_permissions([
            # EBD - acesso completo
            'escola_biblica.view_turma',
            'escola_biblica.add_turma',
            'escola_biblica.change_turma',
            'escola_biblica.delete_turma',
            'escola_biblica.view_aluno',
            'escola_biblica.add_aluno',
            'escola_biblica.change_aluno',
            'escola_biblica.delete_aluno',
            'escola_biblica.view_professor',
            'escola_biblica.add_professor',
            'escola_biblica.change_professor',
            'escola_biblica.delete_professor',
            'escola_biblica.view_presenca',
            'escola_biblica.add_presenca',
            'escola_biblica.change_presenca',
            'escola_biblica.view_aula',
            'escola_biblica.add_aula',
            'escola_biblica.change_aula',
            
            # Secretaria - visualização
            'secretaria.view_pessoa',
            
            # Comunicação - notificações
            'comunicacao.view_notificacao',
            'comunicacao.add_notificacao',
        ])
        
        self._set_permissions(grupo, permissoes, created)
    
    def configurar_professor_ebd(self):
        """Professor EBD: Gestão de presença e aulas da sua turma"""
        grupo, created = self._get_or_create_group(PROFESSOR_EBD)
        
        permissoes = self._get_permissions([
            # EBD - restrito
            'escola_biblica.view_turma',
            'escola_biblica.view_aluno',
            'escola_biblica.view_presenca',
            'escola_biblica.add_presenca',
            'escola_biblica.change_presenca',
            'escola_biblica.view_aula',
            'escola_biblica.add_aula',
            'escola_biblica.change_aula',
        ])
        
        self._set_permissions(grupo, permissoes, created)
    
    def configurar_secretaria_ebd(self):
        """Secretaria EBD: Auxiliar administrativo da EBD"""
        grupo, created = self._get_or_create_group(SECRETARIA_EBD)
        
        permissoes = self._get_permissions([
            # EBD - visualização + presença
            'escola_biblica.view_turma',
            'escola_biblica.view_aluno',
            'escola_biblica.add_aluno',
            'escola_biblica.change_aluno',
            'escola_biblica.view_presenca',
            'escola_biblica.add_presenca',
            'escola_biblica.change_presenca',
            'escola_biblica.view_professor',
        ])
        
        self._set_permissions(grupo, permissoes, created)
    
    def configurar_equipe_eventos(self):
        """Equipe de Eventos: Organizar e gerenciar eventos"""
        grupo, created = self._get_or_create_group(EQUIPE_EVENTOS)
        
        permissoes = self._get_permissions([
            # Eventos - completo
            'eventos.view_evento',
            'eventos.add_evento',
            'eventos.change_evento',
            'eventos.view_inscricao',
            'eventos.add_inscricao',
            'eventos.change_inscricao',
            'eventos.view_presenca',
            'eventos.add_presenca',
            'eventos.change_presenca',
            
            # Secretaria - visualização (participantes)
            'secretaria.view_pessoa',
            
            # Comunicação - notificações
            'comunicacao.view_notificacao',
            'comunicacao.add_notificacao',
        ])
        
        self._set_permissions(grupo, permissoes, created)
    
    def configurar_equipe_midia(self):
        """Equipe de Mídia: Produção audiovisual e comunicação"""
        grupo, created = self._get_or_create_group(EQUIPE_MIDIA)
        
        permissoes = self._get_permissions([
            # Comunicação - completo
            'comunicacao.view_notificacao',
            'comunicacao.add_notificacao',
            'comunicacao.change_notificacao',
            'comunicacao.view_mensagem',
            'comunicacao.add_mensagem',
            
            # Eventos - visualização (para divulgação)
            'eventos.view_evento',
        ])
        
        self._set_permissions(grupo, permissoes, created)
    
    def configurar_equipe_recepcao(self):
        """Equipe de Recepção: Atendimento e registro de visitantes"""
        grupo, created = self._get_or_create_group(EQUIPE_RECEPCAO)
        
        permissoes = self._get_permissions([
            # Secretaria - visualização + adicionar visitantes
            'secretaria.view_pessoa',
            'secretaria.add_pessoa',  # Apenas para visitantes
            
            # Eventos - visualização
            'eventos.view_evento',
            'eventos.view_inscricao',
        ])
        
        self._set_permissions(grupo, permissoes, created)
    
    def configurar_membro_comum(self):
        """Membro Comum: Acesso mínimo (portal próprio)"""
        grupo, created = self._get_or_create_group(MEMBRO_COMUM)
        
        # Sem permissions especiais - apenas view próprio perfil
        permissoes = []
        
        self._set_permissions(grupo, permissoes, created)
    
    # ============== HELPERS ==============
    
    def _get_or_create_group(self, name):
        """Cria ou recupera grupo."""
        if self.dry_run:
            grupo = Group.objects.filter(name=name).first()
            if grupo:
                return grupo, False
            else:
                self.stdout.write(f"  [DRY-RUN] Criaria grupo: {name}")
                # Retorna objeto mock para dry-run
                return type('Group', (), {'name': name, 'permissions': type('Manager', (), {'set': lambda x: None, 'count': lambda: 0})()}), True
        else:
            return Group.objects.get_or_create(name=name)
    
    def _get_permissions(self, codename_list):
        """Busca permissions por codename (formato: 'app.codename')."""
        permissions = []
        
        for codename_full in codename_list:
            try:
                app_label, codename = codename_full.split('.')
                perm = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=codename
                )
                permissions.append(perm)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"    ⚠️  Permission não encontrada: {codename_full}")
                )
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f"    ❌ Formato inválido: {codename_full} (use 'app.codename')")
                )
        
        return permissions
    
    def _set_permissions(self, grupo, permissoes, created):
        """Atribui permissions ao grupo."""
        if self.dry_run:
            if created:
                status_symbol = "🆕"
                status_msg = "NOVO"
            else:
                status_symbol = "🔄"
                status_msg = f"ATUALIZAR ({grupo.permissions.count() if hasattr(grupo.permissions, 'count') else 0} → {len(permissoes)})"
            
            self.stdout.write(
                f"  {status_symbol} {grupo.name}: {status_msg} - {len(permissoes)} permissions"
            )
        else:
            if not self.force and not created:
                # Perguntar confirmação se já existe
                resposta = input(f"  Grupo '{grupo.name}' já existe. Sobrescrever permissions? (s/N): ")
                if resposta.lower() != 's':
                    self.stdout.write(f"  ⏭️  Pulando {grupo.name}")
                    return
            
            grupo.permissions.set(permissoes)
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ {grupo.name}: CRIADO com {len(permissoes)} permissions")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ {grupo.name}: ATUALIZADO para {len(permissoes)} permissions")
                )
