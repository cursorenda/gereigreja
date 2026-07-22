Pasta:
docs/backend/

Arquivo:
09-Forms.md

Documento:
GBE-09

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

# 09 - Forms

> "Um formulário deve coletar dados. A inteligência para processá-los pertence aos Services."

---

# Sumário

1. Objetivo
2. Filosofia dos Forms
3. Papel dos Forms na Arquitetura
4. Responsabilidades
5. O que NÃO pertence aos Forms
6. Estrutura Oficial
7. Organização dos Forms
8. Form vs ModelForm
9. Comunicação com Views
10. Comunicação com Services
11. Comunicação com Models
12. Comunicação com Templates
13. Boas Práticas
14. Documentos Relacionados
15. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para criação e utilização de Forms no GereIgreja.

Seu objetivo é garantir formulários consistentes, reutilizáveis, seguros e totalmente integrados à arquitetura oficial da plataforma.

Os Forms deverão ser responsáveis apenas pela entrada e validação estrutural dos dados.

---

# 2. Filosofia dos Forms

Os Forms representam a camada responsável por receber informações fornecidas pelo usuário.

Eles não executam regras de negócio.

Eles não realizam integrações.

Eles não modificam diretamente o domínio da aplicação.

No GereIgreja seguimos o seguinte princípio:

> **Forms validam dados. Services executam operações.**

Essa separação reduz acoplamento e facilita testes.

---

# 3. Papel dos Forms na Arquitetura

Fluxo oficial:

```text
Usuário

↓

Template

↓

Form

↓

View

↓

Service

↓

Selector

↓

Model

↓

Banco de Dados
```

O Form atua como intermediário entre a interface e a camada de serviços.

---

# 4. Responsabilidades

Os Forms poderão ser responsáveis por:

- receber dados do usuário;
- validar tipos;
- validar formatos;
- validar obrigatoriedade;
- normalizar entradas;
- converter tipos;
- apresentar mensagens de erro;
- disponibilizar dados limpos através de `cleaned_data`.

---

# 5. O que NÃO pertence aos Forms

Os Forms não deverão conter:

- regras de negócio;
- gravação direta em Models;
- cálculos financeiros;
- envio de e-mails;
- integrações externas;
- auditoria;
- geração de arquivos;
- consultas complexas;
- controle de permissões.

Essas responsabilidades pertencem às camadas apropriadas.

---

# 6. Estrutura Oficial

Cada App deverá possuir seu próprio diretório de Forms.

Exemplo:

```text
forms/

__init__.py

membro_form.py

familia_form.py

evento_form.py

financeiro_form.py

filtros.py

importacao.py
```

Cada arquivo deverá representar um domínio específico.

---

# 7. Organização dos Forms

Separar os formulários por finalidade.

Exemplo:

```text
forms/

cadastro/

filtros/

importacao/

relatorios/

configuracoes/
```

Essa organização facilita manutenção à medida que o sistema cresce.

---

# 8. Form vs ModelForm

Preferencialmente utilizar:

### Form

Quando:

- não houver Model correspondente;
- houver múltiplos Models envolvidos;
- tratar filtros;
- login;
- autenticação;
- pesquisas;
- importações.

---

### ModelForm

Utilizar quando representar diretamente um único Model.

Mesmo utilizando ModelForm, a gravação deverá ocorrer preferencialmente através dos Services quando existirem regras de negócio.

---

# 9. Comunicação com Views

As Views deverão instanciar e validar os Forms.

Exemplo:

```python
form = MembroForm(request.POST)

if form.is_valid():

    MembroService.criar(
        igreja=request.igreja,
        dados=form.cleaned_data,
        usuario=request.user
    )
```

A View coordena.

O Form valida.

O Service executa.

---

# 10. Comunicação com Services

Os Services deverão receber apenas dados já validados.

Exemplo:

```python
MembroService.criar(
    dados=form.cleaned_data
)
```

Isso reduz duplicação de validações.

