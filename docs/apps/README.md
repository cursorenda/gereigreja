# Apps - Documentação de Módulos

Apps
↓
O que foi construído.

Esta pasta concentra a documentação funcional e técnica por módulo do GereIgreja.

Finalidade da pasta:

- registrar o que existe em cada app;
- documentar jornadas, regras e integrações por domínio;
- consolidar inventário de componentes por módulo.

## Fronteira com docs/backend (evitar duplicação)

`docs/backend/` define padrões de engenharia (como construir).

`docs/apps/` documenta implementação de cada módulo (o que existe).

Exemplo correto:

- Backend: padrão para escrever Services.
- Apps: lista de Services existentes em Comunicação e suas responsabilidades.

## Como criar documentação de um novo App

1. Escolha o número do app no índice oficial.
2. Crie o arquivo no padrão `NN-NomeDoApp.md`.
3. Estruture o conteúdo com foco no domínio do módulo:
	escopo, jornadas, serviços/selectors existentes, segurança, testes e integrações.
4. Referencie padrões técnicos de `docs/backend/` sem duplicar regras gerais.
5. Atualize este README e o `docs/INDEX.md`.

## Padrão de Nomenclatura

- `NN-NomeDoApp.md`
- `NN` com dois dígitos e ordem fixa para estabilidade de navegação.

## Índice de Apps

- 01-Membros.md
- 02-Secretaria.md
- 03-Financeiro.md
- [04-Comunicacao.md](04-Comunicacao.md)
- 05-EBD.md
- 06-Eventos.md
- 07-Patrimonio.md
- 08-Usuarios.md
- 09-Configuracoes.md
- 10-Dashboard.md
- 11-Core.md

Observação: os arquivos ainda não existentes serão adicionados conforme a documentação de cada módulo for consolidada.
