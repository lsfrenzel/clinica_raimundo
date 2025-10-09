#!/bin/bash
# Script para verificar o status do banco de dados no Railway

echo "🔍 Verificando configuração do Railway..."
echo ""

# Verificar se DATABASE_URL está configurado
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL não está configurado!"
    echo "Configure a variável DATABASE_URL no Railway apontando para seu PostgreSQL"
    exit 1
else
    echo "✅ DATABASE_URL configurado"
    # Mascarar senha na exibição
    echo "   ${DATABASE_URL%%:*}://***@***"
fi

echo ""
echo "🚀 Iniciando população do banco de dados..."
echo ""

# Executar script de população
python popular_railway.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Banco de dados populado com sucesso!"
    echo ""
    echo "🔑 Você pode fazer login com:"
    echo "   Email: admin@clinicadrraimundonunes.com.br"
    echo "   Senha: admin123"
else
    echo ""
    echo "❌ Erro ao popular banco de dados"
    echo "Verifique os logs acima para mais detalhes"
    exit 1
fi
