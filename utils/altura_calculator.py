"""
Calculadora de Altura por Objeto de Referencia

Este módulo permite calcular la altura a la que se grabó un video basándose en 
objetos de referencia del cual se conocen sus dimensiones reales.

Concepto:
- GSD = objeto_real_cm / objeto_pixels
- Altura = (GSD × focal_length_mm × image_width) / sensor_width_mm (método tradicional)
- Altura = (GSD × image_width) / (2 × tan(FOV/2)) (método FOV)

Autor: Sistema de Ganadería
Fecha: 2025
"""

import numpy as np
import math
import cv2
from typing import Dict, List, Tuple, Optional, Union
import matplotlib.pyplot as plt
from dataclasses import dataclass


@dataclass
class CameraConfig:
    """Configuración de cámara para cálculos de altura."""
    image_width: int = 3840
    image_height: int = 2160
    focal_length_mm: Optional[float] = None
    sensor_width_mm: Optional[float] = None
    fov_degrees: Optional[float] = None
    camera_model: str = "Unknown"
    
    def __post_init__(self):
        """Validar configuración de cámara."""
        if self.focal_length_mm is None and self.sensor_width_mm is None and self.fov_degrees is None:
            raise ValueError("Debe proporcionar al menos focal_length + sensor_width O fov_degrees")


@dataclass
class ReferenceObject:
    """Objeto de referencia para cálculos de altura."""
    name: str
    real_length_cm: float
    real_width_cm: float
    pixels_length: float
    pixels_width: float
    position: str = "Unknown"
    
    @property
    def real_average_cm(self) -> float:
        """Promedio de dimensiones reales."""
        return (self.real_length_cm + self.real_width_cm) / 2
    
    @property
    def pixels_average(self) -> float:
        """Promedio de dimensiones en píxeles."""
        return (self.pixels_length + self.pixels_width) / 2


