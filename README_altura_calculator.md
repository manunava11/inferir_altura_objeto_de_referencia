# Calculadora de Altura por Objeto de Referencia

Este conjunto de scripts te permite calcular la altura a la que se grabó un video basándose en objetos de referencia del cual conoces sus dimensiones reales.

## 📁 Archivos

- `utils/altura_calculator.py` - Módulo principal con todas las funciones
- `utils/sam_selector.py` - Selección interactiva de objetos usando SAM
- `utils/video_utils.py` - Utilidades para extraer frames de video
- `calcular_altura_local.py` - Script interactivo completo
- `calcular_altura_rapido.py` - Script rápido con parámetros de línea de comandos

## 🚀 Uso Rápido

### Opción 1: Script Interactivo (Recomendado para principiantes)

```bash
python calcular_altura_local.py
```

El script te guiará paso a paso:
1. Seleccionar tu cámara
2. Ingresar datos del objeto de referencia
3. Ver resultados y opciones adicionales

### Opción 2: Script Rápido (Para usuarios avanzados)

```bash
# Ejemplo básico
python calcular_altura_rapido.py --objeto 15.0 --pixels 43.4

# Con cámara específica
python calcular_altura_rapido.py --camera "DJI Mini SE2" --objeto 15.0 --pixels 43.4

# Con selección interactiva SAM
python calcular_altura_rapido.py --objeto 15.0 --imagen "frame.jpg"

# Con checkpoint SAM personalizado
python calcular_altura_rapido.py --objeto 15.0 --imagen "frame.jpg" --sam-checkpoint "sam_vit_h_4b8939.pth"
```

## 📷 Cámaras Soportadas

### Predefinidas (basadas en etl/config.json):
- **DJI Mini 3 Pro**: focal=6.72mm, sensor=9.65mm ✅ Verificado
- **DJI Mini SE2**: focal=4.49mm, sensor=6.34mm ✅ Verificado
- **Go Pro 12**: focal=35mm (sensor no especificado)
- **iPhone 14**: focal=26mm (sensor no especificado)

⚠️ **Nota**: Los valores de FOV no están verificados en especificaciones oficiales, por lo que el script usa principalmente el método tradicional (focal + sensor).

### Personalizada:
Puedes configurar cualquier cámara con tus propios parámetros.

## 🎯 Objetos de Referencia

### Ejemplos comunes:
- **AprilTag 36h11**: 15.0 × 15.0 cm
- **Caja de cartón**: 30.0 × 20.0 cm
- **Baldosa**: 30.0 × 30.0 cm
- **Marcador en suelo**: 50.0 × 10.0 cm

### Cómo medir en píxeles:
1. **Selección interactiva con SAM** (recomendado): Haz clic en el objeto
2. **Software de edición**: Photoshop, GIMP, etc.
3. **Herramientas de medición**: En reproductores de video
4. **Programáticamente**: Usando OpenCV
5. **Función debug_grid_cm**: De la API existente

## 📐 Fórmulas Utilizadas

```python
# GSD = objeto_real_cm / objeto_pixels
# Altura = (GSD × focal_length_mm × image_width) / sensor_width_mm (método tradicional)
# Altura = (GSD × image_width) / (2 × tan(FOV/2)) (método FOV)
```

## 🔧 Integración con la API

Los scripts generan parámetros listos para usar con tu API:

```python
# Ejemplo de salida
altitude: 990
debug_grid_cm: 50
focal_length: 6.72
sensor_width: 9.65
```

Uso en VideoPredictionRequest:
```python
request = VideoPredictionRequest(
    video="tu_video.mp4",
    altitude=990,  # Altura calculada
    focal_length=6.72,
    sensor_width=9.65,
    debug_grid_cm=50,  # Grilla de 50cm
    # ... otros parámetros
)
```

## 📊 Ejemplo Completo

### Entrada:
- **Cámara**: DJI Mini 3 Pro
- **Objeto**: AprilTag de 15.0 cm
- **Medición**: 43.4 píxeles

### Cálculo:
```
GSD = 15.0 cm / 43.4 px = 0.3456 cm/px
Altura = 9.9 metros
```

### Salida:
```
🔍 RESULTADOS DEL CÁLCULO
==================================================
📐 GSD calculado: 0.3456 cm/px
📏 Precisión: 3.46 mm/px
🎯 Objeto referencia: 15.0 cm = 43.4 px
🖼️  Ancho imagen: 3840 px
📷 Cámara: DJI Mini 3 Pro

📊 Altura (Método Tradicional): 9.90 m (990.1 cm)

🔧 PARÁMETROS PARA LA API
   altitude: 990
   debug_grid_cm: 50
   focal_length: 6.72
   sensor_width: 9.65
```

