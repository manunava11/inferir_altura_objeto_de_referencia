#!/usr/bin/env python3
"""
Script Local para Calcular Altura de Video por Objeto de Referencia

Este script te permite calcular la altura a la que se grabó un video basándose en 
objetos de referencia del cual conoces sus dimensiones reales.

Uso:
    python calcular_altura_local.py

Autor: Sistema de Ganadería
Fecha: 2025
"""

import sys
import os
from typing import Optional

# Añadir el directorio utils al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from altura_calculator import (
    create_calculator, 
    ReferenceObject, 
    display_results, 
    display_validation_stats,
    CameraConfig
)

# Importar SAM selector (opcional)
try:
    from sam_selector import select_object_from_image, create_sam_selector
    SAM_AVAILABLE = True
except ImportError:
    SAM_AVAILABLE = False
    print("⚠️  SAM no disponible. Para usar selección interactiva, instala:")
    print("   pip install segment-anything-py torch torchvision")


def main():
    """Función principal del script."""
    print("🔍 CALCULADORA DE ALTURA POR OBJETO DE REFERENCIA")
    print("=" * 60)
    print()
    
    # ===== CONFIGURACIÓN DE CÁMARA =====
    print("📷 CONFIGURACIÓN DE CÁMARA")
    print("-" * 30)
    
    # Opciones de cámara predefinidas (basadas en etl/config.json)
    camera_options = {
        "1": "DJI Mini 3 Pro",
        "2": "DJI Mini SE2", 
        "3": "Go Pro 12",
        "4": "iPhone 14",
        "5": "Configuración personalizada"
    }
    
    print("Selecciona tu cámara:")
    for key, value in camera_options.items():
        print(f"   {key}. {value}")
    
    while True:
        choice = input("\nOpción (1-5): ").strip()
        if choice in camera_options:
            break
        print("❌ Opción inválida. Intenta de nuevo.")
    
    if choice == "5":
        # Configuración personalizada
        calculator = get_custom_camera_config()
    else:
        camera_model = camera_options[choice]
        calculator = create_calculator(camera_model)
        print(f"✅ Configurada: {camera_model}")
    
    print()
    
    # ===== OBJETO DE REFERENCIA =====
    print("🎯 OBJETO DE REFERENCIA")
    print("-" * 30)
    
    # Preguntar método de medición
    print("¿Cómo quieres medir el objeto?")
    print("1. Entrada manual (tamaño en píxeles)")
    print("2. Selección interactiva con SAM (recomendado)")
    
    if not SAM_AVAILABLE:
        print("   ⚠️  SAM no disponible - solo opción 1")
    
    while True:
        method_choice = input("\nOpción (1-2): ").strip()
        if method_choice in ["1", "2"]:
            break
        print("❌ Opción inválida. Intenta de nuevo.")
    
    # Obtener tamaño real del objeto
    try:
        object_real_cm = float(input("Tamaño real del objeto (cm): "))
        if object_real_cm <= 0:
            raise ValueError("El tamaño debe ser mayor que 0")
    except ValueError as e:
        print(f"❌ Error en el tamaño: {e}")
        return
    
    # Procesar según método elegido
    if method_choice == "1":
        # Método manual
        try:
            object_pixels = float(input("Tamaño del objeto en píxeles: "))
            if object_pixels <= 0:
                raise ValueError("El tamaño en píxeles debe ser mayor que 0")
        except ValueError as e:
            print(f"❌ Error en los datos: {e}")
            return
    else:
        # Método SAM
        if not SAM_AVAILABLE:
            print("❌ SAM no está disponible. Usando método manual.")
            try:
                object_pixels = float(input("Tamaño del objeto en píxeles: "))
                if object_pixels <= 0:
                    raise ValueError("El tamaño en píxeles debe ser mayor que 0")
            except ValueError as e:
                print(f"❌ Error en los datos: {e}")
                return
        else:
            # Usar SAM para selección interactiva
            object_pixels = select_object_with_sam(object_real_cm)
            if object_pixels is None:
                print("❌ Selección cancelada")
                return
    
    print()
    
    # ===== CÁLCULO DE ALTURA =====
    print("📊 CALCULANDO ALTURA...")
    print("-" * 30)
    
    try:
        results = calculator.calculate_height_from_reference(
            object_real_cm=object_real_cm,
            object_pixels=object_pixels
        )
        
        # Mostrar resultados
        display_results(results)
        
    except Exception as e:
        print(f"❌ Error en el cálculo: {e}")
        return
    
    # ===== VALIDACIÓN CON MÚLTIPLES OBJETOS =====
    print("\n🔍 ¿Tienes más objetos de referencia para validar? (s/n): ", end="")
    if input().lower().startswith('s'):
        validate_with_multiple_objects(calculator)
    
    # ===== ANÁLISIS DE SENSIBILIDAD =====
    print("\n📈 ¿Quieres ver análisis de sensibilidad? (s/n): ", end="")
    if input().lower().startswith('s'):
        analyze_sensitivity(calculator, object_real_cm, object_pixels)
    
    # ===== PARÁMETROS PARA API =====
    if 'gsd_cm_per_px' in results:
        show_api_parameters(calculator, results['gsd_cm_per_px'])
    
    print("\n✅ ¡Cálculo completado!")