class AlturaCalculator:
    """
    Calculadora principal para determinar altura de video usando objetos de referencia.
    """
    
    def __init__(self, camera_config: CameraConfig):
        """
        Inicializar calculadora con configuración de cámara.
        
        Args:
            camera_config: Configuración de la cámara
        """
        self.camera_config = camera_config
    
    def calculate_gsd_from_reference(self, object_real_cm: float, object_pixels: float) -> float:
        """
        Calcula el GSD basándose en un objeto de referencia.
        
        Args:
            object_real_cm: Tamaño real del objeto en centímetros
            object_pixels: Tamaño del objeto en píxeles
            
        Returns:
            float: GSD en cm/px
        """
        if object_pixels <= 0:
            raise ValueError("El tamaño en píxeles debe ser mayor que 0")
        
        return object_real_cm / object_pixels
    
    def calculate_height_from_gsd_traditional(
        self, 
        gsd: float, 
        image_width: Optional[int] = None,
        focal_length_mm: Optional[float] = None,
        sensor_width_mm: Optional[float] = None
    ) -> float:
        """
        Calcula la altura usando el método tradicional (focal length + sensor).
        
        Args:
            gsd: Ground Sample Distance en cm/px
            image_width: Ancho de la imagen en píxeles (usa configuración por defecto)
            focal_length_mm: Focal length en milímetros (usa configuración por defecto)
            sensor_width_mm: Ancho del sensor en milímetros (usa configuración por defecto)
            
        Returns:
            float: Altura en centímetros
        """
        if focal_length_mm is None:
            focal_length_mm = self.camera_config.focal_length_mm
        if sensor_width_mm is None:
            sensor_width_mm = self.camera_config.sensor_width_mm
        if image_width is None:
            image_width = self.camera_config.image_width
            
        if focal_length_mm is None or sensor_width_mm is None:
            raise ValueError("Se requieren focal_length_mm y sensor_width_mm para método tradicional")
        
        return (gsd * focal_length_mm * image_width) / sensor_width_mm
    
    def calculate_height_from_gsd_fov(
        self, 
        gsd: float, 
        image_width: Optional[int] = None,
        fov_degrees: Optional[float] = None
    ) -> float:
        """
        Calcula la altura usando el método FOV.
        
        Args:
            gsd: Ground Sample Distance en cm/px
            image_width: Ancho de la imagen en píxeles (usa configuración por defecto)
            fov_degrees: Campo de visión horizontal en grados (usa configuración por defecto)
            
        Returns:
            float: Altura en centímetros
        """
        if fov_degrees is None:
            fov_degrees = self.camera_config.fov_degrees
        if image_width is None:
            image_width = self.camera_config.image_width
            
        if fov_degrees is None:
            raise ValueError("Se requiere fov_degrees para método FOV")
        
        fov_radians = math.radians(fov_degrees)
        return (gsd * image_width) / (2 * math.tan(fov_radians / 2))
    
    def calculate_height_from_reference(
        self,
        object_real_cm: float,
        object_pixels: float,
        image_width: Optional[int] = None
    ) -> Dict:
        """
        Calcula la altura del video usando un objeto de referencia.
        
        Args:
            object_real_cm: Tamaño real del objeto en centímetros
            object_pixels: Tamaño del objeto en píxeles
            image_width: Ancho de la imagen en píxeles (usa configuración por defecto)
            
        Returns:
            dict: Resultados del cálculo
        """
        if image_width is None:
            image_width = self.camera_config.image_width
        
        # Calcular GSD
        gsd = self.calculate_gsd_from_reference(object_real_cm, object_pixels)
        
        results = {
            'gsd_cm_per_px': gsd,
            'gsd_mm_per_px': gsd * 10,
            'object_real_cm': object_real_cm,
            'object_pixels': object_pixels,
            'image_width': image_width,
            'camera_model': self.camera_config.camera_model
        }
        
        # Calcular altura con método tradicional si hay parámetros
        if self.camera_config.focal_length_mm and self.camera_config.sensor_width_mm:
            try:
                height_traditional = self.calculate_height_from_gsd_traditional(gsd, image_width)
                results['height_traditional_cm'] = height_traditional
                results['height_traditional_m'] = height_traditional / 100
            except ValueError as e:
                results['error_traditional'] = str(e)
        
        # Calcular altura con método FOV si está disponible
        if self.camera_config.fov_degrees:
            try:
                height_fov = self.calculate_height_from_gsd_fov(gsd, image_width)
                results['height_fov_cm'] = height_fov
                results['height_fov_m'] = height_fov / 100
            except ValueError as e:
                results['error_fov'] = str(e)
        
        # Comparar métodos si ambos están disponibles
        if 'height_traditional_cm' in results and 'height_fov_cm' in results:
            diff_pct = abs(results['height_fov_cm'] - results['height_traditional_cm']) / results['height_traditional_cm'] * 100
            results['difference_percent'] = diff_pct
            results['methods_agree'] = diff_pct < 5
        
        return results
    
    def validate_multiple_objects(self, reference_objects: List[ReferenceObject]) -> Dict:
        """
        Valida el cálculo con múltiples objetos de referencia.
        
        Args:
            reference_objects: Lista de objetos de referencia
            
        Returns:
            dict: Estadísticas de validación
        """
        if len(reference_objects) < 2:
            raise ValueError("Se requieren al menos 2 objetos para validación")
        
        heights_traditional = []
        heights_fov = []
        gsds = []
        object_results = []
        
        for obj in reference_objects:
            gsd = self.calculate_gsd_from_reference(obj.real_average_cm, obj.pixels_average)
            gsds.append(gsd)
            
            result = self.calculate_height_from_reference(
                obj.real_average_cm, obj.pixels_average
            )
            result['object_name'] = obj.name
            result['object_position'] = obj.position
            object_results.append(result)
            
            if 'height_traditional_cm' in result:
                heights_traditional.append(result['height_traditional_cm'])
            
            if 'height_fov_cm' in result:
                heights_fov.append(result['height_fov_cm'])
        
        # Calcular estadísticas
        stats = {
            'num_objects': len(reference_objects),
            'gsd_mean': np.mean(gsds),
            'gsd_std': np.std(gsds),
            'gsd_cv': (np.std(gsds) / np.mean(gsds)) * 100 if len(gsds) > 1 else 0,
            'object_results': object_results
        }
        
        if heights_traditional:
            stats['height_traditional_mean'] = np.mean(heights_traditional)
            stats['height_traditional_std'] = np.std(heights_traditional)
            stats['height_traditional_cv'] = (np.std(heights_traditional) / np.mean(heights_traditional)) * 100
        
        if heights_fov:
            stats['height_fov_mean'] = np.mean(heights_fov)
            stats['height_fov_std'] = np.std(heights_fov)
            stats['height_fov_cv'] = (np.std(heights_fov) / np.mean(heights_fov)) * 100
        
        return stats
    
    def analyze_sensitivity(
        self,
        object_real_cm: float,
        object_pixels: float,
        pixel_errors: List[int] = None
    ) -> Dict:
        """
        Analiza la sensibilidad del cálculo a errores en la medición.
        
        Args:
            object_real_cm: Tamaño real del objeto en centímetros
            object_pixels: Tamaño del objeto en píxeles
            pixel_errors: Lista de errores en píxeles a probar
            
        Returns:
            dict: Resultados del análisis de sensibilidad
        """
        if pixel_errors is None:
            pixel_errors = [-5, -2, -1, 0, 1, 2, 5]
        
        base_results = self.calculate_height_from_reference(object_real_cm, object_pixels)
        sensitivity_results = []
        
        for error in pixel_errors:
            new_pixels = object_pixels + error
            
            if new_pixels <= 0:
                continue
            
            try:
                results = self.calculate_height_from_reference(object_real_cm, new_pixels)
                results['pixel_error'] = error
                results['new_pixels'] = new_pixels
                
                # Calcular diferencias porcentuales
                if 'height_traditional_cm' in base_results and 'height_traditional_cm' in results:
                    diff_trad = abs(results['height_traditional_cm'] - base_results['height_traditional_cm']) / base_results['height_traditional_cm'] * 100
                    results['diff_traditional_percent'] = diff_trad
                
                if 'height_fov_cm' in base_results and 'height_fov_cm' in results:
                    diff_fov = abs(results['height_fov_cm'] - base_results['height_fov_cm']) / base_results['height_fov_cm'] * 100
                    results['diff_fov_percent'] = diff_fov
                
                sensitivity_results.append(results)
                
            except ValueError:
                continue
        
        return {
            'base_results': base_results,
            'sensitivity_results': sensitivity_results,
            'pixel_errors_tested': pixel_errors
        }
    
    def calculate_debug_grid_cm(self, gsd: float, grid_size_cm: int = 50) -> Dict:
        """
        Calcula el debug_grid_cm para usar con la API.
        
        Args:
            gsd: Ground Sample Distance en cm/px
            grid_size_cm: Tamaño de la grilla en centímetros
            
        Returns:
            dict: Parámetros para la API
        """
        box_size_px = grid_size_cm / gsd
        
        return {
            'debug_grid_cm': grid_size_cm,
            'box_size_px': box_size_px,
            'gsd_cm_per_px': gsd,
            'explanation': f"Grilla de {grid_size_cm}cm cada {box_size_px:.1f} píxeles"
        }
    
    def get_api_parameters(self, gsd: float) -> Dict:
        """
        Obtiene todos los parámetros necesarios para la API.
        
        Args:
            gsd: Ground Sample Distance en cm/px
            
        Returns:
            dict: Parámetros para VideoPredictionRequest
        """
        # Calcular altura usando el método disponible
        if self.camera_config.focal_length_mm and self.camera_config.sensor_width_mm:
            height_cm = self.calculate_height_from_gsd_traditional(gsd)
        elif self.camera_config.fov_degrees:
            height_cm = self.calculate_height_from_gsd_fov(gsd)
        else:
            raise ValueError("No hay suficientes parámetros de cámara para calcular altura")
        
        api_params = {
            'altitude': int(height_cm),
            'sensor_width': self.camera_config.sensor_width_mm,
            'debug_grid_cm': 50  # Grilla de 50cm por defecto
        }
        
        if self.camera_config.focal_length_mm:
            api_params['focal_length'] = self.camera_config.focal_length_mm
        
        if self.camera_config.fov_degrees:
            api_params['focal_length_35mm'] = self._calculate_focal_length_35mm()
        
        return api_params
    
    def _calculate_focal_length_35mm(self) -> float:
        """Calcula el focal length equivalente en 35mm."""
        if self.camera_config.focal_length_mm and self.camera_config.sensor_width_mm:
            # Sensor 35mm tiene 36mm de ancho
            return (self.camera_config.focal_length_mm * 36) / self.camera_config.sensor_width_mm
        return None


