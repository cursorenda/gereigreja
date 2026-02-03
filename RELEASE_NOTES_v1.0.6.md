# 🎉 Gereigreja v1.0.6 — Atualização de 17/01/2026

Olá! Esta versão traz uma melhoria simples, mas muito útil para você acompanhar as atualizações do sistema.

---

## 🆕 O que há de novo?

### ℹ️ Informação de Versão Sempre Visível

**Veja a versão do sistema a qualquer momento** 🏷️  
Agora o número da versão e a data da última atualização aparecem automaticamente no rodapé de todas as páginas. Você sempre saberá qual versão está usando!

**Informação também no painel administrativo** 🔧  
Administradores podem ver a versão atual diretamente no painel admin, facilitando o suporte e a identificação de problemas.

**Mensagem amigável e clara** 💬  
As informações são exibidas de forma elegante e discreta, sem poluir a interface.

**Sistema inteligente** ⚡  
O sistema lê automaticamente o arquivo de changelog e usa cache para melhor performance, atualizando a informação sempre que uma nova versão é instalada.

---

## 💡 Por que isso importa?

- **Transparência**: Você sabe exatamente qual versão está rodando
- **Suporte mais rápido**: Ao relatar problemas, basta informar a versão que aparece no rodapé
- **Controle**: Acompanhe facilmente quando foram feitas atualizações
- **Profissionalismo**: Uma interface mais completa e informativa

---

## 📋 Detalhes Técnicos

Para administradores e desenvolvedores:
- Leitura automática do `CHANGELOG.md` via context processor
- Sistema de cache para otimizar performance
- Exibição no rodapé de todas as páginas (base template)
- Exibição no painel administrativo do Django
- Formatação amigável da data (ex: "17/01/2026")
- Fallback para mensagem padrão caso o changelog não seja encontrado

---

## ❓ Precisa de ajuda?

Se tiver dúvidas ou encontrar algum problema, entre em contato com o suporte técnico.

---

**Equipe Gereigreja** 💙  
*Simplificando a gestão da sua igreja*
