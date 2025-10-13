# ⚡ Quick Start - GitHub Actions Pipeline

## 🚀 Activar en 3 Pasos

### Paso 1: Commit
```bash
cd /Users/lucasblandon/PROYECTOFINAL/codigoV5/apiMS
git add .github/workflows/unit-tests.yml
git commit -m "ci: Add unit tests pipeline"
```

### Paso 2: Push
```bash
git push origin main
```

### Paso 3: Ver Resultado
Abre: **https://github.com/TU-USUARIO/TU-REPO/actions**

¡Eso es todo! ✅

## 📊 Qué Pasará

```
00:00  Push a GitHub
00:05  Pipeline iniciado automáticamente
00:10  Python 3.11 y 3.12 configurados en paralelo
00:20  Dependencias instaladas
01:00  Tests de Auth Service ejecutándose
       ✅ 20 tests Value Objects
       ✅ 13 tests Entities
01:30  Tests de Product Service ejecutándose
       ✅ 21 tests Value Objects
       ✅ 13 tests Entities
02:30  Reportes de cobertura generados
03:00  Artefactos subidos
03:30  ✅ Pipeline completado!

Total: ~3-4 minutos ⚡
```

## ✅ Resultado Esperado

```
🧪 Tests Unitarios

✅ Ejecutar Tests Unitarios (py3.11)    3m 25s
✅ Ejecutar Tests Unitarios (py3.12)    3m 22s

67/67 tests pasados ✅
Cobertura: >95% en dominio
```

## 📦 Artefactos

Descargables desde GitHub Actions:
- **coverage-report** - Reporte HTML interactivo

## 🎨 Badge

Agrega a tu README:

```markdown
![Tests](https://github.com/USUARIO/REPO/actions/workflows/unit-tests.yml/badge.svg)
```

## 🔍 Verificar Localmente Antes

```bash
cd microservices
pytest auth-service/tests/unit/ -v
pytest product-service/tests/unit/ -v
```

Si pasa localmente, pasará en GitHub Actions ✅

---

**Workflow:** 1 (unit-tests.yml)  
**Tests:** 67  
**Duración:** ~3-4 min  

¡Listo para activar! 🚀
