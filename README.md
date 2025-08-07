# 🎯 Cálculo de Altura por Objeto de Referencia

Este módulo permite calcular la altura a la que se grabó un video utilizando objetos de referencia (como AprilTags) y el concepto de GSD (Ground Sample Distance).

## 📁 Estructura

```
Objeto_de_referencia/
├── utils/
│   ├── altura_calculator.py    # Módulo principal de cálculos
│   ├── sam_selector.py         # Selección interactiva con SAM
│   └── video_utils.py          # Utilidades para extraer frames
├── calcular_altura_local.py    # Script interactivo completo
├── calcular_altura_rapido.py   # Script rápido con parámetros
├── ejemplo_sam_completo.py     # Ejemplo completo del flujo
├── test_imports.py             # Script de prueba de imports
├── README_altura_calculator.md # Documentación detallada
└── README.md                   # Este archivo
```

## 🚀 Uso Rápido

### Instalación
```bash
# Requisitos básicos
pip install numpy matplotlib opencv-python

# Para SAM (opcional pero recomendado)
pip install segment-anything-py torch torchvision
```

### Verificar Instalación
```bash
# Probar que todo funciona
python test_imports.py
```

### Ejemplo Básico
```bash
# Script interactivo
python calcular_altura_local.py

# Script rápido
python calcular_altura_rapido.py --objeto 15.0 --pixels 43.4

# Con SAM
python calcular_altura_rapido.py --objeto 15.0 --imagen frame.jpg
```

## 🎯 Características

- ✅ **Cálculo preciso de altura** usando objetos de referencia
- ✅ **Selección interactiva con SAM** (haz clic en el objeto)
- ✅ **Compatibilidad con API existente** (genera parámetros listos)
- ✅ **Múltiples métodos de GSD** (tradicional, FOV, referencia)
- ✅ **Validación y análisis de sensibilidad**
- ✅ **Extracción automática de frames** de video

## 📚 Documentación

Para información detallada, consulta:
- [README_altura_calculator.md](README_altura_calculator.md) - Documentación completa
- [ejemplo_sam_completo.py](ejemplo_sam_completo.py) - Ejemplo paso a paso

## 🔧 Integración con API

Este módulo genera parámetros compatibles con `VideoPredictionRequest`:

```python
{
    'altitude': 990,           # Altura en centímetros
    'debug_grid_cm': 50,       # Grid de debug
    'focal_length': 6.72,      # Distancia focal
    'sensor_width': 9.65       # Ancho del sensor
}
``` 