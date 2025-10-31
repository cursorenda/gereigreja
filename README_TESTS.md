# Executando testes locais (modo rápido com SQLite em memória)

Este README explica como executar rapidamente testes unitários isolados do seu banco remoto (Supabase). Use este modo quando você quiser rodar testes unitários sem tocar no banco de produção ou no banco de testes remoto.

1) O que foi adicionado
- `core/settings_test.py`: arquivo de configurações de teste que:
  - Usa SQLite em memória como `DATABASES['default']`.
  - Habilita `MD5PasswordHasher` para acelerar criação de usuários.
  - Usa `locmem` para email e `FileSystemStorage` para arquivos.
  - Desabilita migrações para apps locais (por exemplo, `secretaria`, `eventos`, `financeiro`, etc.) para evitar conflitos de migração em bancos em memória.

- `secretaria/test_migrations/`: conjunto de migrações vazias para satisfazer a dependência do grafo de migrações enquanto o Django cria tabelas diretamente a partir dos modelos durante os testes.

2) Como rodar um teste específico
No PowerShell na raiz do projeto:

```powershell
python manage.py test eventos.tests.test_evento_sessao -v2 --settings=core.settings_test
```

3) Como rodar toda a suíte de testes (levantar para toda a base)

```powershell
python manage.py test --settings=core.settings_test
```

4) Nota sobre segurança e produção
- `core/settings_test.py` é apenas para desenvolvimento local/CI; não use essas configurações em produção.
- Desabilitar migrações em memória é um atalho prático para testes unitários, mas testes que dependem de comportamento de migrações podem falhar.

5) Se você preferir usar Postgres/ Supabase para testes
- Você pode usar `--keepdb` para evitar que o Django tente DROPar e recriar o banco de testes.
- Se o banco de testes estiver sujo, drope `test_postgres` pelo painel do Supabase ou use `psql` para remover e recriá-lo.

6) Tradução das mudanças recentes (resumo)
- Removidos chips duplicados nas telas de criação/edição de eventos; agora usamos apenas Select2 para seleção de convidados.
- Ajustes no `eventos/forms.py` para garantir que, ao editar um evento, o campo `igreja` mostre a igreja salva e permita trocar apenas para igrejas do mesmo ministério.
- Layout dos formulários `criar_evento.html` e `editar_evento.html` compactado para uma linha com `Igreja`, `Título`, `Tipo`, `Local` conforme solicitado.
- Implementado `EventoSessao` (modelo) para representar sessões/dias de um evento e adicionado FK `sessao` em `ParticipacaoEvento`.
- Sinal `post_save` para `Evento` que cria automaticamente sessões com base em `quantidade_dias`.
- Ajustes em `marcar_presenca_evento` (view) e template para permitir seleção de sessão e salvar presença por sessão.
- Criada migração `eventos/migrations/0009...` e testes unitários para `EventoSessao`.
- Adicionado `core/settings_test.py` e ajustes para rodar testes localmente sem afetar Supabase.

7) Se ocorrerem erros de migração ao usar `core.settings_test.py`
- Verifique mensagens do Django que instruem a rodar `makemigrations --merge` ou que alertam sobre nós folha múltiplos. Eu gerei migrações de teste vazias para `secretaria` para corrigir o grafo de migração no modo de testes; se outros apps apresentarem problemas, avise que eu adiciono migrações vazias para eles também.

---

Se quiser que eu adicione esse README ao repositório como `README_TESTS.md`, eu já fiz. Se preferir um README em português mais detalhado ou um arquivo `CONTRIBUTING.md` com instruções ampliadas, eu posso criar também.
