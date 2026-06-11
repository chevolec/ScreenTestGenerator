# Screentest Generator

Instalacion 
```
pip install opencv-python numpy
```

Uso básico (modo interactivo)
```
python generate_test_pattern.py
```
Te pregunta la resolución con un menú de presets (720p, 1080p, 1440p, 4K, 4K DCI, o custom).

Uso con argumentos (modo automatizado)
```
python generate_test_pattern.py \
  --width 1920 --height 1080 \
  --grid-duration 10 \
  --white-duration 5 \
  --black-duration 5 \
  --smpte-duration 10 \
  --output mi_video.mp4
```

¿Qué genera cada patrón?
| Patrón | Detalle|
|-|-|
|Grid | Cuadrícula adaptativa, diagonales, cruz central, círculo de aspecto, marcadores en esquinas|
|-|-|
|Blanco | 255,255,255 puro con etiqueta|
|-|-|
|Negro | 0,0,0 puro con etiqueta|
|-|-|
|SMPTE | HD 76% — 7 barras superiores, banda de referencia media, zona PLUGE inferior|

El video sale como `test_pattern_WxH.mp4` a 60 fps, con una barra de progreso en terminal mientras genera. Los patrones y duraciones son completamente independientes entre sí vía argumentos.
