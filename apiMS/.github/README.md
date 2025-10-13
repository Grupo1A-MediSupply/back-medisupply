# 🧪 GitHub Actions - Pipeline de Tests Unitarios

## 📋 Pipeline Configurado

Este proyecto incluye **1 workflow simple** de GitHub Actions para ejecutar las pruebas unitarias automáticamente.

## 🎯 Workflow: unit-tests.yml

![Tests](https://github.com/USUARIO/REPO/actions/workflows/unit-tests.yml/badge.svg)

### ✅ Características

- **Trigger:** Push a cualquier rama, Pull Requests, Manual
- **Duración:** ~3-4 minutos
- **Python:** 3.11 y 3.12 (matrix builds)
- **Jobs:** 1 (con 2 versiones en paralelo)

### 🎯 Qué Hace

1. ✅ Ejecuta tests de **Auth Service**
   - Value Objects (20 tests)
   - Entities (13 tests)

2. ✅ Ejecuta tests de **Product Service**
   - Value Objects (21 tests)
   - Entities (13 tests)

3. ✅ Genera **reporte de cobertura**
   - Formato XML para Codecov
   - Formato HTML para descarga
   - Muestra en terminal

4. ✅ Sube reportes
   - Codecov (opcional)
   - Artefactos descargables

### 📊 Tests Ejecutados

```
Total: 67 tests unitarios
├── Auth Service: 33 tests
│   ├── Value Objects: 20 tests
│   └── Entities: 13 tests
└── Product Service: 34 tests
    ├── Value Objects: 21 tests
    └── Entities: 13 tests
```

## 🚀 Cómo Activar

### Paso 1: Commit el workflow
```bash
cd /Users/lucasblandon/PROYECTOFINAL/codigoV5/apiMS
git add .github/workflows/unit-tests.yml
git commit -m "ci: Add unit tests pipeline"
```

### Paso 2: Push a GitHub
```bash
git push origin main
```

### Paso 3: Ver en GitHub
Abre: **https://github.com/TU-USUARIO/TU-REPO/actions**

¡Eso es todo! El pipeline se ejecutará automáticamente. ✅

## 📈 Ejemplo de Ejecución

Cuando hagas push, verás:

```
🧪 Tests Unitarios

✅ Ejecutar Tests Unitarios (py3.11)    3m 25s
✅ Ejecutar Tests Unitarios (py3.12)    3m 22s

Total: ~3-4 minutos ⚡
```

**Detalles de cada ejecución:**
```
📥 Checkout código                     15s
🐍 Configurar Python 3.12              20s
📦 Instalar dependencias               45s
🧪 Tests - Auth Service                30s
🧪 Tests - Product Service             25s
📊 Generar cobertura                   20s
📤 Subir reportes                      15s
✅ Resumen                             5s

Total: ~3m 20s
```

## 📊 Reportes Generados

### Reporte de Cobertura

**Ubicación:** GitHub Actions → Workflow Run → Artifacts

**Formato:**
- `coverage-report` - HTML interactivo (30 días disponible)

**Ver reporte:**
1. Ve a Actions → Workflow ejecutado
2. Scroll down a "Artifacts"
3. Descarga `coverage-report`
4. Abre `index.html` en tu navegador

### Codecov (Opcional)

Si configuras `CODECOV_TOKEN`:
- Reportes automáticos en commits
- Badges de cobertura
- Comparación en PRs

## 🎨 Badge para README

Agrega este badge a tu README principal:

```markdown
![Tests](https://github.com/USUARIO/REPO/actions/workflows/unit-tests.yml/badge.svg)
```

Reemplaza `USUARIO/REPO` con tu usuario y repositorio.

## 🔧 Configuración

### Variables de Entorno

El pipeline usa:
- Python 3.11 y 3.12
- pytest con coverage
- Paths: `microservices/`

### Secrets Opcionales

En GitHub: **Settings → Secrets → Actions**

- `CODECOV_TOKEN` - Para subir a Codecov.io (opcional)

## 💡 Ejecución Manual

Puedes ejecutar el pipeline manualmente:

1. GitHub → Actions
2. Click en "🧪 Tests Unitarios"
3. Click en "Run workflow"
4. Selecciona la rama
5. Click en "Run workflow"

## 🐛 Solución de Problemas

### Si el pipeline falla:

1. **Revisa los logs:**
   - GitHub Actions → Click en el workflow fallido
   - Expande el step que falló

2. **Ejecuta localmente:**
   ```bash
   cd microservices
   pytest auth-service/tests/unit/ -v
   pytest product-service/tests/unit/ -v
   ```

3. **Verifica dependencias:**
   ```bash
   cd microservices
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

## ✅ Checklist

- [x] Workflow creado: `unit-tests.yml`
- [x] Matrix builds: Python 3.11, 3.12
- [x] Tests de Auth Service
- [x] Tests de Product Service
- [x] Reportes de cobertura
- [x] Artefactos configurados
- [x] Documentación incluida
- [ ] Git push para activar 🚀

## 📚 Documentación

- **README.md** - Este archivo (resumen)
- **QUICK_START.md** - Guía de 3 pasos
- [Testing Guide](../microservices/TESTING.md) - Guía completa de tests

## 🎯 Lo Que Se Ejecuta

```yaml
# En cada push o PR:
1. Setup Python (3.11 y 3.12 en paralelo)
2. Instalar dependencias
3. Ejecutar 67 tests unitarios
4. Generar reporte de cobertura
5. Subir artefactos
6. Mostrar resumen
```

## 🎉 Resultado

Tendrás:

✅ **Tests automáticos** en cada push  
✅ **Validación de PRs** antes de merge  
✅ **Reportes de cobertura** descargables  
✅ **Badge de estado** para README  
✅ **Multi-versión Python** (3.11, 3.12)  
✅ **Feedback rápido** (~3-4 minutos)  

---

**Workflow:** 1 (simplificado)  
**Tests ejecutados:** 67  
**Duración:** ~3-4 minutos  
**Estado:** ✅ LISTO  

Para activar: `git push` 🚀