def select_object_with_sam(object_real_cm: float) -> Optional[float]:
    """
    Seleccionar objeto usando SAM de forma interactiva.
    
    Args:
        object_real_cm: Tamaño real del objeto en centímetros
        
    Returns:
        float: Tamaño del objeto en píxeles o None si se cancela
    """
    print("\n🎯 SELECCIÓN INTERACTIVA CON SAM")
    print("-" * 40)
    
    # Solicitar ruta de imagen
    image_path = input("Ruta a la imagen/frame del video: ").strip()
    
    if not os.path.exists(image_path):
        print(f"❌ No se encontró la imagen: {image_path}")
        return None
    
    # Solicitar checkpoint de SAM (opcional)
    sam_checkpoint = input("Ruta al checkpoint de SAM (Enter para auto-detectar): ").strip()
    if not sam_checkpoint:
        sam_checkpoint = None
    
    try:
        # Seleccionar objeto
        result = select_object_from_image(image_path, object_real_cm, sam_checkpoint)
        
        if result is None:
            return None
        
        # Retornar el tamaño en píxeles (usar el más grande)
        return max(result['width_px'], result['height_px'])
        
    except Exception as e:
        print(f"❌ Error en selección SAM: {e}")
        return None


def get_custom_camera_config():
    """Obtiene configuración personalizada de cámara."""
    print("\n📷 CONFIGURACIÓN PERSONALIZADA")
    print("-" * 30)
    
    try:
        image_width = int(input("Ancho de imagen (píxeles) [3840]: ") or "3840")
        image_height = int(input("Alto de imagen (píxeles) [2160]: ") or "2160")
        
        print("\nMétodo de cálculo:")
        print("1. Tradicional (focal length + sensor width)")
        print("2. FOV (campo de visión)")
        print("3. Ambos")
        
        method = input("Opción (1-3): ").strip()
        
        focal_length_mm = None
        sensor_width_mm = None
        fov_degrees = None
        
        if method in ["1", "3"]:
            focal_length_mm = float(input("Focal length (mm): "))
            sensor_width_mm = float(input("Sensor width (mm): "))
        
        if method in ["2", "3"]:
            fov_degrees = float(input("FOV horizontal (grados): "))
        
        camera_model = input("Modelo de cámara [Personalizada]: ") or "Personalizada"
        
        config = CameraConfig(
            image_width=image_width,
            image_height=image_height,
            focal_length_mm=focal_length_mm,
            sensor_width_mm=sensor_width_mm,
            fov_degrees=fov_degrees,
            camera_model=camera_model
        )
        
        from altura_calculator import AlturaCalculator
        return AlturaCalculator(config)
        
    except ValueError as e:
        print(f"❌ Error en configuración: {e}")
        return get_custom_camera_config()


def validate_with_multiple_objects(calculator):
    """Valida con múltiples objetos de referencia."""
    print("\n🔍 VALIDACIÓN CON MÚLTIPLES OBJETOS")
    print("-" * 40)
    
    reference_objects = []
    
    while True:
        print(f"\nObjeto #{len(reference_objects) + 1}:")
        try:
            name = input("Nombre del objeto (ej: AprilTag 1): ")
            real_length = float(input("Largo real (cm): "))
            real_width = float(input("Ancho real (cm): "))
            pixels_length = float(input("Largo en píxeles: "))
            pixels_width = float(input("Ancho en píxeles: "))
            position = input("Posición (ej: Centro, Esquina): ")
            
            obj = ReferenceObject(
                name=name,
                real_length_cm=real_length,
                real_width_cm=real_width,
                pixels_length=pixels_length,
                pixels_width=pixels_width,
                position=position
            )
            
            reference_objects.append(obj)
            
            more = input("\n¿Añadir otro objeto? (s/n): ")
            if not more.lower().startswith('s'):
                break
                
        except ValueError as e:
            print(f"❌ Error en datos: {e}")
            continue
    
    if len(reference_objects) >= 2:
        try:
            stats = calculator.validate_multiple_objects(reference_objects)
            display_validation_stats(stats)
        except Exception as e:
            print(f"❌ Error en validación: {e}")
    else:
        print("❌ Se requieren al menos 2 objetos para validación")


