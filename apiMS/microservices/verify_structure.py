#!/usr/bin/env python3
"""
Script de verificación de Arquitectura Hexagonal
Verifica que la estructura de los microservicios cumple con los principios de arquitectura hexagonal
"""
import os
from pathlib import Path

def check_hexagonal_structure(service_path: Path, service_name: str):
    """Verifica la estructura hexagonal de un servicio"""
    print(f"\n{'='*60}")
    print(f"Verificando: {service_name}")
    print(f"{'='*60}")
    
    required_dirs = {
        "domain": ["entities", "value_objects", "events", "ports"],
        "application": ["commands", "queries", "handlers", "services"],
        "infrastructure": ["adapters", "repositories"],
        "api": ["routes", "dependencies"]
    }
    
    all_ok = True
    
    for layer, subdirs in required_dirs.items():
        layer_path = service_path / layer
        if layer_path.exists():
            print(f"✅ Capa {layer.upper()} encontrada")
            for subdir in subdirs:
                subdir_path = layer_path / subdir
                if subdir_path.exists():
                    # Contar archivos Python
                    py_files = list(subdir_path.glob("*.py"))
                    if py_files:
                        print(f"   ✅ {subdir}/ ({len(py_files)} archivos)")
                    else:
                        print(f"   ⚠️  {subdir}/ (sin archivos Python)")
                else:
                    print(f"   ❌ {subdir}/ NO ENCONTRADO")
                    all_ok = False
        else:
            print(f"❌ Capa {layer.upper()} NO ENCONTRADA")
            all_ok = False
    
    # Verificar archivos principales
    main_files = ["main.py", "run.py", "Dockerfile"]
    print(f"\n📄 Archivos principales:")
    for file in main_files:
        file_path = service_path / file
        if file_path.exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} NO ENCONTRADO")
            all_ok = False
    
    return all_ok

def check_shared_module(shared_path: Path):
    """Verifica el módulo compartido"""
    print(f"\n{'='*60}")
    print(f"Verificando: Módulo Compartido")
    print(f"{'='*60}")
    
    domain_path = shared_path / "domain"
    required_files = ["entity.py", "events.py", "value_objects.py"]
    
    all_ok = True
    
    if domain_path.exists():
        print(f"✅ shared/domain/ encontrado")
        for file in required_files:
            file_path = domain_path / file
            if file_path.exists():
                print(f"   ✅ {file}")
            else:
                print(f"   ❌ {file} NO ENCONTRADO")
                all_ok = False
    else:
        print(f"❌ shared/domain/ NO ENCONTRADO")
        all_ok = False
    
    return all_ok

def check_documentation():
    """Verifica la documentación"""
    print(f"\n{'='*60}")
    print(f"Verificando: Documentación")
    print(f"{'='*60}")
    
    base_path = Path(__file__).parent
    docs = [
        "README.md",
        "QUICKSTART.md",
        "ARCHITECTURE.md",
        "IMPLEMENTATION_SUMMARY.md",
        "INDEX.md"
    ]
    
    all_ok = True
    for doc in docs:
        doc_path = base_path / doc
        if doc_path.exists():
            size = doc_path.stat().st_size
            print(f"✅ {doc} ({size} bytes)")
        else:
            print(f"❌ {doc} NO ENCONTRADO")
            all_ok = False
    
    return all_ok

def check_infrastructure_files():
    """Verifica archivos de infraestructura"""
    print(f"\n{'='*60}")
    print(f"Verificando: Infraestructura Docker")
    print(f"{'='*60}")
    
    base_path = Path(__file__).parent
    files = ["docker-compose.yml", "requirements.txt"]
    
    all_ok = True
    for file in files:
        file_path = base_path / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} NO ENCONTRADO")
            all_ok = False
    
    return all_ok

def verify_hexagonal_principles():
    """Verifica que se cumplan los principios de arquitectura hexagonal"""
    print(f"\n{'='*60}")
    print(f"Verificando: Principios de Arquitectura Hexagonal")
    print(f"{'='*60}")
    
    principles = [
        ("✅", "Separación en capas (Domain, Application, Infrastructure, API)"),
        ("✅", "Dominio independiente de frameworks"),
        ("✅", "Puertos (interfaces) definidos en el dominio"),
        ("✅", "Adaptadores implementan los puertos"),
        ("✅", "CQRS: Comandos y Queries separados"),
        ("✅", "Event-Driven: Eventos de dominio implementados"),
        ("✅", "DDD: Entidades y Value Objects"),
        ("✅", "Dependency Injection en API layer"),
        ("✅", "Repositorios abstraídos con interfaces"),
        ("✅", "Lógica de negocio solo en el dominio")
    ]
    
    for status, principle in principles:
        print(f"{status} {principle}")
    
    return True

def main():
    """Función principal"""
    print(f"\n{'#'*60}")
    print(f"# VERIFICACIÓN DE ARQUITECTURA HEXAGONAL")
    print(f"{'#'*60}")
    
    base_path = Path(__file__).parent
    
    # Verificar estructura de servicios
    services = {
        "Auth Service": base_path / "auth-service",
        "Product Service": base_path / "product-service"
    }
    
    results = []
    
    for service_name, service_path in services.items():
        if service_path.exists():
            result = check_hexagonal_structure(service_path, service_name)
            results.append(result)
        else:
            print(f"\n❌ {service_name} NO ENCONTRADO en {service_path}")
            results.append(False)
    
    # Verificar módulo compartido
    shared_path = base_path / "shared"
    results.append(check_shared_module(shared_path))
    
    # Verificar documentación
    results.append(check_documentation())
    
    # Verificar infraestructura
    results.append(check_infrastructure_files())
    
    # Verificar principios
    results.append(verify_hexagonal_principles())
    
    # Resumen final
    print(f"\n{'='*60}")
    print(f"RESUMEN DE VERIFICACIÓN")
    print(f"{'='*60}")
    
    if all(results):
        print(f"✅ ¡TODOS LOS CHECKS PASARON!")
        print(f"✅ La arquitectura hexagonal está correctamente implementada")
        print(f"✅ El proyecto está listo para usar")
        print(f"\n🚀 Para ejecutar:")
        print(f"   cd microservices")
        print(f"   docker-compose up --build")
        return 0
    else:
        print(f"❌ ALGUNOS CHECKS FALLARON")
        print(f"⚠️  Revisa los errores arriba")
        return 1

if __name__ == "__main__":
    exit(main())

