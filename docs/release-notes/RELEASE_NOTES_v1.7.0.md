# Release Notes v1.7.0

**Data:** 16/03/2026
**Versão:** v1.7.0

## Novidades e Melhorias

- Campo "Celular" adicionado ao cadastro de pessoas
- Formulário público reorganizado, máscaras JS, busca de endereço por CEP
- Página de sucesso do cadastro público modernizada
- Validações robustas: CPF, email, máscaras, ViaCEP, feedback visual
- Preview instantâneo da foto de perfil
- CSS responsivo e visual profissional para telas de pessoa
- Documentação técnica e de usuário atualizada
- Regras de negócio detalhadas para tipos/status de pessoa
- Sistema híbrido de participantes para eventos
- Refino visual e usabilidade em formulários, listas e detalhes
- Ajustes de máscaras, feedbacks e UX em campos obrigatórios e navegação
- Atualização do índice e organização da documentação

## Passos para Deploy

1. Faça pull do repositório
2. Rode as migrações: `python manage.py migrate`
3. Reinicie o serviço web
4. Valide as telas e funcionalidades

## Checklist pós-deploy
- [ ] Cadastro público funcionando
- [ ] Validações e máscaras ativas
- [ ] Campo celular visível e salvo
- [ ] Preview de foto funcionando
- [ ] Documentação acessível
- [ ] Listas, filtros e dashboards OK

---

**Versão anterior:** v1.6.0
**Autor:** GitHub Copilot
