#!/usr/bin/env python3
"""
Script de prueba para verificar que todos los imports funcionan correctamente
"""

import sys
import os

# Añadir el directorio utils al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

def test_imports():
    """Probar todos los imports necesarios."""
    print("🧪 PROBANDO IMPORTS")
    print("=" * 30)
    
    # Probar altura_calculator
    try:
        from altura_calculator import create_calculator, display_results
        print("✅ altura_calculator - OK")
    except ImportError as e:
        print(f"❌ altura_calculator - Error: {e}")
        return False
    
    # Probar sam_selector (opcional)
    try:
        from sam_selector import select_object_from_image
        print("✅ sam_selector - OK")
    except ImportError as e:
        print(f"⚠️  sam_selector - No disponible: {e}")
    
    # Probar video_utils
    try:
        from video_utils import extract_frame
        print("✅ video_utils - OK")
    except ImportError as e:
        print(f"❌ video_utils - Error: {e}")
        return False
    
    # Probar crear calculadora
    try:
        calculator = create_calculator("DJI Mini 3 Pro")
        print("✅ Crear calculadora - OK")
    except Exception as e:
        print(f"❌ Crear calculadora - Error: {e}")
        return False
    
    print("\n🎉 ¡Todos los imports funcionan correctamente!")
    return True

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ El sistema está listo para usar")
        print("💡 Prueba ejecutar: python calcular_altura_local.py")
    else:
        print("\n❌ Hay problemas con los imports")
        print("💡 Verifica que todas las dependencias estén instaladas") 