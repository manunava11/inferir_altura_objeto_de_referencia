#!/usr/bin/env python3
"""
Versión directa de SAM selector para debugging
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Optional
import os

def test_sam_direct(image_path: str, object_real_cm: float) -> Optional[Dict]:
    """
    Test directo de SAM sin la clase SAMSelector
    """
    print("🔍 TEST DIRECTO DE SAM")
    print("=" * 30)
    
    # Verificar checkpoint
    checkpoint = "sam_vit_b_01ec64.pth"
    if not os.path.exists(checkpoint):
        print(f"❌ No se encuentra {checkpoint}")
        return None
    
    print(f"✅ Checkpoint encontrado: {checkpoint}")
    
    # Intentar importar SAM
    try:
        from segment_anything import sam_model_registry, SamPredictor
        print("✅ SAM importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando SAM: {e}")
        return None
    
    # Cargar modelo
    try:
        print("🔄 Cargando modelo SAM...")
        sam = sam_model_registry["vit_b"](checkpoint=checkpoint)
        predictor = SamPredictor(sam)
        print("✅ Modelo SAM cargado")
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        return None
    
    # Cargar imagen
    try:
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        predictor.set_image(image_rgb)
        print(f"✅ Imagen cargada: {image.shape}")
    except Exception as e:
        print(f"❌ Error cargando imagen: {e}")
        return None
    
    # Selección interactiva
    points = []
    masks = []
    
    def onclick(event):
        nonlocal points, masks
        if event.inaxes:
            x, y = int(event.xdata), int(event.ydata)
            points.append([x, y])
            
            plt.plot(x, y, 'ro', markersize=8)
            plt.draw()
            
            print(f"🎯 Punto {len(points)}: ({x}, {y})")
            
            # Generar máscara con SAM
            try:
                input_point = np.array(points)
                input_label = np.array([1] * len(points))
                
                masks_pred, scores, logits = predictor.predict(
                    point_coords=input_point,
                    point_labels=input_label,
                    multimask_output=True
                )
                
                # Usar mejor máscara
                best_mask = masks_pred[np.argmax(scores)]
                masks = [best_mask]
                
                # Mostrar máscara
                plt.imshow(best_mask, alpha=0.3, cmap='Blues')
                plt.draw()
                
                print(f"✅ Máscara generada - Score: {np.max(scores):.3f}")
                
                if len(points) >= 1:
                    plt.close()
                
            except Exception as e:
                print(f"❌ Error generando máscara: {e}")
    
    # Mostrar imagen para selección
    plt.figure(figsize=(12, 8))
    plt.imshow(image_rgb)
    plt.title("TEST DIRECTO SAM - Haz clic en el objeto")
    plt.connect('button_press_event', onclick)
    plt.show()
    
    # Procesar resultado
    if not masks or len(masks) == 0:
        print("❌ No se generó máscara")
        return None
    
    mask = masks[0]
    
    # Calcular dimensiones
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("❌ No se encontraron contornos")
        return None
    
    contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(contour)
    
    # Calcular GSD
    if w > h:
        gsd = object_real_cm / w
    else:
        gsd = object_real_cm / h
    
    result = {
        'width_px': w,
        'height_px': h,
        'area_px': cv2.contourArea(contour),
        'object_real_cm': object_real_cm,
        'gsd_cm_per_px': gsd,
        'method': 'SAM Direct Test',
        'points': points,
        'mask': mask
    }
    
    print("✅ TEST DIRECTO EXITOSO!")
    print(f"   Dimensiones: {w} x {h} px")
    print(f"   GSD: {gsd:.6f} cm/px")
    
    return result

if __name__ == "__main__":
    # Usar la imagen del frame extraído
    image_path = "DJI_0365_frame_0010.jpg"
    if os.path.exists(image_path):
        result = test_sam_direct(image_path, 50.0)
        if result:
            print("🎯 SAM funcionando correctamente!")
        else:
            print("❌ SAM no funcionó")
    else:
        print(f"❌ No se encuentra la imagen: {image_path}")