def display_results(results: Dict) -> None:
    """
    Muestra los resultados de forma clara y organizada.
    
    Args:
        results: Resultados del cálculo de altura
    """
    print("🔍 RESULTADOS DEL CÁLCULO")
    print("=" * 50)
    print(f"📐 GSD calculado: {results['gsd_cm_per_px']:.4f} cm/px")
    print(f"📏 Precisión: {results['gsd_mm_per_px']:.2f} mm/px")
    print(f"🎯 Objeto referencia: {results['object_real_cm']} cm = {results['object_pixels']} px")
    print(f"🖼️  Ancho imagen: {results['image_width']} px")
    print(f"📷 Cámara: {results.get('camera_model', 'Unknown')}")
    print()
    
    if 'height_traditional_cm' in results:
        print(f"📊 Altura (Método Tradicional): {results['height_traditional_m']:.2f} m ({results['height_traditional_cm']:.1f} cm)")
    
    if 'height_fov_cm' in results:
        print(f"📊 Altura (Método FOV): {results['height_fov_m']:.2f} m ({results['height_fov_cm']:.1f} cm)")
    
    if 'difference_percent' in results:
        print(f"\n🔍 Comparación de métodos:")
        print(f"   Diferencia: {results['difference_percent']:.1f}%")
        if results['methods_agree']:
            print("   ✅ Los métodos están de acuerdo (diferencia < 5%)")
        else:
            print("   ⚠️  Los métodos difieren significativamente")
    
    if 'error_traditional' in results:
        print(f"❌ Error método tradicional: {results['error_traditional']}")
    
    if 'error_fov' in results:
        print(f"❌ Error método FOV: {results['error_fov']}")
    
    print("=" * 50)


