#!/bin/bash

# 🧪 Script para probar el pipeline unit-tests.yml localmente
# Este script simula los pasos del workflow de GitHub Actions
# 
# ACTUALIZADO: Incluye todos los tests del Auth Service (domain, application, infrastructure, api)

set -e  # Salir si algún comando falla

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║            🧪 SIMULACIÓN PIPELINE UNIT-TESTS.YML             ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Configurar directorio de trabajo
cd apiMS/microservices
export PYTHONPATH=$(pwd)

echo "📁 Directorio de trabajo: $(pwd)"
echo "🐍 PYTHONPATH: $PYTHONPATH"
echo ""

# Paso 1: Verificar dependencias
echo "📦 PASO 1: Verificar dependencias"
echo "════════════════════════════════════════════════"
if [ -f "requirements.txt" ] && [ -f "requirements-test.txt" ]; then
    echo "✅ Archivos de dependencias encontrados"
    echo "   - requirements.txt"
    echo "   - requirements-test.txt"
else
    echo "❌ Error: Archivos de dependencias no encontrados"
    exit 1
fi
echo ""

# Paso 2: Auth Service Tests
echo "🔐 PASO 2: Auth Service - Tests Unitarios"
echo "════════════════════════════════════════════════"
echo "📋 Ejecutando todos los tests del Auth Service:"
echo "   - Domain (entities, value_objects, events, ports)"
echo "   - Application (commands, queries, handlers, services)"
echo "   - Infrastructure (adapters, repositories, database, email)"
echo "   - API (routes, dependencies)"
echo ""
if pytest auth-service/tests/unit/ -q; then
    echo "✅ Auth Service tests: Todos los tests pasaron"
else
    echo "❌ Auth Service tests: FALLARON"
    exit 1
fi
echo ""

# Paso 3: Product Service Tests  
echo "📦 PASO 3: Product Service - Tests Unitarios"
echo "════════════════════════════════════════════════"
if pytest product-service/tests/unit/ -q; then
    echo "✅ Product Service tests: 34 tests pasaron"
else
    echo "❌ Product Service tests: FALLARON"
    exit 1
fi
echo ""

# Paso 4: Reporte de cobertura (ejecutar por separado para evitar conflictos conftest)
echo "📊 PASO 4: Generar reporte de cobertura"
echo "════════════════════════════════════════════════"

# Generar cobertura para Auth Service
echo "🔐 Generando cobertura Auth Service..."
echo "📊 Analizando cobertura completa del Auth Service:"
echo "   - Domain layer (entities, value_objects, events, ports)"
echo "   - Application layer (commands, queries, handlers, services)"
echo "   - Infrastructure layer (adapters, repositories, database, email)"
echo "   - API layer (routes, dependencies)"
echo ""
if pytest auth-service/tests/unit/ \
    --cov=auth-service \
    --cov-report=xml \
    --cov-report=html \
    --cov-report=term-missing \
    -q; then
    echo "✅ Cobertura Auth Service generada"
else
    echo "❌ Error en cobertura Auth Service"
    exit 1
fi

# Generar cobertura para Product Service
echo "📦 Generando cobertura Product Service..."
if pytest product-service/tests/unit/ \
    --cov=product-service/domain \
    --cov-append \
    --cov-report=xml \
    --cov-report=html \
    --cov-report=term-missing \
    -q; then
    echo "✅ Cobertura Product Service generada"
    echo "✅ Reporte de cobertura combinado generado exitosamente"
    echo "   - coverage.xml"
    echo "   - htmlcov/ (HTML report)"
else
    echo "❌ Error en cobertura Product Service"
    exit 1
fi
echo ""

# Resumen final
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║            ✅ PIPELINE SIMULADO EXITOSAMENTE                ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Resultados:"
echo "✅ Auth Service - Tests completos (domain, application, infrastructure, api)"
echo "✅ Product Service - Value Objects: 21 tests"
echo "✅ Product Service - Entities: 13 tests"
echo ""
echo "Total: Tests unitarios completos del Auth Service + Product Service"
echo "🐍 Versión Python: $(python --version)"
echo ""
echo "🎉 ¡Pipeline listo para GitHub Actions!"