---

# 11. Comunicação com Models

Forms não deverão alterar Models diretamente quando houver lógica de negócio.

Evitar:

```python
form.save()
```

Preferir:

```python
MembroService.criar(
    dados=form.cleaned_data
)
```

Essa abordagem centraliza a lógica da aplicação.

---

# 12. Comunicação com Templates

Os Templates deverão utilizar os Forms para renderização dos campos.

A apresentação visual deverá seguir o GereIgreja Design System (GDS).

Os Templates não deverão conter lógica de validação.

---

# 13. Boas Práticas

Os Forms deverão:

- possuir responsabilidade única;
- ser reutilizáveis;
- possuir nomes descritivos;
- apresentar mensagens claras;
- validar apenas estrutura dos dados;
- utilizar widgets padronizados.

---

# 14. Documentos Relacionados

- GBE-08 — Views
- GBE-10 — Validators
- GBE-05 — Services
- GDS — GereIgreja Design System
- GQF — Framework de Qualidade

---

# 15. Princípios Finais

Os Forms representam a camada oficial de entrada de dados do GereIgreja.

Sua missão é garantir que informações recebidas estejam corretamente estruturadas antes de serem processadas pelos Services.

Ao limitar suas responsabilidades à validação estrutural e apresentação de erros, preservamos uma arquitetura limpa, reutilizável e preparada para crescer.

---

# 16. Widgets

Todos os Forms deverão utilizar Widgets padronizados.

Os Widgets são responsáveis apenas pela apresentação do campo.

Exemplo:

```python
nome = forms.CharField(
    widget=forms.TextInput(
        attrs={
            "class": "form-control",
            "placeholder": "Nome completo"
        }
    )
)
```

Sempre que possível utilizar componentes oficiais do GereIgreja Design System (GDS).

---

# 17. Personalização Visual

A aparência dos formulários deverá seguir integralmente o GDS.

Os formulários deverão manter:

- espaçamento consistente;
- tipografia padronizada;
- ícones oficiais;
- mensagens uniformes;
- cores padronizadas;
- responsividade.

A lógica nunca deverá depender do CSS.

---

# 18. Método clean()

O método `clean()` deverá ser utilizado apenas para validações que envolvam múltiplos campos.

Exemplo:

```python
def clean(self):

    cleaned_data = super().clean()

    data_inicio = cleaned_data.get("data_inicio")
    data_fim = cleaned_data.get("data_fim")

    if data_inicio and data_fim:

        if data_inicio > data_fim:
            raise ValidationError(
                "A data inicial deve ser anterior à data final."
            )

    return cleaned_data
```

Sempre que possível, manter essas validações simples.

---

# 19. clean_<campo>()

Validações específicas deverão utilizar métodos dedicados.

Exemplo:

```python
def clean_cpf(self):

    cpf = self.cleaned_data["cpf"]

    if not validar_cpf(cpf):
        raise ValidationError(
            "CPF inválido."
        )

    return cpf
```

Cada método deverá validar apenas um campo.

---

# 20. Formsets

Quando houver necessidade de editar múltiplos registros simultaneamente, utilizar Formsets.

Exemplos:

- múltiplos telefones;
- dependentes;
- documentos;
- ministérios;
- escalas.

Evitar criar múltiplos Forms independentes.

---

# 21. Inline Formsets

Quando houver relacionamento pai-filho, utilizar Inline Formsets.

Exemplo:

```text
Família

↓

Integrantes
```

ou

```text
Evento

↓

Participantes
```

Essa abordagem simplifica a manutenção dos relacionamentos.

---

# 22. Formulários de Filtros

Filtros deverão utilizar Forms específicos.

Exemplo:

```text
forms/

filtros.py
```

Exemplos de filtros:

- nome;
- congregação;
- cargo;
- situação;
- período;
- cidade.

Filtros nunca deverão alterar dados.

---

# 23. Formulários de Pesquisa

Pesquisas deverão possuir Forms próprios.

