# GitHub Actions - CI/CD Pipeline

## 🚀 Workflows Configurados

Este proyecto incluye **5 workflows** completos de GitHub Actions:

### 1️⃣ tests.yml - Tests Unitarios
![Tests](https://github.com/USUARIO/REPO/actions/workflows/tests.yml/badge.svg)

- **Trigger:** Push, PR, Manual
- **Duración:** ~3-5 minutos
- **Jobs:** 4 (Auth, Product, Summary, Quality)
- **Matrix:** Python 3.11, 3.12

### 2️⃣ ci-cd.yml - Pipeline CI/CD Completo
![CI/CD](https://github.com/USUARIO/REPO/actions/workflows/ci-cd.yml/badge.svg)

- **Trigger:** Push a main, PR a main, Releases
- **Duración:** ~5-8 minutos
- **Jobs:** 5 (Tests, Architecture, Quality, Build, Summary)
- **Docker:** Build y Push automático

### 3️⃣ pr-tests.yml - Validación de PRs
![PR Tests](https://github.com/USUARIO/REPO/actions/workflows/pr-tests.yml/badge.svg)

- **Trigger:** Apertura/Actualización de PR
- **Duración:** ~2-3 minutos
- **Jobs:** 2 (Validation, Summary)
- **Feature:** Comenta automáticamente en PR

### 4️⃣ nightly-tests.yml - Tests Nocturnos
![Nightly](https://github.com/USUARIO/REPO/actions/workflows/nightly-tests.yml/badge.svg)

- **Trigger:** Diario 2:00 AM UTC, Manual
- **Duración:** ~10-15 minutos
- **Jobs:** 1 (Comprehensive)
- **Matrix:** Python 3.10, 3.11, 3.12

### 5️⃣ badges.yml - Actualización de Badges
- **Trigger:** Push a main, After tests workflow
- **Duración:** ~1-2 minutos
- **Jobs:** 1 (Update)

## 📊 Flujo de Ejecución

```
Push/PR → tests.yml (Tests rápidos)
   ↓
   ✅ Pasa → ci-cd.yml (Build & Deploy)
   ↓
   ✅ Main → Build Docker Images
   ↓
   ✅ Push to Registry
```

## 🎯 Características

✅ **Automatización completa** - Sin intervención manual  
✅ **Multi-versión Python** - 3.10, 3.11, 3.12  
✅ **Cobertura de código** - Reportes automáticos  
✅ **Docker builds** - Imágenes listas para deploy  
✅ **Validación de arquitectura** - Estructura verificada  
✅ **Análisis de calidad** - Black, flake8, isort  
✅ **Análisis de seguridad** - Bandit  
✅ **Comentarios en PR** - Feedback automático  
✅ **Artefactos** - Reportes descargables  

## 📁 Archivos Creados

```
.github/
├── workflows/
│   ├── tests.yml              ✅ Tests principales
│   ├── ci-cd.yml             ✅ Pipeline completo
│   ├── pr-tests.yml          ✅ Validación de PRs
│   ├── nightly-tests.yml     ✅ Tests nocturnos
│   └── badges.yml            ✅ Actualización de badges
├── GITHUB_ACTIONS_GUIDE.md   ✅ Guía detallada
└── README.md                 ✅ Este archivo
```

## 🚀 Activación

### Para activar los workflows:

```bash
# 1. Commit de los workflows
git add .github/
git commit -m "ci: Add GitHub Actions workflows"

# 2. Push a GitHub
git push origin main

# 3. Ve a GitHub Actions
# https://github.com/TU-USUARIO/TU-REPO/actions
```

## 📈 Métricas

| Workflow | Duración | Frecuencia | Jobs |
|----------|----------|------------|------|
| tests.yml | 3-5 min | Por push/PR | 4 |
| ci-cd.yml | 5-8 min | Push a main | 5 |
| pr-tests.yml | 2-3 min | Por PR | 2 |
| nightly-tests.yml | 10-15 min | Diario | 1 |
| badges.yml | 1-2 min | Push a main | 1 |

## 🎓 Recursos

- **Guía Completa:** [GITHUB_ACTIONS_GUIDE.md](GITHUB_ACTIONS_GUIDE.md)
- **Tests Documentation:** [../microservices/TESTING.md](../microservices/TESTING.md)
- **GitHub Actions Docs:** https://docs.github.com/actions

---

**Estado:** ✅ CONFIGURADO Y LISTO  
**Workflows:** 5  
**Última actualización:** 2025-01-10  

¡Happy CI/CD! 🚀

