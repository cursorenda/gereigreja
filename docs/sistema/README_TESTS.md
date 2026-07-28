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

3.1) Runner equivalente com descoberta robusta (recomendado para escopo por pasta)

```powershell
python -m pytest -q
```

Exemplo por módulo/pasta:

```powershell
python -m pytest core -q
```

Notas:
- O `pytest.ini` do projeto já aponta para `core.settings_test`.
- Em cenários específicos de descoberta (ex.: alguns rótulos como `core.tests` no `manage.py test`), o pytest pode ser mais estável.
- Para consistência de equipe/CI, escolha um runner oficial por pipeline e mantenha o mesmo comando em todas as execuções.

3.2) Runner oficial padronizado do projeto

```powershell
python scripts/automation/test_runner.py
```

Exemplo por escopo:

```powershell
python scripts/automation/test_runner.py core
```

Este runner encapsula o padrão do projeto (pytest + `core.settings_test`) para reduzir divergências entre ambiente local e pipeline.

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

## Testes de Permissões de Professores EBD (v1.2.2)

### 📚 O que testa

Arquivo: `escola_biblica/tests/test_professor_permissions.py`

**Sistema de permissões granulares** onde:
- ✅ Professores podem acessar **apenas suas turmas**
- ✅ Professores podem fazer **chamada de presença de suas turmas**
- ✅ Professores veem **apenas alunos de suas turmas**
- ❌ Professores **NÃO podem** criar/editar/excluir turmas
- ❌ Professores **NÃO podem** criar/transferir alunos

### 🧪 Como rodar os testes

**Rodar todos os testes de permissões de professores:**
```powershell
python manage.py test escola_biblica.tests.test_professor_permissions --settings=core.settings_test -v2
```

**Rodar apenas teste específico:**
```powershell
# Teste: Professor pode acessar chamada da própria turma
python manage.py test escola_biblica.tests.test_professor_permissions.ProfessorPermissionsTestCase.test_pode_acessar_chamada_turma_professor_propria_turma --settings=core.settings_test -v2

# Teste: Professor NÃO pode acessar turma de outro professor
python manage.py test escola_biblica.tests.test_professor_permissions.ProfessorPermissionsTestCase.test_nao_pode_acessar_chamada_turma_outro_professor --settings=core.settings_test -v2

# Teste: Professor NÃO pode criar turma
python manage.py test escola_biblica.tests.test_professor_permissions.ProfessorCRUDRestrictionsTestCase.test_professor_nao_pode_criar_turma --settings=core.settings_test -v2
```

**Rodar toda a suíte EBD:**
```powershell
python manage.py test escola_biblica.tests --settings=core.settings_test -v2
```

### 📊 Cobertura de testes

**Classes de teste:**
1. `ProfessorPermissionsTestCase` (20+ testes)
   - Funções helper (`pode_acessar_chamada_turma`, `get_turmas_professor`, `pode_ver_aluno`)
   - Views com permissões granulares (`chamada_presenca`, `turma_list`, `aluno_list`, `aluno_detail`)
   - Edge cases (cargo inativo, sem perfil, superuser)
   - Integridade (autenticação obrigatória)

2. `ProfessorCRUDRestrictionsTestCase` (4 testes)
   - Restrições de CRUD (professor não pode criar/editar/excluir turmas)
   - Restrições de gestão de alunos

**Cenários testados:**
- ✅ Professor acessa sua turma → 200 OK
- ✅ Professor tenta acessar turma alheia → 403 Forbidden
- ✅ Secretário EBD acessa qualquer turma → 200 OK
- ✅ Usuário comum tenta acessar → 403 Forbidden
- ✅ Usuário não autenticado → 302 Redirect to login
- ✅ Professor com cargo inativo → 403 Forbidden
- ✅ Superuser → Acesso total (bypass)

### 🔧 Estrutura dos testes

```python
# Setup completo com:
- 2 Professores (A e B) cada um com sua turma
- 1 Secretário EBD (acesso total)
- 1 Usuário comum (sem permissões)
- Cargos de Professor EBD ativos
- Turmas vinculadas aos professores via ManyToMany
- Alunos matriculados em cada turma

# Teste exemplo:
def test_chamada_presenca_view_professor_propria_turma(self):
    """Professor pode acessar view de chamada de sua turma (200 OK)."""
    self.client.login(username='professor_a', password='senha123')
    url = reverse('escola_biblica:chamada_presenca', kwargs={'turma_id': self.turma_a.id})
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)  # ✅ Sucesso
```

### 🐛 Troubleshooting

**Erro: `DoesNotExist: Ministerio matching query`**
- Causa: Banco de testes não tem dados de setup
- Solução: Use `--settings=core.settings_test` para criar banco em memória limpo

**Erro: `IntegrityError: NOT NULL constraint`**
- Causa: Relacionamentos entre modelos incompletos
- Solução: Verifique se `setUpTestData` cria todos os objetos necessários (Ministerio → Igreja → Membro → Cargo)

**Erro: `OperationalError: no such table`**
- Causa: Migrações não aplicadas no banco de testes
- Solução: Django cria tabelas automaticamente com `settings_test.py`, mas se persistir, rode:
  ```powershell
  python manage.py migrate --settings=core.settings_test
  ```

### 📝 Adicionando novos testes

Para adicionar testes de permissões customizadas:

1. **Copie o padrão de setup** de `ProfessorPermissionsTestCase.setUpTestData()`
2. **Crie função helper de permissão** (ex: `pode_editar_licao(user, licao)`)
3. **Teste a função isoladamente** antes de testar a view
4. **Teste todos os cenários**: acesso permitido, negado, edge cases
5. **Documente com docstrings** o que cada teste valida

Exemplo:
```python
def test_professor_pode_editar_licao_sua_turma(self):
    """Professor pode editar lição de sua própria turma."""
    licao = Licao.objects.create(turma=self.turma_a, data=date.today())
    pode_editar = pode_editar_licao(self.user_professor_a, licao)
    self.assertTrue(pode_editar)

def test_professor_nao_pode_editar_licao_turma_alheia(self):
    """Professor NÃO pode editar lição de turma de outro professor."""
    licao = Licao.objects.create(turma=self.turma_b, data=date.today())
    pode_editar = pode_editar_licao(self.user_professor_a, licao)
    self.assertFalse(pode_editar)
```

---

Se quiser que eu adicione esse README ao repositório como `README_TESTS.md`, eu já fiz. Se preferir um README em português mais detalhado ou um arquivo `CONTRIBUTING.md` com instruções ampliadas, eu posso criar também.
