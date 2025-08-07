#!/usr/bin/env python3
"""
Script Rápido para Calcular Altura de Video

Uso rápido sin interacción:
    python calcular_altura_rapido.py

O con parámetros:
    python calcular_altura_rapido.py --camera "DJI Mini 3 Pro" --objeto 15.0 --pixels 43.4
"""

import sys
import os
import argparse

# Añadir el directorio utils al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from altura_calculator import create_calculator, display_results

# Importar SAM selector (opcional)
try:
    from sam_selector import select_object_from_image
    SAM_AVAILABLE = True
except ImportError:
    SAM_AVAILABLE = False


def main():
    """Script principal para cálculo rápido."""
    parser = argparse.ArgumentParser(description='Calcula altura de video por objeto de referencia')
    parser.add_argument('--camera', default='DJI Mini 3 Pro', 
                       help='Modelo de cámara (DJI Mini 3 Pro, DJI Mini SE2, Go Pro 12, iPhone 14)')
    parser.add_argument('--objeto', type=float, required=True,
                       help='Tamaño real del objeto en centímetros')
    parser.add_argument('--pixels', type=float, 
                       help='Tamaño del objeto en píxeles (requerido si no se usa --imagen)')
    parser.add_argument('--imagen', type=str,
                       help='Ruta a imagen para selección interactiva con SAM')
    parser.add_argument('--sam-checkpoint', type=str,
                       help='Ruta al checkpoint de SAM (opcional)')
    parser.add_argument('--resolucion', default='3840x2160',
                       help='Resolución del video (ej: 3840x2160)')
    
    args = parser.parse_args()
    
    # Validar argumentos
    if args.pixels is None and args.imagen is None:
        parser.error("Debe especificar --pixels O --imagen")
    
    try:
        # Crear calculadora
        calculator = create_calculator(args.camera)
        
        # Obtener tamaño en píxeles
        if args.pixels is not None:
            object_pixels = args.pixels
        else:
            # Usar SAM para selección interactiva
            if not SAM_AVAILABLE:
                parser.error("SAM no está disponible. Instala: pip install segment-anything-py torch torchvision")
            
            print("🎯 Selección interactiva con SAM...")
            result = select_object_from_image(args.imagen, args.objeto, args.sam_checkpoint)
            
            if result is None:
                print("❌ Selección cancelada")
                sys.exit(1)
            
            object_pixels = max(result['width_px'], result['height_px'])
            print(f"✅ Objeto seleccionado: {object_pixels:.1f} píxeles")
        
        # Calcular altura
        results = calculator.calculate_height_from_reference(
            object_real_cm=args.objeto,
            object_pixels=object_pixels
        )
        
        # Mostrar resultados
        display_results(results)
        
        # Mostrar parámetros para API
        if 'gsd_cm_per_px' in results:
            api_params = calculator.get_api_parameters(results['gsd_cm_per_px'])
            print(f"\n🔧 Parámetros para API:")
            print(f"   altitude: {api_params['altitude']}")
            print(f"   debug_grid_cm: {api_params['debug_grid_cm']}")
            print(f"   focal_length: {api_params.get('focal_length')}")
            print(f"   sensor_width: {api_params['sensor_width']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 