def display_validation_stats(stats: Dict) -> None:
    """
    Muestra estadísticas de validación con múltiples objetos.
    
    Args:
        stats: Estadísticas de validación
    """
    print("🔍 VALIDACIÓN CON MÚLTIPLES OBJETOS")
    print("=" * 60)
    print(f"📊 Número de objetos: {stats['num_objects']}")
    print(f"📐 GSD promedio: {stats['gsd_mean']:.4f} ± {stats['gsd_std']:.4f} cm/px")
    print(f"🎯 Precisión (CV GSD): {stats['gsd_cv']:.1f}%")
    
    if stats['gsd_cv'] < 5:
        print("   ✅ Excelente precisión")
    elif stats['gsd_cv'] < 10:
        print("   ✅ Buena precisión")
    else:
        print("   ⚠️  Precisión moderada - revisar mediciones")
    
    if 'height_traditional_mean' in stats:
        print(f"\n📊 Altura promedio (Trad): {stats['height_traditional_mean']/100:.2f} ± {stats['height_traditional_std']/100:.2f} m")
        print(f"   CV: {stats['height_traditional_cv']:.1f}%")
    
    if 'height_fov_mean' in stats:
        print(f"📊 Altura promedio (FOV): {stats['height_fov_mean']/100:.2f} ± {stats['height_fov_std']/100:.2f} m")
        print(f"   CV: {stats['height_fov_cv']:.1f}%")
    
    print("\n📋 Detalles por objeto:")
    for result in stats['object_results']:
        print(f"   {result['object_name']} ({result['object_position']}):")
        print(f"      GSD: {result['gsd_cm_per_px']:.4f} cm/px")
        if 'height_traditional_m' in result:
            print(f"      Altura (Trad): {result['height_traditional_m']:.2f} m")
        if 'height_fov_m' in result:
            print(f"      Altura (FOV): {result['height_fov_m']:.2f} m")
    
    print("=" * 60)


