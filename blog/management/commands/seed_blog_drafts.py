from django.core.management.base import BaseCommand
from django.utils.text import slugify

from blog.models import Categoria, Post


POSTS = [
    {
        "titulo": "Como cadastrar membros no Gereigreja sem retrabalho",
        "categoria_slug": "tutoriais-do-sistema",
        "palavras_chave": "como cadastrar membros, tutorial gereigreja, secretaria de igreja",
        "resumo": "Aprenda um fluxo simples para cadastrar membros no Gereigreja com dados completos, organização e menos retrabalho na secretaria.",
        "conteudo": """
<p>Um cadastro bem feito evita correcoes, facilita relatorios e melhora o cuidado com cada pessoa da igreja.</p>
<h2>Comece pelos dados essenciais</h2>
<p>Antes de salvar, confirme nome completo, contato principal, data de nascimento e situacao do membro. Isso reduz inconsistencias futuras.</p>
<h2>Padronize o preenchimento</h2>
<ul>
  <li>Use o mesmo formato para telefone e endereco.</li>
  <li>Defina um responsavel pela revisao de dados.</li>
  <li>Evite abreviacoes diferentes para o mesmo campo.</li>
</ul>
<h2>Revise periodicamente</h2>
<p>Reserve um momento mensal para atualizar informacoes. Com dados corretos, a igreja comunica melhor e acompanha pessoas com mais atencao.</p>
""",
    },
    {
        "titulo": "Passo a passo para organizar familias e grupos no cadastro",
        "categoria_slug": "tutoriais-do-sistema",
        "palavras_chave": "grupos de membros, cadastro por familia, tutorial sistema igreja",
        "resumo": "Veja como estruturar familias e grupos no cadastro para facilitar acompanhamento pastoral, comunicacao e relatorios de membros.",
        "conteudo": """
<p>Organizar familias e grupos no sistema melhora o acompanhamento e traz mais clareza para lideres e secretaria.</p>
<h2>Defina criterios antes de cadastrar</h2>
<p>Escolha se a classificacao sera por nucleo familiar, ministerio ou faixa etaria. O importante e manter um padrao unico.</p>
<h2>Use grupos para acao pratica</h2>
<p>Grupos bem montados ajudam em convocacoes, cuidado pastoral e planejamento de atividades com menos trabalho manual.</p>
<h2>Evite duplicidade</h2>
<p>Antes de criar novos grupos, verifique se ja existe estrutura semelhante para manter o sistema limpo e facil de usar.</p>
""",
    },
    {
        "titulo": "Secretaria eficiente: 7 rotinas semanais que funcionam",
        "categoria_slug": "gestao-de-membros",
        "palavras_chave": "secretaria de igreja, rotina administrativa, gestao de membros",
        "resumo": "Conheca sete rotinas simples para manter a secretaria da igreja organizada, com menos urgencias e mais previsibilidade.",
        "conteudo": """
<p>Uma secretaria eficiente nao depende de correria, e sim de rotina clara e disciplinada.</p>
<h2>Rotinas que geram resultado</h2>
<ul>
  <li>Atualizar cadastros pendentes.</li>
  <li>Conferir aniversariantes e novos convertidos.</li>
  <li>Revisar comunicados e listas de contato.</li>
  <li>Validar relatorios de presenca e envolvimento.</li>
</ul>
<h2>Trabalhe com checklists</h2>
<p>Checklist reduz esquecimento e ajuda quando ha troca de equipe. O segredo e repeticao com qualidade.</p>
""",
    },
    {
        "titulo": "Como tratar transferencias de membros com seguranca",
        "categoria_slug": "gestao-de-membros",
        "palavras_chave": "transferencia de membros, cadastro igreja, secretaria",
        "resumo": "Entenda um processo seguro para entrada e saida de membros, preservando historico, comunicacao e organizacao da igreja.",
        "conteudo": """
<p>Transferencias exigem cuidado para preservar historico e acolher pessoas com transparencia.</p>
<h2>Padrao de entrada e saida</h2>
<p>Registre datas, motivo e igreja de origem ou destino. Essa trilha evita duvidas futuras e melhora a governanca.</p>
<h2>Comunique os envolvidos</h2>
<p>Secretaria, lideranca e pastoreio precisam da mesma informacao para que o processo seja pastoralmente saudavel.</p>
<h2>Mantenha historico intacto</h2>
<p>Evite apagar registros antigos. Historico bem preservado ajuda em relatorios e decisoes futuras.</p>
""",
    },
    {
        "titulo": "Dizimos e ofertas: como organizar o fluxo financeiro mensal",
        "categoria_slug": "financas-da-igreja",
        "palavras_chave": "dizimos e ofertas, fluxo financeiro igreja, tesouraria",
        "resumo": "Aprenda a estruturar o fluxo mensal de dizimos e ofertas com controle, transparencia e previsibilidade financeira.",
        "conteudo": """
<p>Um fluxo financeiro organizado protege a igreja e fortalece a confianca da comunidade.</p>
<h2>Estruture em etapas</h2>
<ul>
  <li>Recebimento e conferencia.</li>
  <li>Registro no sistema.</li>
  <li>Consolidacao por periodo.</li>
  <li>Prestacao de contas.</li>
</ul>
<h2>Evite controle paralelo</h2>
<p>Concentrar os registros no sistema reduz erro e melhora o acompanhamento da tesouraria ao longo do mes.</p>
""",
    },
    {
        "titulo": "Prestacao de contas na igreja: modelo claro e confiavel",
        "categoria_slug": "financas-da-igreja",
        "palavras_chave": "prestacao de contas igreja, transparencia financeira, gestao eclesiastica",
        "resumo": "Veja um modelo pratico de prestacao de contas para fortalecer transparencia, confianca da igreja e boa governanca financeira.",
        "conteudo": """
<p>Prestacao de contas nao e apenas obrigacao administrativa. E parte do testemunho e da boa gestao.</p>
<h2>Mostre o que importa</h2>
<p>Apresente entradas, saidas, saldos e destino dos principais investimentos com linguagem simples para todos entenderem.</p>
<h2>Periodicidade gera confianca</h2>
<p>Compartilhar relatorios em ciclos regulares evita ruido e demonstra compromisso com transparencia.</p>
<h2>Use dados consistentes</h2>
<p>Relatorio confiavel nasce de registro correto no dia a dia. Sem isso, a prestacao perde credibilidade.</p>
""",
    },
    {
        "titulo": "Papéis da lideranca: como distribuir responsabilidades com clareza",
        "categoria_slug": "lideranca-e-governanca",
        "palavras_chave": "lideranca na igreja, papeis ministeriais, governanca",
        "resumo": "Entenda como dividir responsabilidades entre lideres para evitar sobrecarga, retrabalho e falhas de comunicacao.",
        "conteudo": """
<p>Quando os papeis estao claros, a igreja ganha velocidade, unidade e previsibilidade.</p>
<h2>Defina responsavel por processo</h2>
<p>Cada area precisa de um dono visivel: secretaria, financeiro, comunicacao, eventos e discipulado.</p>
<h2>Escreva acordos simples</h2>
<p>Documento curto com atribuicoes e limites de decisao ajuda muito mais do que alinhamentos apenas verbais.</p>
<h2>Revise a cada trimestre</h2>
<p>Ministerios mudam. Ajustar responsabilidades periodicamente evita gargalos e conflitos.</p>
""",
    },
    {
        "titulo": "Governanca de ministerios: indicadores que ajudam a decidir",
        "categoria_slug": "lideranca-e-governanca",
        "palavras_chave": "governanca de ministerio, indicadores igreja, gestao eclesiastica",
        "resumo": "Descubra indicadores simples para acompanhar ministerios e tomar decisoes mais seguras na lideranca da igreja.",
        "conteudo": """
<p>Decidir com base em dados reduz improviso e melhora a efetividade dos ministerios.</p>
<h2>Indicadores essenciais</h2>
<ul>
  <li>Participacao em encontros.</li>
  <li>Retencao de voluntarios.</li>
  <li>Evolucao de novos convertidos.</li>
  <li>Execucao do planejamento mensal.</li>
</ul>
<h2>Dados para servir pessoas</h2>
<p>O objetivo dos indicadores nao e burocracia, e sim cuidado mais intencional com a igreja.</p>
""",
    },
    {
        "titulo": "Comunicacao da igreja: como melhorar alcance sem aumentar equipe",
        "categoria_slug": "comunicacao-e-engajamento",
        "palavras_chave": "comunicacao na igreja, engajamento de membros, avisos",
        "resumo": "Aprenda a organizar a comunicacao da igreja para atingir mais pessoas com clareza, sem depender de mais equipe.",
        "conteudo": """
<p>Boa comunicacao nao e sobre volume, e sobre consistencia e mensagem clara.</p>
<h2>Centralize o calendario</h2>
<p>Com um calendario unico de comunicacao, a equipe evita mensagens repetidas e conflitos de horario.</p>
<h2>Padrao de mensagem</h2>
<p>Use um modelo com data, local, objetivo e publico. Isso reduz duvidas e aumenta participacao.</p>
<h2>Acompanhe o retorno</h2>
<p>Observe quais formatos engajam melhor para aprimorar os proximos comunicados.</p>
""",
    },
    {
        "titulo": "WhatsApp da igreja: boas praticas para avisos que realmente funcionam",
        "categoria_slug": "comunicacao-e-engajamento",
        "palavras_chave": "whatsapp para igrejas, comunicados igreja, engajamento",
        "resumo": "Conheca boas praticas de WhatsApp para igrejas e envie avisos mais objetivos, com melhor leitura e participacao.",
        "conteudo": """
<p>WhatsApp pode aproximar pessoas ou gerar ruido. O resultado depende do metodo.</p>
<h2>Seja objetivo</h2>
<p>Mensagem curta, com chamada clara para acao, funciona melhor do que textos longos em horarios aleatorios.</p>
<h2>Evite excesso</h2>
<p>Defina frequencia de envios e publico correto para manter relevancia e nao cansar os membros.</p>
<h2>Integre com o sistema</h2>
<p>Dados atualizados no cadastro ajudam a segmentar melhor os comunicados.</p>
""",
    },
    {
        "titulo": "Como registrar frequencia da EBD de forma simples e confiavel",
        "categoria_slug": "escola-biblica-e-discipulado",
        "palavras_chave": "frequencia ebd, escola biblica dominical, gestao de ebd",
        "resumo": "Veja um metodo pratico para registrar frequencia da Escola Biblica com consistencia e usar os dados no acompanhamento.",
        "conteudo": """
<p>Frequencia bem registrada mostra quem esta caminhando e quem precisa de atencao pastoral.</p>
<h2>Padrao por turma</h2>
<p>Defina um formato unico para todas as classes. Padrao reduz divergencia e facilita consolidacao.</p>
<h2>Registre no mesmo dia</h2>
<p>Quanto mais proximo da aula, menor a chance de erro e esquecimento.</p>
<h2>Use os dados no discipulado</h2>
<p>Frequencia nao deve ficar no relatorio. Ela precisa orientar visitas e cuidado com cada pessoa.</p>
""",
    },
    {
        "titulo": "Discipulado com acompanhamento: como sair do improviso",
        "categoria_slug": "escola-biblica-e-discipulado",
        "palavras_chave": "discipulado na igreja, acompanhamento espiritual, ebd",
        "resumo": "Entenda como estruturar um discipulado com metas e acompanhamento real, evitando improviso e descontinuidade.",
        "conteudo": """
<p>Discipulado frutifero depende de intencionalidade, constancia e acompanhamento claro.</p>
<h2>Defina trilhas de crescimento</h2>
<p>Organize etapas para novos convertidos, membros em desenvolvimento e formacao de lideres.</p>
<h2>Acompanhe com indicadores simples</h2>
<p>Presenca, participacao e conclusao de etapas ja entregam uma visao importante para decisoes ministeriais.</p>
<h2>Integre lideranca e secretaria</h2>
<p>Quando ambos acompanham os mesmos dados, o cuidado pastoral se torna mais eficaz.</p>
""",
    },
    {
        "titulo": "Agenda da igreja sem conflitos: metodo semanal de planejamento",
        "categoria_slug": "agenda-e-eventos",
        "palavras_chave": "agenda da igreja, planejamento de cultos, calendario eclesiastico",
        "resumo": "Aprenda um metodo semanal para organizar agenda da igreja e reduzir conflitos de horario, equipes e espacos.",
        "conteudo": """
<p>Conflitos de agenda drenam energia da equipe. Planejamento semanal previne a maioria deles.</p>
<h2>Reuniao curta de alinhamento</h2>
<p>Reserve um momento fixo para validar eventos, espacos e responsaveis da semana seguinte.</p>
<h2>Calendario unico</h2>
<p>Evite agendas paralelas. Um unico calendario oficial evita choque de informacoes.</p>
<h2>Comunique com antecedencia</h2>
<p>Quando cada ministerio sabe o que vem pela frente, a execucao fica mais leve e previsivel.</p>
""",
    },
    {
        "titulo": "Como montar equipes e escalas para eventos sem sobrecarregar voluntarios",
        "categoria_slug": "agenda-e-eventos",
        "palavras_chave": "escalas de servico, eventos de igreja, voluntariado",
        "resumo": "Veja como montar escalas de servico equilibradas para eventos e cultos, evitando sobrecarga e melhorando a participacao.",
        "conteudo": """
<p>Escalas bem desenhadas valorizam pessoas e aumentam a qualidade da operacao nos eventos.</p>
<h2>Distribua por capacidade</h2>
<p>Considere disponibilidade real, competencia e frequencia de servico para cada voluntario.</p>
<h2>Planeje com antecedencia</h2>
<p>Escala em cima da hora gera faltas e retrabalho. Antecipacao melhora compromisso.</p>
<h2>Mantenha historico</h2>
<p>Registrar quem serviu e quando ajuda a equilibrar futuras distribuicoes.</p>
""",
    },
    {
        "titulo": "LGPD para igrejas: primeiros passos sem complicacao",
        "categoria_slug": "seguranca-e-boas-praticas",
        "palavras_chave": "lgpd para igrejas, protecao de dados membros, seguranca",
        "resumo": "Entenda os primeiros passos de LGPD na igreja para proteger dados dos membros com praticidade e responsabilidade.",
        "conteudo": """
<p>Adequacao a LGPD e um processo de maturidade. O importante e comecar com medidas objetivas.</p>
<h2>Mapeie dados coletados</h2>
<p>Saiba quais informacoes voce guarda, onde estao e quem acessa.</p>
<h2>Controle de acesso</h2>
<p>Nem todos precisam ver tudo. Permissao por funcao reduz risco de exposicao indevida.</p>
<h2>Politica simples e clara</h2>
<p>Uma orientacao interna curta ja ajuda equipe e lideranca a agir com mais seguranca.</p>
""",
    },
    {
        "titulo": "Seguranca no sistema: 10 ajustes que reduzem risco imediatamente",
        "categoria_slug": "seguranca-e-boas-praticas",
        "palavras_chave": "seguranca de dados igreja, boas praticas digitais, sistema de igreja",
        "resumo": "Confira dez ajustes rapidos para elevar a seguranca digital da igreja e proteger informacoes sensiveis dos membros.",
        "conteudo": """
<p>Pequenas configuracoes geram grande impacto em seguranca quando aplicadas com consistencia.</p>
<h2>Ajustes prioritarios</h2>
<ul>
  <li>Senha forte e troca periodica.</li>
  <li>Perfis com acesso minimo necessario.</li>
  <li>Revisao de usuarios inativos.</li>
  <li>Backup com rotina definida.</li>
</ul>
<h2>Treinamento da equipe</h2>
<p>Boa pratica tecnica precisa ser acompanhada de conscientizacao das pessoas que usam o sistema.</p>
""",
    },
    {
        "titulo": "Caso real: igreja local que organizou a secretaria em 60 dias",
        "categoria_slug": "historias-e-casos-de-uso",
        "palavras_chave": "caso de uso igreja, organizacao da secretaria, gereigreja",
        "resumo": "Conheca um caso pratico de igreja que reorganizou a secretaria em 60 dias com processos simples e foco em dados.",
        "conteudo": """
<p>Com prioridades claras e rotina bem definida, uma igreja local saiu do caos para uma operacao organizada em dois meses.</p>
<h2>Desafio inicial</h2>
<p>Cadastros incompletos, informacoes espalhadas e dificuldade de acompanhamento pastoral.</p>
<h2>Acoes aplicadas</h2>
<p>Padronizacao de cadastro, agenda semanal de revisao e comunicacao centralizada por processo.</p>
<h2>Resultado observado</h2>
<p>Mais previsibilidade, menos retrabalho e melhor visibilidade para decisoes da lideranca.</p>
""",
    },
    {
        "titulo": "Depoimento de lideranca: o que mudou com dados confiaveis",
        "categoria_slug": "historias-e-casos-de-uso",
        "palavras_chave": "depoimento de pastor, gestao de igreja, dados confiaveis",
        "resumo": "Veja como lideres perceberam ganhos reais em comunicacao, planejamento e cuidado pastoral apos organizar dados.",
        "conteudo": """
<p>Lideranca forte precisa de discernimento espiritual e informacao confiavel para decidir melhor.</p>
<h2>Antes e depois</h2>
<p>Antes: decisoes por percepcao parcial. Depois: visao mais clara de membros, eventos e prioridades.</p>
<h2>Beneficio para o pastoreio</h2>
<p>Com historico e acompanhamento, o cuidado se torna mais pessoal e menos reativo.</p>
<h2>Ganho para a equipe</h2>
<p>Processos claros reduziram urgencias e melhoraram a colaboracao entre ministerios.</p>
""",
    },
    {
        "titulo": "Novidades do Gereigreja: como acompanhar atualizacoes sem perder nada",
        "categoria_slug": "novidades-do-produto",
        "palavras_chave": "novidades gereigreja, atualizacao sistema, changelog",
        "resumo": "Saiba como acompanhar atualizacoes do Gereigreja de forma organizada e aplicar melhorias no dia a dia da igreja.",
        "conteudo": """
<p>Atualizacoes frequentes trazem valor quando a equipe sabe o que mudou e como usar.</p>
<h2>Crie rotina de leitura</h2>
<p>Reserve um horario mensal para revisar novidades e definir o que sera adotado primeiro.</p>
<h2>Priorize por impacto</h2>
<p>Comece pelas melhorias que economizam tempo da secretaria e da lideranca.</p>
<h2>Treine rapidamente</h2>
<p>Pequenos alinhamentos internos aceleram a adocao e evitam uso parcial das novas funcoes.</p>
""",
    },
    {
        "titulo": "Checklist de adocao de novas funcionalidades sem quebrar processos",
        "categoria_slug": "novidades-do-produto",
        "palavras_chave": "novas funcionalidades gereigreja, adocao de sistema, processos",
        "resumo": "Use este checklist para adotar novas funcionalidades do Gereigreja com seguranca, mantendo processos estaveis.",
        "conteudo": """
<p>Implementar novidade com metodo evita confusao e garante ganho real para a operacao.</p>
<h2>Checklist pratico</h2>
<ul>
  <li>Validar objetivo da funcionalidade.</li>
  <li>Testar em fluxo controlado.</li>
  <li>Treinar usuarios principais.</li>
  <li>Revisar resultado apos 30 dias.</li>
</ul>
<h2>Melhoria continua</h2>
<p>A cada ciclo, registre aprendizados para acelerar futuras implantacoes.</p>
""",
    },
]

