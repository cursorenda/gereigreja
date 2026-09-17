Pasta:
docs/adr/

Arquivo:
01-DepartamentoVinculo-Historico-e-Cargo.md

Documento:
ADR-01

Versão:
1.0

Status:
Aceito

Responsável:
Equipe de Engenharia

Data da decisão:
Agosto de 2026

# ADR-01 - DepartamentoVinculo, histórico e cargo único

## Contexto

O GereIgreja precisa representar membros e responsáveis de departamentos locais sem reutilizar `MembroCargo` como vínculo departamental e sem transformar organização em autorização.

## Decisão

Será criada a entidade `DepartamentoVinculo`, subordinada ao `Departamento` local, com membro, cargo opcional, `data_inicio` e `data_fim`.

- O vínculo ativo é identificado por `data_fim IS NULL`.
- Existirá no máximo um vínculo ativo por `(departamento, membro)`.
- Nesta versão, um vínculo ativo terá no máximo um cargo opcional.
- Encerramento preserva histórico; retorno e troca de cargo criam novo registro.
- `Cargo` será reutilizado como referência organizacional, sem efeito autorizativo.
- `DepartamentoVinculo` não altera `MembroCargo`, não sincroniza grupos e não concede módulos ou permissões.
- Pastor Local e Secretário Local operarão somente em igrejas explicitamente permitidas/em contexto, sem expansão hierárquica.
- Admin Ministério terá visão consolidada somente leitura por padrão.
- Toda escrita validará departamento, membro, igreja, usuário e ação no backend.

## Consequências

### Positivas

- histórico imutável e auditável;
- separação entre organização e autorização;
- isolamento local explícito;
- modelo mínimo compatível com a estrutura atual.

### Limitações aceitas

- múltiplos cargos simultâneos não são suportados;
- operação local por Admin Ministério não é implícita;
- uma futura mudança dessas regras exigirá novo ADR.

## Alternativas rejeitadas

- Reutilizar `MembroCargo`: possui sincronização automática de grupos e semântica de autorização.
- Many-to-many direto entre membro e departamento: não preserva adequadamente cargo, período e autoria.
- Reabrir vínculo encerrado: sobrescreve a história operacional.

## Controles obrigatórios

- `UniqueConstraint` condicional para vínculo ativo por departamento e membro;
- `CheckConstraint` garantindo `data_fim` nula ou maior/igual a `data_inicio`;
- validação transacional de mesma igreja;
- testes de IDOR, concorrência e ausência de efeitos em grupos.

## Documentos relacionados

- `docs/apps/05-Departamentos.md`
- `docs/governanca/05-Padroes-de-Models.md`
- `docs/governanca/10-Padroes-de-Permissoes.md`
- `docs/seguranca/05-Seguranca-Multi-Tenant.md`
