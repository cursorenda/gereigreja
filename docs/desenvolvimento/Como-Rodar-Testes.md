# Como rodar os testes localmente (banco em memória)

Para rodar os testes do Django localmente, sem depender do PostgreSQL, utilize o banco SQLite em memória já configurado no projeto.

## Comando recomendado (padrão Django)

Execute no terminal, na raiz do projeto:

```
python manage.py test --settings=core.settings_test
```

- Isso garante que os testes rodem com banco de dados isolado, rápido e sem afetar dados reais.
- Não é necessário criar ou configurar banco de dados manualmente.

## Comando equivalente (pytest)

Quando houver necessidade de descoberta mais robusta por pacote/pasta de testes,
utilize o pytest com o mesmo settings de teste:

```
python -m pytest -q
```

Exemplo por escopo:

```
python -m pytest core -q
```

- O projeto já possui `pytest.ini` com `DJANGO_SETTINGS_MODULE = core.settings_test`.
- Este modo evita inconsistências pontuais de descoberta em alguns rótulos do `manage.py test`.

## Comando oficial padronizado (equipe/CI)

Para manter consistência entre máquinas e pipeline, use o runner padrão do projeto:

```
python scripts/automation/test_runner.py
```

Exemplo por escopo:

```
python scripts/automation/test_runner.py core
```

## Observações
- O arquivo `core/settings_test.py` já está pronto para isso.
- Testes que precisam executar migrations reais devem usar `core.settings_test_migrations`, também com SQLite em memória.
- Sempre utilize o parâmetro `--settings` para evitar que os testes rodem no banco de produção.
- Comandos locais que não sejam testes usam `core.settings_local` por padrão e nunca carregam o `.env`.

---

**Executor:**
- Qualquer desenvolvedor local.
- Não requer acesso ao PostgreSQL nem variáveis de ambiente do Render.

---

Dúvidas? Consulte este arquivo ou peça orientação ao responsável técnico.
