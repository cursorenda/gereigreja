# Organização do fluxo de Visitas e Visitantes

## Visitas (Acompanhamento de Visitas)
- O fluxo de visitas refere-se ao acompanhamento realizado pela igreja na casa das pessoas.
- As páginas e templates relacionados ao acompanhamento de visitas são:
  - `acompanhamentos_visita_list.html`: lista de acompanhamentos de visita
  - `registrar_acompanhamento_visita.html`: registro de novo acompanhamento
  - `ver_acompanhamento_visita.html`: detalhes do acompanhamento
  - `editar_acompanhamento_visita.html`: edição do acompanhamento
  - `excluir_acompanhamento_visita.html`: exclusão do acompanhamento
  - `escolher_pessoa_para_acompanhamento.html`: seleção de pessoa para acompanhamento
- Todos os links internos entre essas páginas apontam para o fluxo correto de visitas.
- Não há mais links para páginas de visitantes/recepção dentro do fluxo de visitas.

## Visitantes (Recepção)
- O fluxo de visitantes refere-se às pessoas que vêm à igreja, geralmente relacionado à recepção e eventos.
- As páginas de visitantes estão separadas e não misturadas com o fluxo de visitas.

## Organização e Manutenção
- O fluxo de visitas está centralizado e sem duplicidade.
- Links e breadcrumbs revisados para evitar mistura de fluxos.
- Caso novas páginas sejam criadas, garantir que o fluxo de visitas e visitantes permaneça separado.

---

Última revisão: 14/11/2025
Alteração: Removido link para "Lista de Visitantes" do template `registrar_acompanhamento_visita.html` e substituído por "Lista de Visitas".
