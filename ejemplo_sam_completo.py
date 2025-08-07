#!/usr/bin/env python3
"""
Ejemplo completo de uso del sistema con SAM

Este script demuestra el flujo completo:
1. Extraer frame del video
2. Seleccionar objeto con SAM
3. Calcular altura
4. Generar parámetros para API
"""

import sys
import os

# Añadir el directorio utils al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

def main():
    print("🎯 EJEMPLO COMPLETO CON SAM")
    print("=" * 50)
    
    # Configuración del ejemplo
    video_path = r'E:\Cursor\objeto_referencia\Objeto_de_referencia\DJI_20250731133901_0030_D.MP4'  # Cambiar por tu video
    object_real_cm = 50  # AprilTag de 15cm
    frame_number = 10  # Frame a extraer
    
    # Configuración de grilla de debug
    print("📐 CONFIGURACIÓN DE GRILLA DE DEBUG")
    print("-" * 40)
    try:
        grid_size_input = input("Ingresa el tamaño de grilla en cm (10, 25, 50, 100) [50]: ").strip()
        if grid_size_input == "":
            debug_grid_cm = 50  # Valor por defecto
        else:
            debug_grid_cm = int(grid_size_input)
            if debug_grid_cm <= 0:
                debug_grid_cm = 50
                print("⚠️  Valor inválido, usando 50cm por defecto")
    except ValueError:
        debug_grid_cm = 50
        print("⚠️  Valor inválido, usando 50cm por defecto")
    
    print(f"✅ Grilla de debug configurada: {debug_grid_cm}cm")
    print()
    
    print(f"📹 Video: {video_path}")
    print(f"🎯 Objeto: AprilTag de {object_real_cm}cm")
    print(f"📊 Frame: {frame_number}")
    print(f"📐 Grilla: {debug_grid_cm}cm")
    print()
    
    # Paso 1: Extraer frame
    print("🔄 PASO 1: Extraer frame del video")
    print("-" * 40)
    
    try:
        from video_utils import extract_frame, list_video_info
        
        # Mostrar información del video
        print("📊 Información del video:")
        list_video_info(video_path)
        print()
        
        # Extraer frame
        frame_path = extract_frame(video_path, frame_number)
        if not frame_path:
            print("❌ Error extrayendo frame")
            return
        
        print(f"✅ Frame extraído: {frame_path}")
        print()
        
    except ImportError:
        print("❌ Error: No se pudo importar video_utils")
        print("💡 Asegúrate de que opencv-python esté instalado")
        return
    
    # Paso 2: Seleccionar objeto con SAM
    print("🔄 PASO 2: Selección interactiva con SAM")
    print("-" * 40)
    
    try:
        from sam_selector import select_object_from_image
        import cv2
        import numpy as np
        
        print("🎯 Abriendo imagen para selección...")
        print("💡 Haz clic en el AprilTag para seleccionarlo")
        print("💡 Puedes hacer múltiples clics para mejor precisión")
        print()
        
        # Seleccionar objeto
        result = select_object_from_image(frame_path, object_real_cm)
        
        if not result:
            print("❌ Selección cancelada")
            return
        
        print("✅ Objeto seleccionado exitosamente")
        
        # Debug: Mostrar información del resultado
        print("🔍 DEBUG - Información del resultado:")
        print(f"   Método: {result.get('method', 'No especificado')}")
        print(f"   Máscara disponible: {'Sí' if result.get('mask') is not None else 'No'}")
        print(f"   Puntos seleccionados: {len(result.get('points', []))}")
        print(f"   Dimensiones: {result.get('width_px', 0):.1f} x {result.get('height_px', 0):.1f} px")
        if result.get('mask') is not None:
            mask_shape = result['mask'].shape
            mask_sum = np.sum(result['mask'])
            print(f"   Forma de máscara: {mask_shape}")
            print(f"   Píxeles segmentados: {mask_sum}")
        else:
            print("   ⚠️  SAM no está activo. Posibles causas:")
            print("      - No está instalado: pip install segment-anything")
            print("      - Falta checkpoint SAM (descarga de GitHub)")
            print("      - Falta PyTorch: pip install torch torchvision")
        print()
        
        # Generar imagen con segmentación para validación
        if result.get('mask') is not None:
            print("🖼️  Generando imagen de validación...")
            
            # Cargar imagen original
            original_image = cv2.imread(frame_path)
            original_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
            
            # Crear overlay con la máscara
            mask = result['mask']
            
            # Crear imagen de validación con overlay
            validation_image = original_rgb.copy()
            
            # Aplicar color a la máscara (verde semi-transparente)
            mask_color = np.zeros_like(validation_image)
            mask_color[mask] = [0, 255, 0]  # Verde
            
            # Combinar imagen original con máscara
            alpha = 0.4  # Transparencia
            validation_image = cv2.addWeighted(validation_image, 1-alpha, mask_color, alpha, 0)
            
            # Añadir contorno del objeto
            contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                cv2.drawContours(validation_image, contours, -1, (255, 0, 0), 3)  # Contorno rojo
            
            # Marcar puntos de selección
            for i, point in enumerate(result['points']):
                cv2.circle(validation_image, tuple(point), 8, (255, 255, 0), -1)  # Círculos amarillos
                cv2.putText(validation_image, str(i+1), 
                           (point[0]+10, point[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # Generar grilla de debug basada en GSD y tamaño configurado
            print("📐 Generando grilla de referencia...")
            gsd = result['gsd_cm_per_px']
            
            # Usar el tamaño de grilla configurado por el usuario
            grid_cm = debug_grid_cm
            
            # Convertir grilla a píxeles - CORRECCIÓN: usar debug_grid_cm directamente
            grid_px = int(debug_grid_cm / gsd)
            
            print(f"📐 Grilla de referencia: {debug_grid_cm}cm = {grid_px}px")
            print(f"📐 GSD utilizado: {gsd:.6f} cm/px")
            print(f"📐 Verificación: {grid_px}px × {gsd:.6f}cm/px = {grid_px * gsd:.2f}cm")
            
            # Validar que el cálculo sea correcto
            calculated_cm = grid_px * gsd
            if abs(calculated_cm - debug_grid_cm) > 1:  # Permitir 1cm de diferencia por redondeo
                print(f"⚠️  Posible error en cálculo: esperado {debug_grid_cm}cm, calculado {calculated_cm:.2f}cm")
            
            # Validar que la grilla sea visible
            if grid_px < 5:
                print(f"⚠️  Grilla muy pequeña ({grid_px}px), aumentando tamaño...")
                grid_cm = int(5 * gsd) + 5  # Al menos 5px + margen
                grid_px = int(grid_cm / gsd)
                print(f"📐 Grilla ajustada: {grid_cm}cm = {grid_px}px")
            elif grid_px > 500:
                print(f"⚠️  Grilla muy grande ({grid_px}px), reduciendo tamaño...")
                grid_cm = int(500 * gsd)
                grid_px = int(grid_cm / gsd)
                print(f"📐 Grilla ajustada: {grid_cm}cm = {grid_px}px")
            
            # Dibujar grilla
            h, w = validation_image.shape[:2]
            
            # Líneas verticales
            for x in range(0, w, grid_px):
                cv2.line(validation_image, (x, 0), (x, h), (128, 128, 128), 1, cv2.LINE_AA)
                # Etiquetas cada 5 líneas
                if x % (grid_px * 5) == 0 and x > 0:
                    grid_number = x // grid_px
                    distance_cm = grid_number * debug_grid_cm
                    cv2.putText(validation_image, f"{distance_cm}cm", (x + 5, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
            
            # Líneas horizontales
            for y in range(0, h, grid_px):
                cv2.line(validation_image, (0, y), (w, y), (128, 128, 128), 1, cv2.LINE_AA)
                # Etiquetas cada 5 líneas
                if y % (grid_px * 5) == 0 and y > 0:
                    grid_number = y // grid_px
                    distance_cm = grid_number * debug_grid_cm
                    cv2.putText(validation_image, f"{distance_cm}cm", (5, y - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
            
            # Añadir líneas principales más gruesas cada metro
            meter_px = int(100 / gsd)  # 1 metro en píxeles
            if meter_px > 50:  # Solo si es visible
                for x in range(0, w, meter_px):
                    cv2.line(validation_image, (x, 0), (x, h), (64, 64, 64), 2, cv2.LINE_AA)
                for y in range(0, h, meter_px):
                    cv2.line(validation_image, (0, y), (w, y), (64, 64, 64), 2, cv2.LINE_AA)
            
            # Añadir información de medición actualizada
            x, y, w_obj, h_obj = cv2.boundingRect(contours[0]) if contours else (0, 0, 0, 0)
            info_text = [
                f"Objeto: {object_real_cm}cm",
                f"Pixeles: {result['width_px']:.1f}x{result['height_px']:.1f}",
                f"GSD: {result['gsd_cm_per_px']:.6f} cm/px",
                f"Metodo: {result['method']}",
                f"Grilla: {debug_grid_cm}cm ({grid_px}px)",
                f"Escala: 1px = {gsd:.3f}cm",
                f"Config: Usuario={debug_grid_cm}cm"
            ]
            
            for i, text in enumerate(info_text):
                y_pos = 30 + i*22
                cv2.putText(validation_image, text, (10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(validation_image, text, (10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            
            # Guardar imagen de validación
            validation_path = frame_path.replace('.jpg', '_segmented_with_grid.jpg')
            validation_bgr = cv2.cvtColor(validation_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(validation_path, validation_bgr)
            
            print(f"✅ Imagen de validación guardada: {validation_path}")
            print("💡 Revisa la imagen para verificar que la segmentación sea correcta")
            print("   - Área verde: objeto segmentado")
            print("   - Contorno rojo: borde del objeto")
            print("   - Círculos amarillos: puntos de selección")
            print("   - Grilla gris: referencia de medición")
            print(f"   - Cada cuadro de grilla = {debug_grid_cm}cm x {debug_grid_cm}cm")
            print(f"   - Configurado por usuario: {debug_grid_cm}cm")
            print(f"   - Líneas gruesas cada metro (si es visible)")
            
            # También generar imagen solo con grilla para referencia
            grid_only_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
            
            # Dibujar solo la grilla en imagen limpia
            for x in range(0, w, grid_px):
                cv2.line(grid_only_image, (x, 0), (x, h), (0, 255, 0), 1, cv2.LINE_AA)
            for y in range(0, h, grid_px):
                cv2.line(grid_only_image, (0, y), (w, y), (0, 255, 0), 1, cv2.LINE_AA)
            
            # Líneas principales cada metro
            if meter_px > 50:
                for x in range(0, w, meter_px):
                    cv2.line(grid_only_image, (x, 0), (x, h), (0, 200, 0), 2, cv2.LINE_AA)
                for y in range(0, h, meter_px):
                    cv2.line(grid_only_image, (0, y), (w, y), (0, 200, 0), 2, cv2.LINE_AA)
            
            # Guardar imagen solo con grilla
            grid_path = frame_path.replace('.jpg', '_grid_reference.jpg')
            grid_bgr = cv2.cvtColor(grid_only_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(grid_path, grid_bgr)
            
            print(f"✅ Imagen de grilla de referencia: {grid_path}")
            print(f"   - Úsala para validar mediciones manualmente")
        else:
            print("ℹ️  No hay máscara disponible (modo manual)")
            print("🖼️  Generando imagen de validación con puntos...")
            
            # Generar imagen de validación solo con puntos para modo manual
            original_image = cv2.imread(frame_path)
            original_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
            validation_image = original_rgb.copy()
            
            # Marcar puntos de selección si existen
            if result.get('points'):
                for i, point in enumerate(result['points']):
                    cv2.circle(validation_image, tuple(point), 12, (255, 255, 0), -1)  # Círculos amarillos más grandes
                    cv2.circle(validation_image, tuple(point), 15, (255, 0, 0), 3)     # Borde rojo
                    cv2.putText(validation_image, str(i+1), 
                               (point[0]+20, point[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
                    cv2.putText(validation_image, str(i+1), 
                               (point[0]+20, point[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
            
            # Añadir información de medición
            info_text = [
                f"Objeto: {object_real_cm}cm",
                f"Pixeles: {result['width_px']:.1f}x{result['height_px']:.1f}",
                f"GSD: {result['gsd_cm_per_px']:.4f} cm/px",
                f"Metodo: {result['method']} (sin mascara)"
            ]
            
            for i, text in enumerate(info_text):
                cv2.putText(validation_image, text, (10, 30 + i*30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 3)
                cv2.putText(validation_image, text, (10, 30 + i*30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            
            # Guardar imagen de validación
            validation_path = frame_path.replace('.jpg', '_manual_points.jpg')
            validation_bgr = cv2.cvtColor(validation_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(validation_path, validation_bgr)
            
            print(f"✅ Imagen de validación guardada: {validation_path}")
            print("💡 Revisa la imagen para verificar los puntos de selección")
            print("   - Círculos amarillos con borde rojo: puntos seleccionados")
        
        print()
        
    except ImportError:
        print("❌ Error: SAM no está disponible")
        print("💡 Para usar SAM, instala:")
        print("   pip install segment-anything-py torch torchvision")
        print()
        print("🔄 Continuando con medición manual...")
        
        # Fallback a medición manual
        try:
            object_pixels = float(input("Ingresa el tamaño del objeto en píxeles: "))
            result = {
                'width_px': object_pixels,
                'height_px': object_pixels,
                'gsd_cm_per_px': object_real_cm / object_pixels,
                'method': 'Manual'
            }
        except ValueError:
            print("❌ Error en medición manual")
            return
    
    # Paso 3: Calcular altura y validar GSD
    print("🔄 PASO 3: Calcular altura y validar GSD")
    print("-" * 40)
    
    try:
        from altura_calculator import create_calculator, display_results
        
        # Mostrar GSD calculado y validar fórmula
        gsd_calculated = result['gsd_cm_per_px']
        print(f"📐 GSD calculado por SAM: {gsd_calculated:.6f} cm/px")
        print(f"📐 Precisión: {gsd_calculated * 10:.3f} mm/px")
        
        # Para validación, mostrar la fórmula teórica del GSD
        print()
        print("💡 Recordatorio - Fórmula teórica del GSD:")
        print("   GSD = (sensor_width_mm * height_cm) / (focal_length_mm * image_width_px)")
        print(f"   Donde height_cm sería la altura de vuelo calculada")
        print()
        
        # Crear calculadora
        calculator = create_calculator("DJI Mini 3 Pro")
        
        # Calcular altura
        height_results = calculator.calculate_height_from_reference(
            object_real_cm=object_real_cm,
            object_pixels=max(result['width_px'], result['height_px'])
        )
        
        # Mostrar resultados
        display_results(height_results)
        print()
        
    except Exception as e:
        print(f"❌ Error calculando altura: {e}")
        return
    
    # Paso 4: Generar parámetros para API
    print("🔄 PASO 4: Parámetros para API")
    print("-" * 40)
    
    try:
        gsd = result['gsd_cm_per_px']
        api_params = calculator.get_api_parameters(gsd)
        
        print("🔧 Parámetros para VideoPredictionRequest:")
        for key, value in api_params.items():
            print(f"   {key}: {value}")
        
        print()
        print("💡 Uso en tu código:")
        print("```python")
        print("from api.schemas import VideoPredictionRequest")
        print()
        print("request = VideoPredictionRequest(")
        print(f"    video='{video_path}',")
        print(f"    altitude={api_params['altitude']},")
        print(f"    focal_length={api_params.get('focal_length')},")
        print(f"    sensor_width={api_params['sensor_width']},")
        print(f"    debug_grid_cm={api_params['debug_grid_cm']}")
        print(")")
        print("```")
        
    except Exception as e:
        print(f"❌ Error generando parámetros API: {e}")
        return
    
    print()
    print("✅ ¡Proceso completado exitosamente!")
    print("🎯 Ahora puedes usar los parámetros generados en tu API")


if __name__ == "__main__":
    main() 