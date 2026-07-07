# Documentação: Módulo de Grupos/Casas (GrupoCasa)

## Visão Geral
O módulo de Grupos/Casas permite agrupar pessoas (membros) que compartilham o mesmo endereço, facilitando o acompanhamento de famílias, células e visitas domiciliares. O agrupamento é feito automaticamente por endereço ou manualmente via comandos administrativos.

---

## Funcionamento do Agrupamento
- **Associação automática:**
  - Ao cadastrar ou atualizar o endereço de um membro, o sistema tenta associá-lo a um GrupoCasa existente com o mesmo endereço (normalizado).
  - Se não existir, cria um novo GrupoCasa automaticamente, desde que haja pelo menos dois membros no mesmo endereço.
- **Agrupamento em massa:**
  - Comando: `python manage.py agrupar_grupos_casa --preview` (gera relatório)
  - Comando: `python manage.py agrupar_grupos_casa --apply` (aplica agrupamento)
  - Pessoas são agrupadas por endereço normalizado (igreja, CEP, rua, número, complemento).
- **Filtro de status:**
  - Apenas membros com status "Ativo", "Desligado" ou "Em Disciplina" são considerados para agrupamento.

---

## Manutenção e Limpeza
- **Grupos vazios:**
  - Mudanças de endereço, exclusão ou alteração de status podem deixar grupos/casas sem moradores.
  - Grupos vazios poluem a interface e devem ser removidos periodicamente.
- **Remoção manual/automática:**
  - Comando: `python manage.py cleanup_empty_grupocasa --confirm` (remove grupos/casas sem moradores)
  - Use `--force` para remover mesmo se houver visitas associadas (atenção: pode perder histórico).
  - Recomenda-se rodar este comando após grandes alterações de membros.
- **Preenchimento de endereço:**
  - Comando: `python manage.py backfill_grupocasa_address --apply` (preenche bairro/cidade/estado do grupo a partir dos moradores)

---

## Boas Práticas
- Revise periodicamente os grupos/casas e execute a limpeza de grupos vazios.
- Oriente os usuários a manterem os endereços dos membros atualizados.
- Utilize os comandos administrativos após importações, grandes edições ou auditorias.
- Considere ocultar grupos/casas com zero membros na interface padrão para melhor experiência do usuário.

---

## Fluxo Resumido
1. Cadastro/edição de membro → associação automática a GrupoCasa por endereço.
2. Agrupamento em massa via comando para consolidar dados.
3. Limpeza periódica de grupos/casas vazios.
4. Preenchimento de endereço dos grupos a partir dos moradores.

---

## Comandos Úteis
- `python manage.py agrupar_grupos_casa --preview` — Gera relatório de agrupamento sugerido.
- `python manage.py agrupar_grupos_casa --apply` — Aplica agrupamento sugerido.
- `python manage.py cleanup_empty_grupocasa --confirm` — Remove grupos/casas sem moradores.
- `python manage.py cleanup_empty_grupocasa --force --confirm` — Remove inclusive grupos com visitas.
- `python manage.py backfill_grupocasa_address --apply` — Preenche endereço dos grupos a partir dos moradores.

---

## Observações
- O sistema não remove automaticamente grupos/casas vazios após alterações de membros; a limpeza deve ser feita manualmente ou agendada.
- Grupos/casas com visitas associadas não são removidos por padrão para preservar o histórico.
- O agrupamento considera apenas membros com status permitido.

---

## Sugestões Futuras
- Automatizar a limpeza de grupos/casas vazios via tarefa agendada.
- Adicionar botão de "Limpar grupos vazios" na interface administrativa.
- Exibir aviso ao editar grupo/casa vazio sugerindo exclusão.

---

*Esta documentação deve ser revisada e atualizada sempre que houver mudanças no fluxo de agrupamento, comandos ou regras de negócio do módulo de Grupos/Casas.*
