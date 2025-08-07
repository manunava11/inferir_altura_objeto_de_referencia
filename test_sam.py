#!/usr/bin/env python3
"""
Script de diagnóstico para verificar SAM
"""

print("🔍 DIAGNÓSTICO DE SAM")
print("=" * 40)

# Test 1: Importar segment_anything
try:
    import segment_anything
    print("✅ segment_anything importado correctamente")
    print(f"   Versión: {getattr(segment_anything, '__version__', 'No disponible')}")
except ImportError as e:
    print(f"❌ Error importando segment_anything: {e}")

# Test 2: Importar componentes específicos
try:
    from segment_anything import SamPredictor, sam_model_registry
    print("✅ SamPredictor y sam_model_registry importados")
except ImportError as e:
    print(f"❌ Error importando componentes SAM: {e}")

# Test 3: Verificar torch
try:
    import torch
    print(f"✅ PyTorch disponible: {torch.__version__}")
    print(f"   CUDA disponible: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"❌ Error importando torch: {e}")

# Test 4: Verificar nuestro sam_selector
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
    from sam_selector import SAMSelector
    print("✅ sam_selector importado correctamente")
    
    # Crear selector y verificar estado
    selector = SAMSelector()
    if selector.predictor is not None:
        print("✅ SAM predictor inicializado")
    else:
        print("❌ SAM predictor no inicializado (falta checkpoint)")
        
except Exception as e:
    print(f"❌ Error con sam_selector: {e}")

print("\n💡 RECOMENDACIONES:")
print("Si SAM no está disponible:")
print("1. Instalar: pip install segment-anything")
print("2. Instalar PyTorch: pip install torch torchvision")
print("3. Descargar checkpoint SAM de: https://github.com/facebookresearch/segment-anything")