def analyze_sensitivity(calculator, object_real_cm, object_pixels):
    """Analiza la sensibilidad del cálculo."""
    print("\n📈 ANÁLISIS DE SENSIBILIDAD")
    print("-" * 30)
    
    try:
        sensitivity = calculator.analyze_sensitivity(
            object_real_cm=object_real_cm,
            object_pixels=object_pixels
        )
        
        base_results = sensitivity['base_results']
        print(f"📐 Medición base: {object_pixels} px")
        
        if 'height_traditional_m' in base_results:
            print(f"   Altura base (Trad): {base_results['height_traditional_m']:.2f} m")
        if 'height_fov_m' in base_results:
            print(f"   Altura base (FOV): {base_results['height_fov_m']:.2f} m")
        
        print(f"\n{'Error (px)':>10} {'Píxeles':>10} {'Altura Trad (m)':>15} {'Altura FOV (m)':>15} {'Diff %':>10}")
        print("-" * 70)
        
        for result in sensitivity['sensitivity_results']:
            error = result['pixel_error']
            new_pixels = result['new_pixels']
            height_trad = result.get('height_traditional_m', 0)
            height_fov = result.get('height_fov_m', 0)
            diff_trad = result.get('diff_traditional_percent', 0)
            
            print(f"{error:>10} {new_pixels:>10.1f} {height_trad:>15.2f} {height_fov:>15.2f} {diff_trad:>10.1f}%")
        
        print("\n💡 Recomendaciones:")
        print("   • Medir con precisión de ±1 píxel para error < 2%")
        print("   • Usar objetos grandes para reducir error relativo")
        print("   • Validar con múltiples objetos")
        
    except Exception as e:
        print(f"❌ Error en análisis: {e}")


def show_api_parameters(calculator, gsd):
    """Muestra parámetros para usar con la API."""
    print("\n🔧 PARÁMETROS PARA LA API")
    print("-" * 30)
    
    try:
        api_params = calculator.get_api_parameters(gsd)
        
        print("Parámetros para VideoPredictionRequest:")
        for key, value in api_params.items():
            print(f"   {key}: {value}")
        
        # Mostrar diferentes tamaños de grilla
        print("\n📏 Diferentes tamaños de grilla (debug_grid_cm):")
        for grid_cm in [25, 50, 100, 200]:
            grid_params = calculator.calculate_debug_grid_cm(gsd, grid_cm)
            print(f"   {grid_cm}cm → {grid_params['box_size_px']:.1f} px")
        
        print(f"\n💡 Uso en la API:")
        print(f"   debug_grid_cm={api_params['debug_grid_cm']}")
        print(f"   altitude={api_params['altitude']}")
        
    except Exception as e:
        print(f"❌ Error al calcular parámetros API: {e}")


def show_example():
    """Muestra un ejemplo de uso."""
    print("\n📋 EJEMPLO DE USO")
    print("-" * 30)
    print("Imagina que tienes un AprilTag de 15cm en tu video:")
    print("1. Mides el AprilTag en el video: 43.4 píxeles")
    print("2. Configuras tu cámara: DJI Mini 3 Pro")
    print("3. El script calcula:")
    print("   - GSD = 15.0 cm / 43.4 px = 0.3456 cm/px")
    print("   - Altura = 9.9 metros")
    print("4. Obtienes parámetros para la API:")
    print("   - altitude: 990")
    print("   - debug_grid_cm: 50")
    print()


if __name__ == "__main__":
    try:
        # Mostrar ejemplo si no hay argumentos
        if len(sys.argv) == 1:
            show_example()
        
        main()
        
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("💡 Asegúrate de que el archivo utils/altura_calculator.py esté disponible") 