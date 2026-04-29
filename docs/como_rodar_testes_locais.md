# Como rodar os testes localmente (banco em memória)

Para rodar os testes do Django localmente, sem depender do PostgreSQL, utilize o banco SQLite em memória já configurado no projeto.

## Comando recomendado

Execute no terminal, na raiz do projeto:

```
python manage.py test --settings=core.settings_test
```

- Isso garante que os testes rodem com banco de dados isolado, rápido e sem afetar dados reais.
- Não é necessário criar ou configurar banco de dados manualmente.

## Observações
- O arquivo `core/settings_test.py` já está pronto para isso.
- Se preferir, também pode usar `core/test_settings.py` (ambos usam SQLite em memória).
- Sempre utilize o parâmetro `--settings` para evitar que os testes rodem no banco de produção.

---

**Executor:**
- Qualquer desenvolvedor local.
- Não requer acesso ao PostgreSQL nem variáveis de ambiente do Render.

---

Dúvidas? Consulte este arquivo ou peça orientação ao responsável técnico.
