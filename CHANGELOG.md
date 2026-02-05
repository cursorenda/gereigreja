## v1.1.2 — 04/02/2026
Correção de bugs

## v1.1.1 — 04/02/2026
# ⚠️ Arquivos modificados mas não commitados:

- [Não commitado] M CHANGELOG.md

- [Não commitado] M core/admin.py

- [Não commitado] M core/templatetags/versao.py

- [Não commitado] M secretaria/templates/secretaria/index.html

- [Não commitado] M secretaria/views.py

- [Não commitado] M templates/base_com_menu.html



Novo layout 100% largura: Página inicial da secretaria redesenhada, responsiva e moderna.

Bloco “Próximos eventos” aprimorado: Exibe eventos futuros com dia da semana, data, título e horários reais, visual idêntico ao modelo.

Cards padronizados: Atividades Recentes, Próximos Eventos e Gráfico agora com altura e bordas iguais, barra de rolagem nas atividades.

Gráfico de evolução ampliado: Altura aumentada para melhor visualização.

Barra de ações profissional: Botões de navegação (Dashboard, Listar Pessoas, Relatório, Agenda, Bancos, Ajuda/FAQ) agrupados à esquerda, com links corretos e design uniforme.

Busca centralizada: Campo de busca alinhado, com altura igual aos botões e espaçamento visual.

Cards informativos e aniversariantes: Cards de totais e aniversariantes com ícones, nomes e layout limpo.

Responsividade e espaçamento refinados: Layout adaptado para todas as telas, com alinhamento e espaçamento profissional.

Preparação para página de Ajuda/FAQ: Botão já disponível na barra de ações.

## v1.1.0 — 03/02/2026
- **Sistema de Deploy Automatizado**: novo app completo para gerenciar versões via Django Admin com seleção de tipo de versão (Patch, Minor, Major), detecção automática de mudanças Git, auto-população do changelog com commits filtrados, atualização automática de CHANGELOG.md e backup_log.txt, commit, tag e push automáticos, logs detalhados e acesso restrito a superusuários.
- **Backup Melhorado**: novo backup JSON que funciona no servidor usando Django dumpdata, backup de arquivos em ZIP com toda pasta /media, detecção inteligente de pg_dump com suporte Windows e Linux, mensagens de erro amigáveis com links para soluções alternativas, indicadores visuais no admin de quais backups funcionam em produção.
- **Release Notes**: criados 10 arquivos de release notes (v1.0.0 até v1.0.9) em formato user-friendly com emojis e template para futuras versões.
- **Interface Admin Aprimorada**: adicionado link "Deploy e Versionamento" em Ferramentas do Sistema, avisos coloridos indicando backups disponíveis em produção vs local, dica de fazer backup antes de deploy com links diretos.
- **Documentação**: template de release notes para padronização futura e instruções claras sobre execução local vs servidor.

## v1.0.9 — 02/02/2026
- **Novo Relatório Geral do Dia da EBD**: relatório consolidado com dados de todas as turmas, filtro inteligente por datas com lições cadastradas e comparativo automático com a aula anterior.
- **Dashboard EBD melhorado**: card "Turmas" renomeado para "Turmas e Chamadas" com descrição mais clara; card de Relatórios reestruturado com tooltip e botões diretos para "Cargos e Funções" e "Relatório Geral do Dia".
- **Correções na Chamada de Presença**: adicionada exibição de mensagens de sucesso/erro, garantido envio correto do campo data no POST e tratamento de erro quando formset é inválido.
- **Correção de tipo Decimal**: resolvido erro de incompatibilidade entre float e Decimal no cálculo de ofertas do relatório.
- **Filtros inteligentes**: relatório do dia filtra apenas turmas do ano letivo correto e com lições cadastradas na data selecionada.
- **Ajustes de responsividade**: melhorias no layout da lista de cargos para telas menores.

## v1.0.8 — 29/01/2026
- Deploy completo e reinicialização do ciclo de versionamento.
- Correção de erro de template (NoReverseMatch) na tela de confirmação de troca de senha.
- Atualização de arquivos estáticos e templates.
- Registro de backup e versionamento em backup_log.txt.

#
## v1.0.7 — 28/01/2026
- Melhorias completas no gerenciamento de cargos e ocupantes: botão "Finalizar vínculo" (mantém histórico), histórico de ocupantes visível, filtro de membros/obreiros ativos.
- Padronização dos templates de cadastro/edição de membro usando partial reutilizável, com comentários explicativos e ação dinâmica.
- Nova aba de histórico de cargos na edição de membro.
- Scripts de auditoria e correção adicionados em /scripts (auditoria de vínculos, correção de cargos, criação automática de membros, etc).
- Novos templates para Escola Bíblica: wizard de geração de lições, banner de período/trimestre, seleção para copiar dados do período anterior.
- Novas migrations aplicadas (configuração EBD, escola bíblica, secretaria).
- Ajustes de responsividade e largura máxima nas telas de cargos.
- Versionamento e registro deste deploy no backup_log.txt.

# Changelog
# Changelog

## v1.0.6 — 17/01/2026
- Exibição automática da versão e data do sistema no rodapé e no admin, com leitura do CHANGELOG.md, cache e mensagem amigável.

## v1.0.5 — 17/01/2026
 - Modernização e correção do fluxo de chamada de presença da EBD, com mensagens globais e feedbacks claros.
 - Unificação da página de associação de usuários com a página de usuários, simplificando a gestão.
 - Melhorias no dashboard da secretaria para visualização e navegação.
 - Ajustes e melhorias em templates de dashboards e menus.
 - Remoção de bugs e aprimoramento do tratamento de erros em formulários.
 - Refatoração de views e templates para maior clareza e usabilidade.
 - Outras pequenas melhorias visuais e funcionais em diversos módulos.

## v1.0.4 — 08/01/2026
- Dashboard totalmente responsivo, com gráficos dinâmicos e layout adaptável (flexbox, media queries)
- Correção do preenchimento automático do campo "igreja" no formulário de pessoa
- Ajuste: botões de ação aparecem apenas na aba correta na edição de pessoa
- Melhorias e correções na página de associação de usuários (erros corrigidos e usabilidade aprimorada)
- Remoção de arquivos temporários/desatualizados de templates
- Pequenas melhorias em JS e templates

## v1.0.3
- Correção de bugs na geração de relatórios
- Melhoria na performance do sistema

## v1.0.2
- Atualização da documentação do usuário
- Adição de novos testes automatizados

## v1.0.1
- Correção de pequenos bugs
- Ajustes na interface do usuário

## v1.0.0
- Primeira versão oficial do Gereigreja
- Padronização dos filtros da lista de membros
- Remoção do campo considerar_ativo_relatorios
- Ajuste visual dos filtros e campo de tags
- Correções de layout e usabilidade

## Como usar
- Para cada nova versão, adicione uma seção com o número da versão e as principais mudanças.
- Exemplo:
  ## v1.1.0
  - Nova funcionalidade X
  - Correção de bug Y