Exemplo:

```python
PesquisaMembroForm

PesquisaEventoForm

PesquisaFinanceiroForm
```

Separar pesquisa de cadastro melhora a organização.

---

# 24. Formulários de Importação

Toda importação deverá possuir um Form específico.

Exemplos:

- Excel;
- CSV;
- XML;
- JSON.

O Form apenas valida o arquivo.

O processamento pertence ao Service.

---

# 25. Formulários de Exportação

Quando houver parâmetros para exportação, utilizar Forms.

Exemplo:

- período;
- formato;
- congregação;
- categorias.

A geração do arquivo deverá ocorrer nos Services.

---

# 26. Formulários em Etapas (Wizard)

Cadastros longos poderão utilizar múltiplas etapas.

Exemplo:

```text
Etapa 1

↓

Dados pessoais

↓

Etapa 2

↓

Contato

↓

Etapa 3

↓

Família

↓

Etapa 4

↓

Informações ministeriais
```

Cada etapa deverá possuir validação independente.

---

# 27. Campos Dinâmicos

Campos poderão ser adicionados dinamicamente quando necessário.

Exemplo:

```python
def __init__(self, *args, usuario=None, **kwargs):

    super().__init__(*args, **kwargs)

    if usuario.is_superuser:

        self.fields["administrador"] = forms.BooleanField(
            required=False
        )
```

Evitar excesso de comportamento dinâmico.

---

# 28. Campos Ocultos

Campos HiddenInput deverão ser utilizados apenas quando realmente necessários.

Exemplo:

```python
forms.HiddenInput()
```

Nunca confiar em valores ocultos para decisões de segurança.

Toda validação deverá ocorrer no backend.

---

# 29. Upload de Arquivos

Uploads deverão utilizar validações específicas.

Verificar:

- extensão;
- tipo MIME;
- tamanho máximo;
- quantidade de arquivos;
- permissões.

Arquivos enviados nunca deverão ser considerados confiáveis.

---

# 30. Mensagens de Erro

Mensagens deverão ser:

- objetivas;
- amigáveis;
- claras;
- consistentes.

Exemplo:

✔ "Informe um CPF válido."

Evitar:

✘ "ValidationError: invalid CPF format."

As mensagens são parte da experiência do usuário.

---

# 31. BaseForm do GereIgreja

Todos os formulários da plataforma deverão herdar de uma classe base quando compartilharem comportamentos comuns.

Exemplo:

```python
class BaseForm(forms.Form):

    """
    Classe base para os formulários do GereIgreja.
    """

    def adicionar_classes_padrao(self):
        ...
```

A BaseForm poderá centralizar:

- classes CSS;
- placeholders;
- atributos HTML;
- estilos do GDS;
- comportamentos comuns;
- internacionalização;
- acessibilidade.

Essa abordagem reduz duplicação e aumenta a consistência.

---

# 32. Reutilização

Sempre que possível reutilizar:

- campos;
- widgets;
- validadores;
- mixins;
- BaseForms;
- componentes do GDS.

Evitar copiar código entre formulários.

Caso um trecho seja reutilizado em três ou mais Forms, considerar sua extração para um componente compartilhado.

---

# 33. Integração com o GDS

Todos os Forms deverão utilizar o GereIgreja Design System.

Itens obrigatórios:

- tipografia oficial;
- espaçamentos;
- botões padronizados;
- cores oficiais;
- componentes reutilizáveis;
- mensagens padronizadas;
- ícones oficiais.

O usuário deverá perceber a mesma identidade visual em toda a plataforma.

---

# 34. Acessibilidade

Os formulários deverão seguir as recomendações da WCAG.

Boas práticas:

- labels associadas aos campos;
- mensagens claras;
- contraste adequado;
- navegação por teclado;
- foco visível;
- indicação de campos obrigatórios;
- descrição de erros.

A acessibilidade faz parte da arquitetura da plataforma.

---

# 35. Experiência do Usuário (UX)

