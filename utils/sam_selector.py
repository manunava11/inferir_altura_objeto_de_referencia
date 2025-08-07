"""
Módulo para selección interactiva de objetos usando SAM (Segment Anything Model)

Este módulo permite seleccionar objetos en imágenes haciendo clic, usando SAM
para segmentación automática y medición de dimensiones.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List, Optional, Dict
import torch
from segment_anything import SamPredictor, sam_model_registry
import os
import sys


class SAMSelector:
    """
    Selector de objetos usando SAM para medición interactiva.
    """
    
    def __init__(self, sam_checkpoint_path: Optional[str] = None, model_type: str = "vit_b"):
        """
        Inicializar SAM selector.
        
        Args:
            sam_checkpoint_path: Ruta al checkpoint de SAM (opcional)
            model_type: Tipo de modelo SAM ('vit_h', 'vit_l', 'vit_b')
        """
        self.model_type = model_type
        self.sam_checkpoint_path = sam_checkpoint_path
        self.predictor = None
        self.image = None
        self.image_rgb = None
        
        # Auto-detectar modelo basado en el checkpoint encontrado
        if self.sam_checkpoint_path is None:
            self._auto_detect_model_type()
        
        # Intentar cargar SAM
        self._load_sam()
    
    def _auto_detect_model_type(self):
        """Auto-detectar tipo de modelo basado en checkpoint disponible."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Directorio padre
        checkpoint_patterns = [
            ("sam_vit_b_01ec64.pth", "vit_b"),
            ("sam_vit_l_0b3195.pth", "vit_l"), 
            ("sam_vit_h_4b8939.pth", "vit_h"),
            (os.path.join(base_dir, "sam_vit_b_01ec64.pth"), "vit_b"),
            (os.path.join(base_dir, "sam_vit_l_0b3195.pth"), "vit_l"),
            (os.path.join(base_dir, "sam_vit_h_4b8939.pth"), "vit_h")
        ]
        
        for checkpoint_path, model_type in checkpoint_patterns:
            if os.path.exists(checkpoint_path):
                self.sam_checkpoint_path = checkpoint_path
                self.model_type = model_type
                print(f"🔍 DEBUG: Auto-detectado modelo {model_type} con checkpoint {checkpoint_path}")
                return
        
        print("🔍 DEBUG: No se encontró checkpoint automático")
    
    def _load_sam(self):
        """Cargar modelo SAM."""
        print("🔍 DEBUG: Iniciando carga de SAM...")
        try:
            if self.sam_checkpoint_path is None:
                print("🔍 DEBUG: Buscando checkpoint automáticamente...")
                # Intentar encontrar checkpoint automáticamente
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Directorio padre
                possible_paths = [
                    "sam_vit_h_4b8939.pth",
                    "sam_vit_l_0b3195.pth", 
                    "sam_vit_b_01ec64.pth",
                    "models/sam_vit_h_4b8939.pth",
                    "checkpoints/sam_vit_h_4b8939.pth",
                    # También buscar en el directorio base del proyecto
                    os.path.join(base_dir, "sam_vit_h_4b8939.pth"),
                    os.path.join(base_dir, "sam_vit_l_0b3195.pth"),
                    os.path.join(base_dir, "sam_vit_b_01ec64.pth")
                ]
                
                for path in possible_paths:
                    print(f"🔍 DEBUG: Verificando {path}...")
                    if os.path.exists(path):
                        self.sam_checkpoint_path = path
                        print(f"✅ DEBUG: Encontrado checkpoint: {path}")
                        break
                
                if self.sam_checkpoint_path is None:
                    print("⚠️  No se encontró checkpoint de SAM. Usando modo manual.")
                    return
            
            print(f"🔍 DEBUG: Intentando importar SAM...")
            # Verificar imports antes de continuar
            try:
                from segment_anything import sam_model_registry, SamPredictor
                print("✅ DEBUG: Imports SAM exitosos")
            except ImportError as e:
                print(f"❌ DEBUG: Error importando SAM: {e}")
                self.predictor = None
                return
            
            # Cargar modelo SAM
            print(f"🔄 Cargando SAM modelo {self.model_type}...")
            print(f"🔍 DEBUG: Usando checkpoint: {self.sam_checkpoint_path}")
            sam = sam_model_registry[self.model_type](checkpoint=self.sam_checkpoint_path)
            self.predictor = SamPredictor(sam)
            print("✅ SAM cargado exitosamente")
            
        except Exception as e:
            print(f"❌ Error cargando SAM: {e}")
            print(f"🔍 DEBUG: Tipo de error: {type(e).__name__}")
            print("💡 Para usar SAM, descarga el checkpoint de:")
            print("   https://github.com/facebookresearch/segment-anything")
            print("   Y especifica la ruta con --sam-checkpoint")
            self.predictor = None
    
    def load_image(self, image_path: str) -> bool:
        """
        Cargar imagen para selección.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            # Cargar imagen
            self.image = cv2.imread(image_path)
            if self.image is None:
                print(f"❌ No se pudo cargar la imagen: {image_path}")
                return False
            
            # Convertir a RGB para matplotlib
            self.image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            
            # Configurar predictor SAM si está disponible
            if self.predictor is not None:
                self.predictor.set_image(self.image_rgb)
            
            print(f"✅ Imagen cargada: {self.image.shape[1]}x{self.image.shape[0]} píxeles")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando imagen: {e}")
            return False
    
    def select_object_interactive(self, object_real_cm: float) -> Optional[Dict]:
        """
        Seleccionar objeto interactivamente haciendo clic.
        
        Args:
            object_real_cm: Tamaño real del objeto en centímetros
            
        Returns:
            dict: Información del objeto seleccionado o None si se cancela
        """
        if self.image is None:
            print("❌ No hay imagen cargada")
            return None
        
        # Variables para capturar clics
        points = []
        point_labels = []
        mask = None
        
        def onclick(event):
            nonlocal points, point_labels, mask
            
            if event.inaxes:
                x, y = int(event.xdata), int(event.ydata)
                
                # Añadir punto
                points.append([x, y])
                point_labels.append(1)  # 1 = punto positivo
                
                # Dibujar punto
                plt.plot(x, y, 'ro', markersize=8)
                plt.draw()
                
                # Si tenemos SAM, generar máscara
                if self.predictor is not None and len(points) >= 1:
                    try:
                        # Convertir puntos a formato SAM
                        input_point = np.array(points)
                        input_label = np.array(point_labels)
                        
                        # Predecir máscara
                        masks, scores, logits = self.predictor.predict(
                            point_coords=input_point,
                            point_labels=input_label,
                            multimask_output=True
                        )
                        
                        # Usar la máscara con mejor score
                        best_mask_idx = np.argmax(scores)
                        mask = masks[best_mask_idx]
                        
                        # Mostrar máscara
                        plt.imshow(mask, alpha=0.3, cmap='Blues')
                        plt.draw()
                        
                        print(f"🎯 Punto {len(points)}: ({x}, {y}) - Score: {scores[best_mask_idx]:.3f}")
                        
                    except Exception as e:
                        print(f"❌ Error generando máscara: {e}")
                else:
                    print(f"🎯 Punto {len(points)}: ({x}, {y})")
                
                # Si tenemos suficientes puntos o máscara, terminar
                if len(points) >= 3 or (mask is not None and len(points) >= 1):
                    plt.disconnect('button_press_event')
                    plt.close()
        
        # Mostrar imagen
        plt.figure(figsize=(12, 8))
        plt.imshow(self.image_rgb)
        plt.title("Haz clic en el objeto de referencia (múltiples clics para mejor precisión)")
        plt.axis('on')
        
        # Conectar evento de clic
        plt.connect('button_press_event', onclick)
        plt.show()
        
        # Procesar resultado
        if len(points) == 0:
            print("❌ No se seleccionaron puntos")
            return None
        
        # Calcular dimensiones del objeto
        if mask is not None:
            # Usar máscara SAM para medición precisa
            return self._measure_from_mask(mask, object_real_cm, points)
        else:
            # Usar puntos manuales
            return self._measure_from_points(points, object_real_cm)
    
    def _measure_from_mask(self, mask: np.ndarray, object_real_cm: float, points: List) -> Dict:
        """
        Medir objeto usando máscara SAM.
        
        Args:
            mask: Máscara binaria del objeto
            object_real_cm: Tamaño real del objeto
            points: Puntos de clic
            
        Returns:
            dict: Información de medición
        """
        # Encontrar contorno de la máscara
        contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return self._measure_from_points(points, object_real_cm)
        
        # Usar el contorno más grande
        contour = max(contours, key=cv2.contourArea)
        
        # Calcular bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Calcular dimensiones en píxeles
        width_px = w
        height_px = h
        
        # Calcular área y perímetro
        area_px = cv2.contourArea(contour)
        perimeter_px = cv2.arcLength(contour, True)
        
        # Calcular GSD asumiendo objeto cuadrado
        if width_px > height_px:
            gsd = object_real_cm / width_px
        else:
            gsd = object_real_cm / height_px
        
        return {
            'width_px': width_px,
            'height_px': height_px,
            'area_px': area_px,
            'perimeter_px': perimeter_px,
            'object_real_cm': object_real_cm,
            'gsd_cm_per_px': gsd,
            'method': 'SAM mask',
            'points': points,
            'mask': mask
        }
    
    def _measure_from_points(self, points: List, object_real_cm: float) -> Dict:
        """
        Medir objeto usando puntos manuales.
        
        Args:
            points: Lista de puntos de clic
            object_real_cm: Tamaño real del objeto
            
        Returns:
            dict: Información de medición
        """
        if len(points) < 2:
            print("❌ Se necesitan al menos 2 puntos para medición manual")
            return None
        
        # Calcular distancia entre puntos
        distances = []
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                p1, p2 = points[i], points[j]
                dist = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                distances.append(dist)
        
        # Usar la distancia más grande como dimensión principal
        max_distance = max(distances)
        
        # Calcular GSD
        gsd = object_real_cm / max_distance
        
        return {
            'width_px': max_distance,
            'height_px': max_distance,  # Asumir cuadrado
            'area_px': max_distance ** 2,
            'perimeter_px': max_distance * 4,
            'object_real_cm': object_real_cm,
            'gsd_cm_per_px': gsd,
            'method': 'Manual points',
            'points': points,
            'mask': None
        }
    
    def display_measurement_result(self, result: Dict):
        """
        Mostrar resultado de la medición.
        
        Args:
            result: Resultado de la medición
        """
        if result is None:
            return
        
        print("\n📐 RESULTADO DE MEDICIÓN")
        print("=" * 40)
        print(f"🎯 Método: {result['method']}")
        print(f"📏 Dimensiones: {result['width_px']:.1f} x {result['height_px']:.1f} px")
        print(f"📐 Área: {result['area_px']:.1f} px²")
        print(f"📏 Perímetro: {result['perimeter_px']:.1f} px")
        print(f"🎯 Objeto real: {result['object_real_cm']} cm")
        print(f"📐 GSD calculado: {result['gsd_cm_per_px']:.4f} cm/px")
        print(f"📏 Precisión: {result['gsd_cm_per_px'] * 10:.2f} mm/px")
        print(f"📍 Puntos seleccionados: {len(result['points'])}")


def create_sam_selector(sam_checkpoint_path: Optional[str] = None) -> SAMSelector:
    """
    Crear selector SAM con configuración automática.
    
    Args:
        sam_checkpoint_path: Ruta al checkpoint de SAM
        
    Returns:
        SAMSelector: Selector configurado
    """
    return SAMSelector(sam_checkpoint_path)


# Función de conveniencia para uso rápido
def select_object_from_image(image_path: str, object_real_cm: float, 
                           sam_checkpoint_path: Optional[str] = None) -> Optional[Dict]:
    """
    Seleccionar objeto de una imagen de forma rápida.
    
    Args:
        image_path: Ruta a la imagen
        object_real_cm: Tamaño real del objeto en centímetros
        sam_checkpoint_path: Ruta al checkpoint de SAM (opcional)
        
    Returns:
        dict: Información del objeto seleccionado o None si se cancela
    """
    selector = create_sam_selector(sam_checkpoint_path)
    
    if not selector.load_image(image_path):
        return None
    
    result = selector.select_object_interactive(object_real_cm)
    
    if result:
        selector.display_measurement_result(result)
    
    return result 