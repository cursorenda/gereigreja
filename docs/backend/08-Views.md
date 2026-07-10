Pasta:
docs/backend/

Arquivo:
08-Views.md

Documento:
GBE-08

Seção:
Backend

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# 08 - Views

> "A View coordena a requisição. A inteligência pertence aos Services."

---

# Sumário

1. Objetivo
2. Filosofia das Views
3. Papel das Views na Arquitetura
4. Responsabilidades
5. O que NÃO pertence às Views
6. Fluxo Oficial da Requisição
7. Estrutura Oficial
8. Function Based Views vs Class Based Views
9. Organização das Views
10. Comunicação com Forms
11. Comunicação com Services
12. Comunicação com Selectors
13. Boas Práticas
14. Documentos Relacionados
15. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para implementação das Views do GereIgreja.

Seu objetivo é garantir que todas as Views da plataforma permaneçam pequenas, organizadas e focadas exclusivamente na coordenação das requisições HTTP.

Toda lógica de negócio deverá permanecer fora das Views.

---

# 2. Filosofia das Views

As Views representam a camada de entrada da aplicação.

Sua responsabilidade é receber uma requisição, encaminhá-la para a camada adequada e devolver uma resposta ao usuário.

No GereIgreja adotamos o seguinte princípio:

> **Views coordenam. Services executam.**

Uma View nunca deverá concentrar regras de negócio.

---

# 3. Papel das Views na Arquitetura

Fluxo oficial:

```text
Usuário

↓

URL

↓

View

↓

Form / Serializer

↓

Service

↓

Selector

↓

Model

↓

Banco de Dados

↓

Resposta
```

As Views funcionam como ponto de integração entre o navegador (ou API) e as demais camadas da aplicação.

---

# 4. Responsabilidades

As Views poderão ser responsáveis por:

- receber requisições HTTP;
- validar o método da requisição;
- instanciar Forms ou Serializers;
- verificar autenticação;
- verificar permissões;
- chamar Services;
- recuperar dados por meio de Selectors;
- montar o contexto;
- renderizar Templates;
- devolver respostas HTTP.

---

# 5. O que NÃO pertence às Views

As Views não deverão conter:

- regras de negócio;
- cálculos complexos;
- consultas SQL;
- consultas extensas ao ORM;
- integrações externas;
- envio de e-mails;
- geração de relatórios;
- processamento financeiro;
- auditoria;
- importações;
- exportações.

Essas responsabilidades pertencem às camadas especializadas.

---

# 6. Fluxo Oficial da Requisição

Fluxo recomendado:

```text
Receber Request

↓

Verificar autenticação

↓

Verificar permissões

↓

Instanciar Form ou Serializer

↓

Validar entrada

↓

Chamar Service

↓

Obter resultado

↓

Renderizar resposta
```

Cada etapa possui uma responsabilidade específica.

---

# 7. Estrutura Oficial

Cada App deverá possuir seu próprio arquivo de Views.

Exemplo:

```text
views.py
```

Quando o módulo crescer, utilizar diretório próprio:

```text
views/

__init__.py

membros.py

familias.py

ministerios.py

financeiro.py

eventos.py

relatorios.py
```

A divisão deverá seguir o domínio de negócio.

---

# 8. Function Based Views vs Class Based Views

O GereIgreja adotará preferencialmente **Class Based Views (CBVs)** para interfaces web, aproveitando a reutilização oferecida pelo Django.

As **Function Based Views (FBVs)** poderão ser utilizadas em cenários específicos, quando proporcionarem maior simplicidade e legibilidade.

A escolha deverá considerar:

- clareza;
- reutilização;
- facilidade de manutenção;
- aderência aos padrões da plataforma.

A consistência arquitetural é mais importante do que a preferência pessoal do desenvolvedor.

---

# 9. Organização das Views

As Views deverão ser organizadas por domínio.

Exemplo:

