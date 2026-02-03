# 🎉 Gereigreja v1.0.7 — Atualização de 28/01/2026

Olá! Esta é uma versão muito especial, repleta de melhorias para facilitar o gerenciamento de pessoas e a Escola Bíblica Dominical.

---

## 🆕 O que há de novo?

### 👥 Gerenciamento de Cargos Totalmente Renovado

**Finalize vínculos sem perder o histórico** 📋  
Agora você pode encerrar a função de alguém em um cargo com o novo botão "Finalizar vínculo". Todo o histórico fica preservado para consulta futura — perfeito para relatórios e auditoria!

**Veja quem já ocupou cada cargo** 🕰️  
Na tela de cada cargo, você pode visualizar todos os ocupantes anteriores. Mantenha o controle completo da história da sua igreja.

**Filtros inteligentes** 🔍  
Ao atribuir cargos, o sistema mostra apenas membros e obreiros ativos, tornando a seleção muito mais rápida e prática.

### 📝 Cadastro de Membros Modernizado

**Interface padronizada e consistente** ✨  
Renovamos completamente os formulários de cadastro e edição de membros. Agora tudo segue o mesmo padrão visual, com comentários explicativos e ações dinâmicas.

**Nova aba de histórico de cargos** 📊  
Ao editar um membro, você tem acesso a uma aba exclusiva mostrando todos os cargos que ele já ocupou ou ocupa. Consulte facilmente toda a trajetória ministerial da pessoa.

### 📖 Escola Bíblica ainda mais completa

**Assistente para criar lições** 🧙‍♂️  
Novo wizard (assistente passo a passo) para gerar lições de forma rápida e organizada.

**Banner de período/trimestre** 🎨  
Identificação visual clara do período letivo atual no topo das páginas da EBD.

**Copie dados do período anterior** 🔄  
Economize tempo! Ao criar um novo período, você pode copiar automaticamente as configurações do período anterior.

### 🛠️ Ferramentas de Administração

**Scripts de auditoria e correção** 🔧  
Adicionamos scripts profissionais na pasta `/scripts` para:
- Auditar vínculos de cargos
- Corrigir inconsistências
- Criar membros automaticamente
- E muito mais!

### 📱 Design Responsivo Aprimorado

**Melhor visualização em celulares** 📲  
Ajustamos as telas de cargos para funcionar perfeitamente em dispositivos móveis, com largura máxima otimizada.

---

## 💡 Por que isso importa?

- **Gestão profissional**: Controle completo do histórico de cargos e ocupantes
- **Mais produtividade**: Crie lições e períodos da EBD com muito mais rapidez
- **Dados organizados**: Templates padronizados facilitam o uso e a manutenção
- **Mobilidade**: Use o sistema com conforto em qualquer dispositivo

---

## 📋 Detalhes Técnicos

Para administradores e desenvolvedores:
- Implementado sistema de histórico de ocupantes de cargos com soft delete
- Templates refatorados com partials reutilizáveis (`_pessoa_form_fields.html`)
- Wizard multi-etapa para geração de lições da EBD
- Scripts de manutenção em `/scripts/` (auditoria, correção, importação)
- Migrations aplicadas nos módulos: configuração, escola_biblica, secretaria
- Media queries otimizadas para responsividade em dispositivos móveis
- Deploy registrado em `backup_log.txt`

---

## ❓ Precisa de ajuda?

Se tiver dúvidas sobre as novas funcionalidades ou encontrar algum problema, entre em contato com o suporte técnico.

---

**Equipe Gereigreja** 💙  
*Simplificando a gestão da sua igreja*