## 🎯 Ejemplo con SAM

### Paso 1: Extraer frame del video
```bash
python utils/video_utils.py video.mp4 --info
# Salida: 1000 frames, 30.0 fps, 33.3s

python utils/video_utils.py video.mp4 --frame 500 --output frame.jpg
# Extrae frame del medio del video
```

### Paso 2: Calcular altura con selección interactiva
```bash
python calcular_altura_rapido.py --objeto 15.0 --imagen frame.jpg
```

### Interfaz SAM:
1. Se abre la imagen
2. Haz clic en el AprilTag
3. SAM segmenta automáticamente el objeto
4. Se calcula el GSD y la altura

### Resultado:
```
🎯 Punto 1: (1200, 800) - Score: 0.987
📐 RESULTADO DE MEDICIÓN
========================================
🎯 Método: SAM mask
📏 Dimensiones: 43.2 x 43.2 px
📐 Área: 1866.2 px²
🎯 Objeto real: 15.0 cm
📐 GSD calculado: 0.3472 cm/px
📏 Precisión: 3.47 mm/px

🔍 RESULTADOS DEL CÁLCULO
==================================================
📐 GSD calculado: 0.3472 cm/px
📊 Altura: 9.85 m (985.2 cm)
```

## ⚠️ Limitaciones y Recomendaciones

### Limitaciones:
- Requiere objetos de referencia en el video
- Sensible a errores de medición en píxeles
- Objetos muy pequeños pueden dar baja precisión

### Mejores prácticas:
1. **Usar objetos grandes** (>10cm) para mayor precisión
2. **Medir con precisión** (±1 píxel)
3. **Validar con múltiples objetos** en diferentes posiciones
4. **Usar objetos cuadrados** cuando sea posible
5. **Evitar objetos en los bordes** de la imagen (distorsión)

## 🎯 Selección Interactiva con SAM

### ¿Qué es SAM?
**SAM (Segment Anything Model)** es un modelo de IA que permite seleccionar objetos en imágenes simplemente haciendo clic. Esto hace que la medición de objetos sea mucho más fácil y precisa.

### Ventajas de usar SAM:
- ✅ **Selección con un clic**: No necesitas medir manualmente
- ✅ **Precisión automática**: El modelo detecta los bordes del objeto
- ✅ **Funciona con cualquier objeto**: AprilTags, cajas, marcadores, etc.
- ✅ **Múltiples clics**: Mejora la precisión con más puntos

### Instalación de SAM:
```bash
# Instalar dependencias
pip install segment-anything-py torch torchvision

# Descargar modelo SAM (opcional - se descarga automáticamente)
# https://github.com/facebookresearch/segment-anything
```

### Uso con SAM:
```bash
# Extraer frame del video
python utils/video_utils.py video.mp4 --frame 100 --output frame.jpg

# Calcular altura con selección interactiva
python calcular_altura_rapido.py --objeto 15.0 --imagen frame.jpg
```

## 🛠️ Instalación

### Requisitos básicos:
```bash
pip install numpy matplotlib opencv-python
```

### Requisitos para SAM (opcional):
```bash
pip install segment-anything-py torch torchvision
```

### Estructura de archivos:
```
tu_proyecto/
├── utils/
│   └── altura_calculator.py
├── calcular_altura_local.py
├── calcular_altura_rapido.py
└── README_altura_calculator.md
```

## 🔍 Validación y Análisis

Los scripts incluyen funciones avanzadas:

### Validación con múltiples objetos:
- Compara resultados de diferentes objetos
- Calcula estadísticas de precisión
- Identifica posibles errores

### Análisis de sensibilidad:
- Muestra cómo errores en medición afectan la altura
- Recomienda precisión necesaria
- Ayuda a entender la robustez del cálculo

## 📞 Soporte

Si tienes problemas:
1. Verifica que todos los archivos estén en su lugar
2. Asegúrate de tener las dependencias instaladas
3. Revisa que los datos de entrada sean correctos
4. Usa el script interactivo para debugging

## 🎯 Casos de Uso

### 1. Videos sin telemetría:
- Calcula altura usando objetos conocidos
- Útil para videos antiguos o de terceros

### 2. Validación de altura:
- Confirma altura reportada por el dron
- Detecta errores en datos de telemetría

### 3. Calibración de sistema:
- Ajusta parámetros de cámara
- Mejora precisión de mediciones

### 4. Análisis de precisión:
- Evalúa calidad de mediciones
- Optimiza configuración de vuelo 