# Configuraciones predefinidas de cámaras comunes
CAMERA_CONFIGS = {
    "DJI Mini 3 Pro": CameraConfig(
        image_width=3840,
        image_height=2160,
        focal_length_mm=6.72,
        sensor_width_mm=9.65,
        fov_degrees=None,  # No verificado en especificaciones oficiales
        camera_model="DJI Mini 3 Pro"
    ),
    "DJI Mini SE2": CameraConfig(
        image_width=2704,
        image_height=1520,
        focal_length_mm=4.49,
        sensor_width_mm=6.34,
        fov_degrees=None,  # No verificado
        camera_model="DJI Mini SE2"
    ),
    "Go Pro 12": CameraConfig(
        image_width=3840,
        image_height=2160,
        focal_length_mm=35.0,
        sensor_width_mm=None,  # No especificado en config.json
        fov_degrees=None,
        camera_model="Go Pro 12"
    ),
    "iPhone 14": CameraConfig(
        image_width=3840,
        image_height=2160,
        focal_length_mm=26.0,
        sensor_width_mm=None,  # No especificado en config.json
        fov_degrees=None,
        camera_model="iPhone 14"
    )
}


def create_calculator(camera_model: str = "DJI Mini 3 Pro") -> AlturaCalculator:
    """
    Crea una calculadora con configuración predefinida.
    
    Args:
        camera_model: Modelo de cámara predefinido
        
    Returns:
        AlturaCalculator: Calculadora configurada
    """
    if camera_model not in CAMERA_CONFIGS:
        raise ValueError(f"Modelo de cámara no encontrado. Opciones: {list(CAMERA_CONFIGS.keys())}")
    
    return AlturaCalculator(CAMERA_CONFIGS[camera_model])


# Ejemplo de uso
if __name__ == "__main__":
    # Crear calculadora con DJI Mini 3 Pro
    calculator = create_calculator("DJI Mini 3 Pro")
    
    # Ejemplo: AprilTag de 15cm medido en 43.4 píxeles
    results = calculator.calculate_height_from_reference(
        object_real_cm=15.0,
        object_pixels=43.4
    )
    
    # Mostrar resultados
    display_results(results)
    
    # Calcular parámetros para API
    if 'gsd_cm_per_px' in results:
        api_params = calculator.get_api_parameters(results['gsd_cm_per_px'])
        print("\n🔧 PARÁMETROS PARA LA API:")
        print(f"   altitude: {api_params['altitude']}")
        print(f"   focal_length: {api_params.get('focal_length')}")
        print(f"   sensor_width: {api_params['sensor_width']}")
        print(f"   debug_grid_cm: {api_params['debug_grid_cm']}")
        
        # Mostrar diferentes tamaños de grilla
        print("\n📏 Diferentes tamaños de grilla:")
        for grid_cm in [25, 50, 100, 200]:
            grid_params = calculator.calculate_debug_grid_cm(results['gsd_cm_per_px'], grid_cm)
            print(f"   {grid_cm}cm → {grid_params['box_size_px']:.1f} px") 