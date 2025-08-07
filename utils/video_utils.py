"""
Utilidades para extraer frames de video para uso con SAM.
"""

import cv2
import os
from typing import List, Optional
import argparse


def extract_frame(video_path: str, frame_number: int = 0, output_path: Optional[str] = None) -> Optional[str]:
    """
    Extraer un frame específico de un video.
    
    Args:
        video_path: Ruta al video
        frame_number: Número de frame (0 = primer frame)
        output_path: Ruta de salida (opcional)
        
    Returns:
        str: Ruta del frame extraído o None si falla
    """
    try:
        # Abrir video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ No se pudo abrir el video: {video_path}")
            return None
        
        # Obtener información del video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        print(f"📹 Video: {total_frames} frames, {fps:.1f} fps, {duration:.1f}s")
        
        # Validar frame number
        if frame_number >= total_frames:
            print(f"❌ Frame {frame_number} no existe. Máximo: {total_frames - 1}")
            cap.release()
            return None
        
        # Ir al frame específico
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        
        if not ret:
            print(f"❌ No se pudo leer el frame {frame_number}")
            cap.release()
            return None
        
        # Generar ruta de salida si no se especifica
        if output_path is None:
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = f"{video_name}_frame_{frame_number:04d}.jpg"
        
        # Guardar frame
        cv2.imwrite(output_path, frame)
        cap.release()
        
        print(f"✅ Frame extraído: {output_path}")
        print(f"   Tiempo: {frame_number / fps:.1f}s")
        print(f"   Resolución: {frame.shape[1]}x{frame.shape[0]}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error extrayendo frame: {e}")
        return None


def extract_frame_by_time(video_path: str, time_seconds: float, output_path: Optional[str] = None) -> Optional[str]:
    """
    Extraer frame por tiempo en segundos.
    
    Args:
        video_path: Ruta al video
        time_seconds: Tiempo en segundos
        output_path: Ruta de salida (opcional)
        
    Returns:
        str: Ruta del frame extraído o None si falla
    """
    try:
        # Abrir video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ No se pudo abrir el video: {video_path}")
            return None
        
        # Obtener FPS
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            print("❌ No se pudo obtener FPS del video")
            cap.release()
            return None
        
        # Calcular frame number
        frame_number = int(time_seconds * fps)
        
        # Extraer frame
        result = extract_frame(video_path, frame_number, output_path)
        cap.release()
        
        return result
        
    except Exception as e:
        print(f"❌ Error extrayendo frame por tiempo: {e}")
        return None


def list_video_info(video_path: str):
    """
    Mostrar información detallada de un video.
    
    Args:
        video_path: Ruta al video
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ No se pudo abrir el video: {video_path}")
            return
        
        # Obtener información
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        print(f"📹 INFORMACIÓN DEL VIDEO")
        print(f"=" * 40)
        print(f"📁 Archivo: {os.path.basename(video_path)}")
        print(f"📐 Resolución: {width}x{height}")
        print(f"🎬 FPS: {fps:.2f}")
        print(f"📊 Frames totales: {total_frames}")
        print(f"⏱️  Duración: {duration:.2f} segundos")
        print(f"📅 Tiempo: {duration/60:.1f} minutos")
        
        # Sugerir frames útiles
        print(f"\n💡 Frames sugeridos:")
        print(f"   Frame 0: Inicio del video")
        if total_frames > 1:
            print(f"   Frame {total_frames//4}: 25% del video")
            print(f"   Frame {total_frames//2}: 50% del video")
            print(f"   Frame {3*total_frames//4}: 75% del video")
            print(f"   Frame {total_frames-1}: Final del video")
        
        cap.release()
        
    except Exception as e:
        print(f"❌ Error obteniendo información: {e}")


def main():
    """Función principal para uso desde línea de comandos."""
    parser = argparse.ArgumentParser(description='Extraer frames de video para uso con SAM')
    parser.add_argument('video', help='Ruta al video')
    parser.add_argument('--frame', type=int, default=0, help='Número de frame (default: 0)')
    parser.add_argument('--time', type=float, help='Tiempo en segundos (alternativa a --frame)')
    parser.add_argument('--output', help='Ruta de salida (opcional)')
    parser.add_argument('--info', action='store_true', help='Mostrar información del video')
    
    args = parser.parse_args()
    
    if args.info:
        list_video_info(args.video)
        return
    
    if args.time is not None:
        # Extraer por tiempo
        result = extract_frame_by_time(args.video, args.time, args.output)
    else:
        # Extraer por frame number
        result = extract_frame(args.video, args.frame, args.output)
    
    if result:
        print(f"\n🎯 Frame listo para usar con SAM:")
        print(f"   python calcular_altura_rapido.py --objeto 15.0 --imagen {result}")


if __name__ == "__main__":
    main() 