```text
views/

membros.py

familias.py

financeiro.py

eventos.py

relatorios.py

dashboard.py
```

Evitar arquivos com centenas de linhas contendo funcionalidades de múltiplos módulos.

---

# 10. Comunicação com Forms

As Views deverão delegar aos Forms a validação estrutural dos dados.

Exemplo:

```python
form = MembroForm(request.POST)

if form.is_valid():
    MembroService.criar(
        form.cleaned_data
    )
```

A View não deverá repetir validações já realizadas pelo Form.

---

# 11. Comunicação com Services

Toda operação que altere o estado da aplicação deverá ser executada por um Service.

Exemplo:

```python
MembroService.atualizar(
    membro,
    form.cleaned_data
)
```

As Views não deverão acessar os Models diretamente para realizar alterações.

---

# 12. Comunicação com Selectors

Quando uma funcionalidade envolver apenas leitura de dados, a View poderá utilizar um Selector.

Exemplo:

```python
membros = MembroSelector.listar_ativos(
    igreja
)
```

Caso exista qualquer regra de negócio associada, a consulta deverá ser iniciada por um Service.

---

# 13. Boas Práticas

As Views deverão:

- possuir responsabilidade única;
- conter poucas linhas de código;
- ser altamente legíveis;
- delegar responsabilidades;
- utilizar Services para escrita;
- utilizar Selectors para leitura;
- evitar duplicação de código.

Uma View simples é mais fácil de testar e manter.

---

# 14. Documentos Relacionados

- GBE-04 — Models
- GBE-05 — Services
- GBE-06 — Selectors
- GBE-07 — Managers
- GBE-09 — Forms
- GAF — Framework de Autenticação

---

# 15. Princípios Finais

As Views representam a porta de entrada da aplicação.

Seu papel é coordenar o fluxo da requisição, mantendo-se livres de regras de negócio e concentrando-se apenas na interação entre o usuário e as camadas internas da plataforma.

Uma arquitetura com Views enxutas favorece reutilização, testes automatizados e evolução contínua da aplicação.

---

# 16. Generic Class-Based Views

O GereIgreja utilizará preferencialmente as Generic Class-Based Views (GCBVs) fornecidas pelo Django.

As principais Views recomendadas são:

- ListView;
- DetailView;
- CreateView;
- UpdateView;
- DeleteView;
- TemplateView;
- RedirectView.

Sempre que possível, utilizar essas classes como base para reduzir código repetitivo.

---

# 17. ListView

As ListViews deverão ser utilizadas para listagens.

Exemplo:

```python
class MembroListView(ListView):

    model = Membro

    template_name = "membros/lista.html"

    paginate_by = 25

    def get_queryset(self):
        return MembroSelector.listar_ativos(
            self.request.igreja
        )
```

Toda consulta deverá ser realizada através de Selectors.

---

# 18. DetailView

Responsável por exibir detalhes de um único registro.

Exemplo:

```python
class MembroDetailView(DetailView):

    model = Membro

    template_name = "membros/detalhe.html"
```

Caso seja necessário um carregamento mais elaborado, utilizar um Selector.

---

# 19. CreateView

CreateViews deverão delegar a gravação ao Service.

Exemplo:

```python
class MembroCreateView(CreateView):

    form_class = MembroForm

    template_name = "membros/form.html"

    def form_valid(self, form):

        MembroService.criar(
            igreja=self.request.igreja,
            dados=form.cleaned_data,
            usuario=self.request.user
        )

        return redirect("membros:lista")
```

A View não deverá chamar `form.save()` diretamente quando houver regras de negócio.

---

# 20. UpdateView

Atualizações seguem o mesmo princípio.

```python
MembroService.atualizar(
    membro,
    form.cleaned_data
)
```

Toda alteração deverá passar pelo Service.

---

# 21. DeleteView

Exclusões deverão utilizar Services.

Exemplo:

```python
MembroService.excluir(
    membro,
    usuario=request.user
)
```

Isso garante:

- auditoria;
- validações;
- regras de negócio;
- Soft Delete (quando aplicável).

---

# 22. Mixins

O GereIgreja incentivará o uso de Mixins para reutilização de comportamento.

Exemplos:

```text
LoginRequiredMixin

PermissionRequiredMixin

SuccessMessageMixin

TenantMixin

AuditMixin

BreadcrumbMixin
```

Cada Mixin deverá possuir responsabilidade única.

---

# 23. Permissões

As Views deverão validar permissões antes de executar qualquer operação.

Exemplo:

```python
class MembroUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView
):
```

A autorização deverá utilizar o framework GAF.

Nunca confiar apenas na interface.

---

# 24. Paginação

Toda listagem potencialmente grande deverá utilizar paginação.

Exemplo:

```python
paginate_by = 25
```

A quantidade poderá variar conforme o módulo.

Nunca carregar milhares de registros em uma única página.

---

# 25. Mensagens ao Usuário

Utilizar o framework oficial de mensagens do Django.

Exemplo:

```python
messages.success(
    request,
    "Membro cadastrado com sucesso."
)
```

Mensagens deverão ser:

- claras;
- objetivas;
- amigáveis.

---

# 26. Tratamento de Exceções

As Views deverão capturar apenas exceções esperadas.

Exemplo:

```python
try:

    ...

except ValidationError:

    ...

except PermissionDenied:

    ...
```

Exceções inesperadas deverão ser tratadas pelo middleware global.

---

# 27. Redirecionamentos

Após operações de escrita, utilizar redirecionamentos explícitos.

Exemplo:

```python
return redirect("membros:lista")
```

Evitar URLs fixas.

Preferir sempre nomes de rotas.

---

# 28. Contexto (Context)

Adicionar ao contexto apenas informações necessárias.

Exemplo:

```python
context["estatisticas"] = DashboardSelector.indicadores_rapidos(
    self.request.igreja
)
```

Evitar consultas desnecessárias.

---

# 29. Logging

As Views normalmente não deverão registrar logs técnicos.

Quando necessário, o registro deverá ocorrer no Service correspondente.

Isso mantém a responsabilidade da View limitada ao fluxo HTTP.

---

# 30. Auditoria

As Views nunca deverão gravar auditorias diretamente.

Toda auditoria deverá ocorrer dentro dos Services.

Assim garantimos que operações realizadas por APIs, comandos ou tarefas assíncronas também sejam auditadas.

---

# 31. Exemplo Completo de uma View

Abaixo um exemplo seguindo o padrão oficial do GereIgreja.

```python
class MembroCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SuccessMessageMixin,
    CreateView
):

    form_class = MembroForm

    template_name = "membros/form.html"

    permission_required = "membros.add_membro"

    success_message = "Membro cadastrado com sucesso."

    def form_valid(self, form):

        MembroService.criar(
            igreja=self.request.igreja,
            dados=form.cleaned_data,
            usuario=self.request.user
        )

        return redirect("membros:lista")
```

Observe que toda regra de negócio permanece no Service.

---

# 32. Organização por Domínio

Quando um módulo crescer, as Views deverão ser separadas por domínio.

Exemplo:

```text
views/

__init__.py

dashboard.py

membros.py

familias.py

ministerios.py

eventos.py

financeiro.py

tesouraria.py

usuarios.py

configuracoes.py
```

Cada arquivo deverá conter apenas Views relacionadas ao mesmo domínio.

---

# 33. Organização das URLs

Cada App deverá possuir seu próprio arquivo `urls.py`.

Exemplo:

```text
membros/

urls.py

views/

forms/

services/
```

As URLs deverão ser organizadas por módulo e registradas posteriormente nas URLs principais da plataforma.

---

# 34. Nomenclatura

Utilizar nomes padronizados.

