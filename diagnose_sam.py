#!/usr/bin/env python3
"""
Diagnóstico específico para SAM
"""
import os
import sys

print("🔍 DIAGNÓSTICO DETALLADO DE SAM")
print("=" * 50)

# Verificar checkpoint
print("📁 CHECKPOINT:")
checkpoint_file = "sam_vit_b_01ec64.pth"
if os.path.exists(checkpoint_file):
    size_mb = os.path.getsize(checkpoint_file) / (1024*1024)
    print(f"✅ Encontrado: {checkpoint_file} ({size_mb:.1f} MB)")
else:
    print(f"❌ No encontrado: {checkpoint_file}")

print()
print("📦 IMPORTS:")

# Test imports
try:
    import torch
    print(f"✅ torch: {torch.__version__}")
    print(f"   CUDA disponible: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"❌ torch: {e}")

try:
    import torchvision
    print(f"✅ torchvision: {torchvision.__version__}")
except ImportError as e:
    print(f"❌ torchvision: {e}")

try:
    import segment_anything
    print(f"✅ segment_anything importado")
    print(f"   Ubicación: {segment_anything.__file__}")
except ImportError as e:
    print(f"❌ segment_anything: {e}")
    print("💡 Instala con: pip install segment-anything")

try:
    from segment_anything import sam_model_registry, SamPredictor
    print("✅ Componentes SAM importados")
except ImportError as e:
    print(f"❌ Componentes SAM: {e}")

print()
print("🧪 TEST SAM:")

# Test crear SAM
try:
    from segment_anything import sam_model_registry, SamPredictor
    import torch
    
    print("🔄 Intentando cargar modelo SAM...")
    sam = sam_model_registry["vit_b"](checkpoint=checkpoint_file)
    print("✅ Modelo SAM cargado")
    
    predictor = SamPredictor(sam)
    print("✅ Predictor SAM creado")
    
    print("🎯 SAM está completamente funcional")
    
except Exception as e:
    print(f"❌ Error creando SAM: {e}")
    print(f"   Tipo de error: {type(e).__name__}")
