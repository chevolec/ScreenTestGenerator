# Screentest Generator

Genera videos MP4 de patrones de prueba para proyección, o slideshows de imágenes.

## Instalación

```
pip install opencv-python numpy pillow
```

---

## Modo 1: Test Pattern

Genera un video con patrones de calibración de pantalla.

**Uso interactivo** (te pregunta la resolución):
```
python generateScreentest.py
```

**Uso con argumentos:**
```
python generateScreentest.py \
  --width 1920 --height 1080 \
  --grid-duration 10 \
  --white-duration 5 \
  --black-duration 5 \
  --smpte-duration 10 \
  --output mi_video.mp4
```

### Patrones disponibles

| Patrón | Detalle |
|-|-|
| Grid | Cuadrícula adaptativa, diagonales, cruz central, círculo de aspecto, marcadores en esquinas |
| Blanco | 255,255,255 puro con etiqueta |
| Negro | 0,0,0 puro con etiqueta |
| SMPTE | HD 75% — 7 barras superiores, banda de referencia media, zona PLUGE inferior |

El video sale como `test_pattern_WxH.mp4` a 60 fps, con barra de progreso en terminal.

---

## Modo 2: Slideshow

Genera un video slideshow a partir de una carpeta de imágenes.

**Uso básico:**
```
python generateScreentest.py --slideshow \
  --images-dir ./fotos \
  --width 1920 --height 1080
```

**Uso completo:**
```
python generateScreentest.py --slideshow \
  --images-dir ./fotos \
  --width 1920 --height 1080 \
  --slide-duration 10 \
  --transition-duration 0.5 \
  --shuffle \
  --show-filename \
  --output mi_slideshow.mp4
```

### Parámetros slideshow

| Parámetro | Default | Descripción |
|-|-|-|
| `--images-dir` | requerido* | Carpeta con las imágenes |
| `--slide-duration` | 30s | Duración de cada imagen en segundos |
| `--transition-duration` | 0.5s | Duración de la transición entre imágenes |
| `--shuffle` | off | Mostrar imágenes en orden aleatorio |
| `--show-filename` | off | Mostrar el nombre del archivo sobre cada imagen |
| `--output` | `slideshow_WxH.mp4` | Nombre del archivo de salida |

*Si no se pasa, lo pregunta interactivamente.

### Formatos de imagen soportados

`.jpg` · `.jpeg` · `.png` · `.bmp` · `.webp`

### Comportamiento

- Las imágenes se ordenan alfabéticamente por defecto (`--shuffle` para aleatorio)
- Si la imagen no coincide con la resolución del video, se escala con letterbox (barras negras) manteniendo el aspect ratio, usando PIL Lanczos para máxima calidad
- La transición entre imágenes es un barrido de izquierda a derecha
- El video se genera a 60 fps