Exemplo:

```python
MembroListView

MembroDetailView

MembroCreateView

MembroUpdateView

MembroDeleteView
```

Evitar abreviações.

Os nomes deverão refletir claramente a responsabilidade da View.

---

# 35. Integração com Templates

Cada View deverá possuir um Template específico.

Exemplo:

```text
templates/

membros/

lista.html

detalhe.html

form.html

confirmar_exclusao.html
```

Evitar reutilizações que prejudiquem a clareza do código.

---

# 36. Reutilização

Sempre que possível reutilizar:

- Mixins;
- Forms;
- Selectors;
- Services;
- Componentes do GDS (GereIgreja Design System).

A reutilização reduz duplicação e facilita manutenção.

---

# 37. Anti-patterns

Evitar:

- Views com centenas de linhas;
- consultas SQL na View;
- chamadas diretas ao ORM para escrita;
- regras de negócio;
- cálculos financeiros;
- importações complexas;
- geração de PDFs;
- envio de e-mails;
- chamadas HTTP para APIs externas;
- duplicação de lógica.

Essas responsabilidades pertencem às camadas especializadas.

---

# 38. Refatoração

Sempre que uma View crescer excessivamente:

- mover regras para Services;
- mover consultas para Selectors;
- criar Mixins reutilizáveis;
- dividir Views por domínio;
- revisar responsabilidades.

A View deverá permanecer enxuta.

---

# 39. Checklist para Criação

Antes de implementar uma View verificar:

- responsabilidade única;
- autenticação configurada;
- permissões aplicadas;
- Form ou Serializer adequado;
- Service utilizado para escrita;
- Selector utilizado para leitura;
- Template definido;
- URL registrada;
- testes previstos.

---

# 40. Checklist para Revisão

Durante uma revisão arquitetural verificar:

- ausência de regras de negócio;
- ausência de consultas complexas;
- ausência de acesso direto ao banco para escrita;
- uso correto de Services;
- uso correto de Selectors;
- código legível;
- métodos curtos;
- documentação atualizada.

---

# 41. Integração com o Ecossistema GBE

As Views fazem parte do fluxo oficial da Engenharia do Backend.

```text
Request

↓

URL

↓

View

↓

Form / Serializer

↓

Service

↓

Selector

↓

Manager

↓

Model

↓

Banco de Dados

↓

Response
```

Cada camada possui uma responsabilidade única e bem definida.

---

# 42. Evolução Contínua

As Views deverão evoluir acompanhando as necessidades da plataforma.

Novas funcionalidades deverão priorizar:

- reutilização;
- baixo acoplamento;
- simplicidade;
- clareza;
- aderência aos padrões definidos pelo GEA.

Mudanças estruturais deverão preservar a organização da arquitetura.

---

# 43. Documentos Relacionados

- GEA-02 — Arquitetura da Plataforma
- GEA-03 — Arquitetura dos Módulos
- GBE-04 — Models
- GBE-05 — Services
- GBE-06 — Selectors
- GBE-07 — Managers
- GBE-09 — Forms
- GAF — Framework de Autenticação
- GQF — Framework de Qualidade

---

# 44. Princípios Finais

As Views representam a interface entre o usuário e a lógica interna da plataforma.

Seu papel é coordenar o fluxo da requisição, delegando responsabilidades às camadas especializadas.

Ao manter as Views pequenas, legíveis e focadas na orquestração do fluxo HTTP, o GereIgreja garante uma arquitetura mais organizada, testável e preparada para evoluir.

Cada nova View deverá respeitar os princípios definidos neste documento, contribuindo para a consistência e a longevidade da plataforma.

---

## ✅ Status

**Pasta:** `docs/backend/`

**Arquivo:** `08-Views.md`

**Status:** **CONCLUÍDO (v1.0)**

Este documento passa a ser a referência oficial para implementação de todas as Views do GereIgreja.