POSTS_LOTE_2 = [
    {
        "titulo": "Painel de indicadores da igreja: como montar uma visao mensal objetiva",
        "categoria_slug": "tutoriais-do-sistema",
        "palavras_chave": "indicadores de igreja, dashboard gereigreja, relatorios administrativos",
        "resumo": "Aprenda a montar um painel mensal com os indicadores certos para acompanhar membros, eventos, comunicacao e rotina administrativa.",
        "conteudo": """
<p>Tomar decisao sem visao consolidada gera retrabalho. Um painel mensal ajuda lideranca e secretaria a agir com mais clareza.</p>
<h2>Comece com poucos indicadores</h2>
<p>Selecione de 5 a 8 metricas essenciais, como novos cadastros, presenca em atividades, movimentacoes de membros e cumprimento de agenda.</p>
<h2>Defina uma rotina de leitura</h2>
<p>Nao basta gerar relatorio. A equipe precisa revisar os dados em reuniao curta, com decisoes praticas para o proximo ciclo.</p>
""",
    },
    {
        "titulo": "Como configurar perfis e permissoes da equipe sem bloquear a operacao",
        "categoria_slug": "tutoriais-do-sistema",
        "palavras_chave": "permissoes no sistema, perfis de acesso igreja, seguranca operacional",
        "resumo": "Veja como configurar acessos por funcao para proteger dados e manter a operacao da igreja fluindo sem gargalos.",
        "conteudo": """
<p>Permissao bem desenhada protege informacoes sem travar o trabalho da equipe.</p>
<h2>Mapeie funcoes reais</h2>
<p>Antes de configurar perfis, liste quem executa cada processo: secretaria, financeiro, lideranca e comunicacao.</p>
<h2>Adote o minimo necessario</h2>
<p>Cada usuario deve ter apenas o acesso que precisa para sua rotina, reduzindo risco de alteracoes indevidas.</p>
""",
    },
    {
        "titulo": "Limpeza de cadastro legado: como corrigir dados antigos com metodo",
        "categoria_slug": "gestao-de-membros",
        "palavras_chave": "limpeza de cadastro, dados de membros, secretaria de igreja",
        "resumo": "Organize um plano de limpeza de cadastro para corrigir dados antigos sem parar a rotina da secretaria.",
        "conteudo": """
<p>Cadastros antigos e incompletos dificultam comunicacao e acompanhamento pastoral.</p>
<h2>Trabalhe por lotes pequenos</h2>
<p>Separe os registros por criterio, como familias, faixa etaria ou data de atualizacao, para corrigir com constancia.</p>
<h2>Valide com quem conhece as pessoas</h2>
<p>Apoio de lideres de ministerio e discipuladores acelera a confirmacao das informacoes.</p>
""",
    },
    {
        "titulo": "Recepcao e acompanhamento de novos membros: fluxo em 4 etapas",
        "categoria_slug": "gestao-de-membros",
        "palavras_chave": "novos membros, acolhimento igreja, acompanhamento pastoral",
        "resumo": "Estruture um fluxo de recepcao em quatro etapas para integrar novos membros com clareza e continuidade.",
        "conteudo": """
<p>Um bom acolhimento aumenta pertencimento e reduz evasao nos primeiros meses.</p>
<h2>Etapas recomendadas</h2>
<ul>
  <li>Cadastro inicial e contato de boas-vindas.</li>
  <li>Conexao com lideranca local.</li>
  <li>Insercao em grupo ou classe.</li>
  <li>Revisao de acompanhamento em 30 dias.</li>
</ul>
<p>Com etapas claras, a igreja acompanha pessoas com mais intencionalidade.</p>
""",
    },
    {
        "titulo": "Centros de custo por ministerio: quando e como aplicar",
        "categoria_slug": "financas-da-igreja",
        "palavras_chave": "centro de custo igreja, controle financeiro ministerios, tesouraria",
        "resumo": "Entenda quando usar centros de custo e como separar despesas por ministerio para ganhar visibilidade financeira.",
        "conteudo": """
<p>Sem separacao por area, fica dificil analisar onde o recurso esta sendo aplicado.</p>
<h2>Defina categorias simples</h2>
<p>Crie centros de custo objetivos, alinhados ao planejamento anual da igreja e aos principais ministerios.</p>
<h2>Analise mensalmente</h2>
<p>Relatorios por centro de custo ajudam a corrigir desvios antes que eles virem problemas maiores.</p>
""",
    },
    {
        "titulo": "Planejamento orcamentario anual da igreja: roteiro pratico",
        "categoria_slug": "financas-da-igreja",
        "palavras_chave": "orcamento anual igreja, planejamento financeiro eclesiastico, gestao financeira",
        "resumo": "Monte um planejamento orcamentario anual equilibrado, com previsao de receitas, despesas e prioridades ministeriais.",
        "conteudo": """
<p>Orcamento anual bem feito melhora previsibilidade e reduz decisoes emergenciais.</p>
<h2>Construa com lideres de area</h2>
<p>Financeiro e liderancas ministeriais devem colaborar para que o orcamento represente a realidade da igreja.</p>
<h2>Preveja margens de ajuste</h2>
<p>Inclua revisoes trimestrais para recalibrar prioridades conforme o andamento do ano.</p>
""",
    },
    {
        "titulo": "Reunioes de lideranca que geram decisao: pauta, tempo e acompanhamento",
        "categoria_slug": "lideranca-e-governanca",
        "palavras_chave": "reuniao de lideranca igreja, governanca ministerial, tomada de decisao",
        "resumo": "Aprenda a conduzir reunioes de lideranca mais objetivas, com pauta clara, tempo definido e acompanhamento real.",
        "conteudo": """
<p>Reuniao boa nao e longa. E clara, focada e termina com responsabilidades definidas.</p>
<h2>Estruture a pauta</h2>
<p>Separe o encontro em informacao, decisao e encaminhamento. Isso evita dispersao e melhora execucao.</p>
<h2>Finalize com donos e prazos</h2>
<p>Cada decisao precisa de responsavel e data de revisao para virar resultado.</p>
""",
    },
    {
        "titulo": "Sucessao de lideres sem ruptura: plano de transicao para ministerios",
        "categoria_slug": "lideranca-e-governanca",
        "palavras_chave": "sucessao de lideres, transicao ministerial, governanca da igreja",
        "resumo": "Veja como preparar transicoes de lideranca com antecedencia para preservar continuidade e saude ministerial.",
        "conteudo": """
<p>Transicao sem planejamento gera inseguranca e perda de ritmo nos ministerios.</p>
<h2>Prepare sucessores cedo</h2>
<p>Mapeie potenciais lideres, distribua responsabilidades e acompanhe evolucao de forma intencional.</p>
<h2>Registre processos-chave</h2>
<p>Documentar rotinas evita dependencia de pessoas especificas e facilita a passagem de bastao.</p>
""",
    },
    {
        "titulo": "Calendario de campanhas da igreja: como integrar comunicacao e agenda",
        "categoria_slug": "comunicacao-e-engajamento",
        "palavras_chave": "campanhas da igreja, calendario de comunicacao, engajamento",
        "resumo": "Organize campanhas e comunicados em um calendario integrado para aumentar alcance e evitar mensagens conflitantes.",
        "conteudo": """
<p>Campanhas bem coordenadas aumentam participacao e melhoram a experiencia da igreja.</p>
<h2>Planeje por ciclos</h2>
<p>Defina objetivos mensais, publico principal e canais de divulgacao para cada campanha.</p>
<h2>Alinhe com eventos e ministerios</h2>
<p>Comunicacao precisa conversar com o calendario da igreja para nao competir por atencao.</p>
""",
    },
    {
        "titulo": "Roteiro de avisos para culto: comunicacao clara em menos de 3 minutos",
        "categoria_slug": "comunicacao-e-engajamento",
        "palavras_chave": "avisos de culto, comunicacao objetiva, igreja local",
        "resumo": "Use um roteiro de avisos objetivo para comunicar o essencial no culto sem cansar a congregacao.",
        "conteudo": """
<p>Aviso eficiente e curto, relevante e acionavel.</p>
<h2>Formato recomendado</h2>
<p>Para cada aviso, informe o que e, para quem e quando acontece. Evite detalhes operacionais desnecessarios.</p>
<h2>Priorize o que gera acao</h2>
<p>Comunique primeiro o que exige resposta imediata da igreja.</p>
""",
    },
    {
        "titulo": "Trilha de 90 dias para novos convertidos: estrutura de acompanhamento",
        "categoria_slug": "escola-biblica-e-discipulado",
        "palavras_chave": "novos convertidos, trilha de discipulado, acompanhamento espiritual",
        "resumo": "Monte uma trilha de 90 dias para novos convertidos com etapas claras de integracao, ensino e acompanhamento.",
        "conteudo": """
<p>Os primeiros meses sao decisivos para consolidar fe, vinculo e participacao.</p>
<h2>Divida por fases</h2>
<p>Organize o processo em semanas com objetivos simples: conexao, fundamentos e insercao em comunidade.</p>
<h2>Use acompanhamento ativo</h2>
<p>Relacao pessoal e retorno frequente fazem diferenca no desenvolvimento espiritual.</p>
""",
    },
    {
        "titulo": "Como avaliar a saude da EBD com indicadores simples",
        "categoria_slug": "escola-biblica-e-discipulado",
        "palavras_chave": "saude da ebd, indicadores escola biblica, discipulado",
        "resumo": "Aprenda a medir a saude da Escola Biblica com indicadores simples para orientar melhorias de ensino e participacao.",
        "conteudo": """
<p>Sem medicao, a lideranca da EBD trabalha no escuro.</p>
<h2>Indicadores recomendados</h2>
<ul>
  <li>Presenca media por turma.</li>
  <li>Retencao ao longo do trimestre.</li>
  <li>Participacao em atividades complementares.</li>
</ul>
<p>Dados simples ja mostram onde agir com prioridade.</p>
""",
    },
    {
        "titulo": "Eventos em 30-60-90 dias: metodo para evitar correria",
        "categoria_slug": "agenda-e-eventos",
        "palavras_chave": "planejamento de eventos igreja, cronograma 30 60 90, agenda",
        "resumo": "Organize eventos da igreja com o metodo 30-60-90 dias para reduzir improviso e melhorar execucao.",
        "conteudo": """
<p>Eventos bem executados nascem de planejamento antecipado, nao de esforco de ultima hora.</p>
<h2>Marco de 90 dias</h2>
<p>Defina escopo, equipe principal, orcamento e indicadores de sucesso.</p>
<h2>Marco de 60 e 30 dias</h2>
<p>Refine comunicacao, escalas, fornecedores e checklist final para o dia do evento.</p>
""",
    },
    {
        "titulo": "Check-in e presenca em eventos grandes: fluxo para ganhar controle",
        "categoria_slug": "agenda-e-eventos",
        "palavras_chave": "check in evento igreja, controle de presenca, organizacao de eventos",
        "resumo": "Veja um fluxo de check-in para eventos grandes que melhora controle de presenca e tomada de decisao.",
        "conteudo": """
<p>Sem processo de check-in, a igreja perde visibilidade sobre participacao e capacidade.</p>
<h2>Planeje filas e equipes</h2>
<p>Defina pontos de entrada, equipe de apoio e responsavel por consolidar os dados ao final.</p>
<h2>Use os dados depois do evento</h2>
<p>Presenca registrada ajuda a planejar comunicacao e proximas edicoes com mais precisao.</p>
""",
    },
    {
        "titulo": "Politica de senhas para equipe da igreja: modelo simples e eficaz",
        "categoria_slug": "seguranca-e-boas-praticas",
        "palavras_chave": "politica de senhas igreja, seguranca digital, acesso ao sistema",
        "resumo": "Implemente uma politica de senhas simples para reduzir risco e proteger dados sensiveis da igreja.",
        "conteudo": """
<p>Boa politica de senha e uma das medidas mais baratas para elevar seguranca.</p>
<h2>Regras minimas</h2>
<p>Use senhas fortes, troca periodica e proibicao de compartilhamento entre usuarios.</p>
<h2>Treinamento rapido</h2>
<p>Equipe orientada evita erros comuns que comprometem dados e acessos.</p>
""",
    },
    {
        "titulo": "Backup e recuperacao: plano essencial para nao parar a operacao",
        "categoria_slug": "seguranca-e-boas-praticas",
        "palavras_chave": "backup de dados igreja, recuperacao de sistema, continuidade operacional",
        "resumo": "Aprenda a estruturar um plano de backup e recuperacao para manter a operacao da igreja em cenarios criticos.",
        "conteudo": """
<p>Nao basta ter backup. E preciso saber restaurar com rapidez e seguranca.</p>
<h2>Defina frequencia e responsabilidade</h2>
<p>Estabeleca rotina de backup, local de armazenamento e quem valida a execucao.</p>
<h2>Teste restauracao periodicamente</h2>
<p>Sem teste, o backup vira suposicao. Teste garante confianca quando houver incidente.</p>
""",
    },
    {
        "titulo": "Estudo de caso: como uma igreja reduziu faltas de voluntarios em eventos",
        "categoria_slug": "historias-e-casos-de-uso",
        "palavras_chave": "caso de uso voluntariado, faltas em escala, eventos de igreja",
        "resumo": "Conheca um estudo de caso pratico sobre reducao de faltas em escalas de voluntariado com ajustes simples de processo.",
        "conteudo": """
<p>Com pequenos ajustes de comunicacao e confirmacao, uma equipe reduziu faltas e aumentou previsibilidade.</p>
<h2>Mudancas aplicadas</h2>
<p>Escalas antecipadas, lembretes padronizados e canal unico para substituicoes.</p>
<h2>Resultado em poucas semanas</h2>
<p>Menos lacunas no dia do evento e melhor experiencia para participantes e servos.</p>
""",
    },
    {
        "titulo": "Relato pratico: integracao entre secretaria e pastoreio com dados unificados",
        "categoria_slug": "historias-e-casos-de-uso",
        "palavras_chave": "secretaria e pastoreio, dados unificados, gestao de membros",
        "resumo": "Veja um relato pratico de integracao entre secretaria e pastoreio para melhorar acompanhamento e comunicacao.",
        "conteudo": """
<p>Quando secretaria e pastoreio usam bases diferentes, o cuidado com pessoas perde ritmo.</p>
<h2>Chave da integracao</h2>
<p>Padrao unico de cadastro, rotina de atualizacao e reunioes de alinhamento com dados comuns.</p>
<h2>Beneficios observados</h2>
<p>Mais agilidade no acompanhamento e menos retrabalho para as equipes.</p>
""",
    },
    {
        "titulo": "Como priorizar melhorias do produto com base no uso real da equipe",
        "categoria_slug": "novidades-do-produto",
        "palavras_chave": "priorizacao de melhorias, adocao de funcionalidades, gereigreja",
        "resumo": "Aprenda a priorizar melhorias com base no uso real do sistema para acelerar ganhos operacionais da igreja.",
        "conteudo": """
<p>Nem toda novidade deve ser adotada ao mesmo tempo. Prioridade e o que resolve dor real.</p>
<h2>Criticos de priorizacao</h2>
<p>Impacto na rotina, facilidade de implementacao e quantidade de equipes beneficiadas.</p>
<h2>Rodadas curtas de adocao</h2>
<p>Implementar em ciclos curtos permite aprender e ajustar sem interromper a operacao.</p>
""",
    },
    {
        "titulo": "Changelog interno da igreja: como treinar equipe a cada atualizacao",
        "categoria_slug": "novidades-do-produto",
        "palavras_chave": "changelog interno, treinamento de equipe, atualizacoes do sistema",
        "resumo": "Estruture um changelog interno para treinar a equipe a cada atualizacao e melhorar adocao de novas funcionalidades.",
        "conteudo": """
<p>Atualizacao sem comunicacao interna vira funcionalidade subutilizada.</p>
<h2>Formato recomendado</h2>
<p>Registre o que mudou, quem e impactado e qual acao pratica deve ser feita pela equipe.</p>
<h2>Treinamento em micro encontros</h2>
<p>Alinhamentos curtos e frequentes aumentam aprendizagem e padronizam o uso do sistema.</p>
""",
    },
]


