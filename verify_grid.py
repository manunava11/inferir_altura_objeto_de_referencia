#!/usr/bin/env python3
"""
Script de verificación de cálculos de grilla
"""

def verify_grid_calculation():
    print("🔍 VERIFICACIÓN DE CÁLCULOS DE GRILLA")
    print("=" * 50)
    
    # Datos de ejemplo (sustituye con tus valores reales)
    object_real_cm = 50  # AprilTag de 50cm
    object_pixels = 100  # Ejemplo: objeto ocupa 100 píxeles
    
    # Calcular GSD
    gsd = object_real_cm / object_pixels
    print(f"📐 Objeto real: {object_real_cm}cm")
    print(f"📐 Objeto en píxeles: {object_pixels}px")
    print(f"📐 GSD calculado: {gsd:.6f} cm/px")
    print()
    
    # Probar diferentes tamaños de grilla
    grid_sizes = [10, 25, 50, 100]
    
    for grid_cm in grid_sizes:
        grid_px = int(grid_cm / gsd)
        verification = grid_px * gsd
        
        print(f"Grilla de {grid_cm}cm:")
        print(f"  - En píxeles: {grid_px}px")
        print(f"  - Verificación: {grid_px}px × {gsd:.6f}cm/px = {verification:.2f}cm")
        print(f"  - Diferencia: {abs(verification - grid_cm):.2f}cm")
        print()
    
    print("💡 INTERPRETACIÓN:")
    print("- Si la diferencia es grande (>2cm), hay un problema en el cálculo del GSD")
    print("- El GSD debe coincidir con la medición real del objeto")
    print("- Cada cuadro de la grilla debe medir exactamente el tamaño especificado")

if __name__ == "__main__":
    verify_grid_calculation()
