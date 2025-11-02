#!/usr/bin/env python3
"""
Script para filtrar archivos con 0% de cobertura del reporte XML.
Elimina archivos/clases con 0% de cobertura para que el total solo incluya
archivos con cobertura > 0%.
"""
import xml.etree.ElementTree as ET
import os
import sys

cov_file = 'coverage.xml'
if not os.path.exists(cov_file):
    print('⚠️  Archivo coverage.xml no encontrado')
    sys.exit(0)

tree = ET.parse(cov_file)
root = tree.getroot()
removed_count = 0

for package in root.findall('.//package'):
    classes_to_remove = []
    for clazz in package.findall('.//class'):
        lines = clazz.findall('.//line')
        if not lines:
            classes_to_remove.append(clazz)
            continue
        covered_lines = sum(1 for line in lines if line.get('hits', '0') != '0')
        total_lines = len(lines)
        if total_lines > 0 and (covered_lines / total_lines) * 100 == 0:
            classes_to_remove.append(clazz)
            removed_count += 1
    for clazz in classes_to_remove:
        package.remove(clazz)

packages_to_remove = [pkg for pkg in root.findall('.//package') if len(pkg.findall('.//class')) == 0]
for package in packages_to_remove:
    parent = root.find('.//package/..')
    if parent is not None:
        parent.remove(package)

tree.write(cov_file)
print(f'✅ Filtrado coverage.xml - excluidos {removed_count} archivos con 0% de cobertura')
print('✅ El total ahora solo incluye archivos con cobertura > 0%')