Os formulários deverão priorizar simplicidade.

Boas práticas:

- poucos campos por tela;
- agrupamento lógico;
- ordem natural de preenchimento;
- feedback imediato;
- mensagens compreensíveis;
- botões claramente identificados.

Evitar formulários excessivamente longos quando puderem ser divididos em etapas.

---

# 36. Formulários Reutilizáveis

Quando diferentes módulos compartilharem os mesmos campos, criar formulários reutilizáveis.

Exemplo:

```text
forms/

base/

endereco.py

contato.py

documentos.py
```

Esses formulários poderão ser herdados ou compostos por outros.

---

# 37. Internacionalização

Os textos apresentados pelos Forms deverão ser preparados para internacionalização (i18n).

Exemplo:

```python
from django.utils.translation import gettext_lazy as _

nome = forms.CharField(
    label=_("Nome")
)
```

Mesmo que inicialmente a plataforma seja utilizada em português, essa prática prepara o sistema para futuras expansões.

---

# 38. Anti-patterns

Evitar:

- regras de negócio dentro do Form;
- consultas complexas ao banco;
- chamadas HTTP;
- envio de e-mails;
- gravação direta em múltiplos Models;
- processamento financeiro;
- lógica duplicada;
- formulários com centenas de linhas.

Sempre que um Form crescer excessivamente, reavaliar sua responsabilidade.

---

# 39. Refatoração

Quando um Form crescer:

- extrair Widgets;
- extrair Validadores;
- criar BaseForms;
- dividir por domínio;
- reutilizar componentes;
- revisar responsabilidades.

A evolução contínua faz parte da arquitetura.

---

# 40. Checklist para Criação

Antes de criar um Form verificar:

- possui responsabilidade única;
- nome claro;
- valida apenas estrutura;
- utiliza Widgets padronizados;
- utiliza mensagens consistentes;
- segue o GDS;
- utiliza BaseForm quando apropriado;
- preparado para reutilização.

---

# 41. Checklist para Revisão

Durante uma revisão arquitetural verificar:

- ausência de regras de negócio;
- ausência de gravação direta em Models;
- validações bem distribuídas;
- Widgets padronizados;
- acessibilidade adequada;
- documentação atualizada;
- código legível;
- reutilização de componentes.

---

# 42. Estrutura Recomendada

Para Apps grandes, recomenda-se:

```text
forms/

__init__.py

base/

cadastro/

edicao/

filtros/

pesquisa/

importacao/

exportacao/

configuracoes/

validators.py

widgets.py

mixins.py
```

Essa organização facilita manutenção e escalabilidade.

---

# 43. Integração com o Ecossistema GBE

Os Forms participam do fluxo oficial da arquitetura.

```text
Usuário

↓

Template

↓

Form

↓

View

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
```

Cada camada possui responsabilidades independentes e complementares.

---

# 44. Documentos Relacionados

- GEA-02 — Arquitetura da Plataforma
- GBE-05 — Services
- GBE-08 — Views
- GBE-10 — Validators
- GDS — GereIgreja Design System
- GQF — Framework de Qualidade

---

# 45. Princípios Finais

Os Forms representam a camada oficial de entrada de dados da plataforma.

Sua missão é validar a estrutura das informações recebidas, orientar o usuário durante o preenchimento e entregar dados consistentes para os Services.

Ao limitar suas responsabilidades e integrá-los ao GereIgreja Design System, garantimos uma experiência uniforme, acessível e preparada para crescer junto com a plataforma.

Todo novo formulário desenvolvido para o GereIgreja deverá seguir os princípios definidos neste documento, preservando a qualidade da arquitetura e a consistência da experiência do usuário.

---

## ✅ Status

**Pasta:** `docs/backend/`

**Arquivo:** `09-Forms.md`

**Status:** **CONCLUÍDO (v1.0)**

Este documento passa a ser a referência oficial para a criação e manutenção de todos os formulários do GereIgreja.