class Command(BaseCommand):
    help = "Cria lotes de posts em rascunho com conteudo profissional e SEO basico"

    def add_arguments(self, parser):
        parser.add_argument(
            "--lote",
            choices=["1", "2"],
            default="1",
            help="Seleciona o lote de conteudo a ser aplicado (padrao: 1).",
        )
        parser.add_argument(
            "--atualizar-existentes",
            action="store_true",
            help="Atualiza titulo, resumo, conteudo, categoria e SEO dos rascunhos ja existentes.",
        )

    @staticmethod
    def enriquecer_conteudo(item):
        return (
            item["conteudo"].strip()
            + """
<h2>Aplicacao pratica na rotina da igreja</h2>
<p>Para transformar este conteudo em resultado, defina um responsavel, um prazo curto e um criterio de revisao. O ideal e aplicar em ciclo de 30 dias e medir se houve reducao de retrabalho, mais clareza de dados e melhor comunicacao com a equipe.</p>
<h2>Erros comuns que devem ser evitados</h2>
<ul>
  <li>Fazer mudancas sem padrao definido para toda a equipe.</li>
  <li>Registrar informacoes em planilhas paralelas fora do sistema.</li>
  <li>Adiar revisoes, acumulando ajustes para momentos de urgencia.</li>
  <li>Executar processos sem checklist e sem validacao final.</li>
</ul>
<h2>Checklist rapido de implementacao</h2>
<ol>
  <li>Defina o objetivo principal da melhoria.</li>
  <li>Organize o passo a passo com quem executa cada etapa.</li>
  <li>Padronize o registro das informacoes no Gereigreja.</li>
  <li>Revise resultados e ajuste o processo ao final do periodo.</li>
</ol>
<p>Com consistencia e acompanhamento, pequenas melhorias geram ganho real de organizacao, transparencia e cuidado pastoral.</p>
<p><strong>Proximo passo:</strong> aplique este modelo no Gereigreja e avalie os resultados com sua equipe ainda nesta semana.</p>
"""
        )

    def handle(self, *args, **options):
        criados = 0
        existentes = 0
        atualizados = 0
        sem_categoria = []
        lote = options.get("lote", "1")
        posts = POSTS if lote == "1" else POSTS_LOTE_2
        atualizar_existentes = options.get("atualizar_existentes", False)

        for item in posts:
            categoria = Categoria.objects.filter(slug=item["categoria_slug"]).first()
            if not categoria:
                sem_categoria.append(item["categoria_slug"])
                continue

            slug = slugify(item["titulo"])
            post, created = Post.objects.get_or_create(
                slug=slug,
                defaults={
                    "titulo": item["titulo"],
                    "resumo": item["resumo"],
                    "conteudo": self.enriquecer_conteudo(item),
                    "categoria": categoria,
                    "palavras_chave": item["palavras_chave"],
                    "publicado": False,
                },
            )
            if created:
                criados += 1
            else:
                existentes += 1
                if atualizar_existentes and not post.publicado:
                    post.titulo = item["titulo"]
                    post.resumo = item["resumo"]
                    post.conteudo = self.enriquecer_conteudo(item)
                    post.categoria = categoria
                    post.palavras_chave = item["palavras_chave"]
                    post.save(update_fields=["titulo", "resumo", "conteudo", "categoria", "palavras_chave", "atualizado_em"])
                    atualizados += 1

        self.stdout.write(self.style.SUCCESS(f"Lote processado: {lote}"))
        self.stdout.write(self.style.SUCCESS(f"Rascunhos criados: {criados}"))
        self.stdout.write(self.style.WARNING(f"Rascunhos ja existentes: {existentes}"))
        self.stdout.write(self.style.SUCCESS(f"Rascunhos atualizados: {atualizados}"))
        if sem_categoria:
            faltantes = ", ".join(sorted(set(sem_categoria)))
            self.stdout.write(self.style.ERROR(f"Categorias nao encontradas: {faltantes}"))
