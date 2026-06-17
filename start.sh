#!/bin/bash

echo "🚀 Iniciando KIMI OS..."
echo "🤖 Sistema Operativo de IA Autónoma"
echo "🎯 Autonomía: 99%"
echo ""

# Verificar variables de entorno
if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ GROQ_API_KEY no configurada"
    exit 1
fi

echo "✅ Variables de entorno verificadas"
echo "🧠 Iniciando núcleo..."

# Iniciar aplicación
python dashboard/app.py