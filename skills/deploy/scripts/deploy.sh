#!/bin/bash
# Script de deploy automatizado
# Uso: ./deploy.sh [versao]

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Iniciando processo de deploy...${NC}"

# 1. Verificar branch
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ]; then
    echo -e "${RED}❌ Erro: Você deve estar na branch 'main' para fazer deploy!${NC}"
    echo "Branch atual: $BRANCH"
    exit 1
fi

# 2. Verificar mudanças não commitadas
if [[ -n $(git status -s) ]]; then
    echo -e "${RED}❌ Erro: Existem mudanças não commitadas!${NC}"
    git status -s
    exit 1
fi

# 3. Pull para garantir atualização
echo "📥 Sincronizando com repositório remoto..."
git pull origin main

# 4. Criar backup antes do deploy
echo "💾 Criando backup de segurança..."
cd ../backup/scripts
./backup.sh || python backup.py
cd -

# 5. Executar testes (se houver)
echo "🧪 Executando testes..."
python manage.py test --settings=core.settings_test || {
    echo -e "${RED}❌ Testes falharam! Deploy cancelado.${NC}"
    exit 1
}

# 6. Verificar migrações pendentes
echo "🔍 Verificando migrações..."
python manage.py makemigrations --dry-run --check || {
    echo -e "${RED}⚠️  Existem migrações pendentes!${NC}"
    echo "Execute: python manage.py makemigrations"
    exit 1
}

# 7. Atualizar CHANGELOG se versão foi passada
if [ -n "$1" ]; then
    VERSION=$1
    echo "📝 Atualizando CHANGELOG.md para versão $VERSION..."
    DATE=$(date +"%d/%m/%Y")
    
    # Adicionar nova versão no topo do CHANGELOG
    sed -i "1s/^/## v${VERSION} — ${DATE}\n\n### Mudanças\n- [Adicione as mudanças aqui]\n\n/" CHANGELOG.md
    
    git add CHANGELOG.md
    git commit -m "Release v${VERSION}"
fi

# 8. Tag da versão (se especificada)
if [ -n "$1" ]; then
    echo "🏷️  Criando tag v${VERSION}..."
    git tag -a "v${VERSION}" -m "Release v${VERSION}"
fi

# 9. Push para o repositório
echo "📤 Enviando para repositório..."
git push origin main --tags

# 10. Deploy automático no Render
echo -e "${GREEN}✅ Deploy iniciado!${NC}"
echo "🔄 O Render detectará o push e iniciará o deploy automaticamente."
echo "📊 Acompanhe em: https://dashboard.render.com"
echo ""
echo "⏳ Aguarde alguns minutos para o deploy completar..."
echo "✅ Build → Instalar dependências → Migrações → Collectstatic → Restart"

# 11. Verificar status (opcional - requer Render CLI)
if command -v render &> /dev/null; then
    echo ""
    echo "📡 Verificando status do serviço..."
    render services status
fi

echo ""
echo -e "${GREEN}🎉 Processo de deploy concluído!${NC}"
