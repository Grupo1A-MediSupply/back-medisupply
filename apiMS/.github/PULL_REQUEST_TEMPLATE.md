## 📋 Descripción

<!-- Describe qué cambios introduces y por qué -->

## 🎯 Tipo de Cambio

<!-- Marca con [x] el tipo de cambio -->

- [ ] 🐛 Bug fix (corrección de error)
- [ ] ✨ Nueva funcionalidad
- [ ] 💥 Breaking change (cambio que rompe compatibilidad)
- [ ] 📝 Documentación
- [ ] 🎨 Refactorización
- [ ] ⚡ Mejora de rendimiento
- [ ] 🧪 Tests

## ✅ Checklist

<!-- Verifica que hayas completado todo -->

- [ ] Mi código sigue la **Arquitectura Hexagonal**
- [ ] He mantenido la separación de capas (Domain, Application, Infrastructure, API)
- [ ] He agregado **tests unitarios** para los cambios
- [ ] Todos los tests **pasan localmente** (`pytest -v`)
- [ ] He actualizado la **documentación** si es necesario
- [ ] Los **comandos y queries** están separados (CQRS)
- [ ] He registrado **eventos de dominio** donde corresponde
- [ ] El código sigue los **principios DDD**

## 🧪 Tests

<!-- Describe qué tests agregaste o modificaste -->

- [ ] Tests unitarios agregados/actualizados
- [ ] Tests de Value Objects
- [ ] Tests de Entidades
- [ ] Tests de Command Handlers
- [ ] Tests de Query Handlers

**Comando para ejecutar tests:**
```bash
cd microservices
pytest auth-service/tests/unit/ -v
pytest product-service/tests/unit/ -v
```

## 🏗️ Arquitectura

<!-- Verifica la arquitectura hexagonal -->

- [ ] Dominio **sin dependencias** externas
- [ ] Lógica de negocio **solo en el dominio**
- [ ] Puertos (interfaces) definidos en el dominio
- [ ] Adaptadores implementan puertos
- [ ] Value Objects son **inmutables**
- [ ] Entidades registran **eventos de dominio**

## 🔍 Capas Afectadas

<!-- Marca qué capas modificaste -->

- [ ] **Domain Layer** (entities, value_objects, events, ports)
- [ ] **Application Layer** (commands, queries, handlers)
- [ ] **Infrastructure Layer** (adapters, repositories)
- [ ] **API Layer** (routes, dependencies)

## 📸 Screenshots / Ejemplos

<!-- Si aplica, agrega capturas o ejemplos de uso -->

## 🔗 Issues Relacionados

<!-- Referencia issues relacionados: Closes #123 -->

Closes #

## 📝 Notas Adicionales

<!-- Cualquier información adicional para los revisores -->

---

## ✅ Pre-merge Checklist (Para Revisores)

- [ ] El código sigue arquitectura hexagonal
- [ ] Tests pasan en el CI/CD
- [ ] Cobertura de código > 90%
- [ ] Arquitectura hexagonal verificada
- [ ] Sin vulnerabilidades de seguridad
- [ ] Documentación actualizada
- [ ] Code review completado

---

**Recuerda:** Los workflows de GitHub Actions se ejecutarán automáticamente y comentarán aquí con los resultados. ✅

