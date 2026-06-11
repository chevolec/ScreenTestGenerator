#!/usr/bin/env python3
"""
Video Test Pattern Generator
Genera un video MP4 con patrones de prueba para proyección:
  1. Grid Test Pattern
  2. Pantalla Blanca
  3. Pantalla Negra
  4. Barras de color SMPTE

Requisitos:
    pip install opencv-python numpy

Uso:
    python generate_test_pattern.py --width 1920 --height 1080 \
        --grid-duration 10 --white-duration 5 --black-duration 5 --smpte-duration 10

    O en modo interactivo (sin argumentos):
    python generate_test_pattern.py
"""

import cv2
import numpy as np
import argparse
import sys
from typing import Tuple


# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
FPS = 60
CODEC = "mp4v"   # H.264 compatible; en Linux puedes probar "avc1"


# ─────────────────────────────────────────────
# GENERADORES DE FRAMES
# ─────────────────────────────────────────────

def make_grid_frame(width: int, height: int) -> np.ndarray:
    """Grid Test Pattern: cuadrícula con marcadores de centro y esquinas."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = (20, 20, 20)  # fondo casi negro

    color_grid   = (0, 255, 0)       # verde
    color_diag   = (80, 80, 80)      # gris oscuro
    color_center = (255, 255, 255)   # blanco
    color_corner = (0, 180, 255)     # naranja

    # Número de celdas (adaptado a la resolución)
    cols = max(16, width  // 120)
    rows = max(9,  height // 120)

    cell_w = width  / cols
    cell_h = height / rows

    # Líneas diagonales de referencia
    cv2.line(frame, (0, 0),          (width, height), color_diag, 1)
    cv2.line(frame, (width, 0),      (0, height),     color_diag, 1)

    # Líneas verticales
    for c in range(cols + 1):
        x = int(round(c * cell_w))
        cv2.line(frame, (x, 0), (x, height), color_grid, 1)

    # Líneas horizontales
    for r in range(rows + 1):
        y = int(round(r * cell_h))
        cv2.line(frame, (0, y), (width, y), color_grid, 1)

    # Cruz central
    cx, cy = width // 2, height // 2
    arm = min(width, height) // 12
    cv2.line(frame, (cx - arm, cy), (cx + arm, cy), color_center, 2)
    cv2.line(frame, (cx, cy - arm), (cx, cy + arm), color_center, 2)
    cv2.circle(frame, (cx, cy), arm // 2, color_center, 2)

    # Marcadores en esquinas (L shapes)
    m = max(30, min(width, height) // 30)
    corners = [(m, m), (width - m, m), (m, height - m), (width - m, height - m)]
    offsets = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
    for (px, py), (ox, oy) in zip(corners, offsets):
        cv2.line(frame, (px, py), (px + ox * m, py),      color_corner, 3)
        cv2.line(frame, (px, py), (px, py + oy * m),      color_corner, 3)

    # Círculo de aspecto (inscrito en el centro)
    r_circle = min(cx, cy) - max(30, min(width, height) // 20)
    if r_circle > 0:
        cv2.circle(frame, (cx, cy), r_circle, color_center, 1)

    # Texto de resolución y patrón
    font       = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = max(0.6, min(width, height) / 900)
    thickness  = max(1, int(font_scale * 2))
    label      = f"GRID TEST PATTERN  {width}x{height} @ {FPS}fps"
    text_size, _ = cv2.getTextSize(label, font, font_scale, thickness)
    tx = (width - text_size[0]) // 2
    ty = height - max(20, height // 30)
    cv2.putText(frame, label, (tx + 1, ty + 1), font, font_scale, (0,0,0),    thickness + 1, cv2.LINE_AA)
    cv2.putText(frame, label, (tx,     ty),     font, font_scale, color_center, thickness,     cv2.LINE_AA)

    return frame


def make_solid_frame(width: int, height: int,
                     color: Tuple[int,int,int],
                     label: str) -> np.ndarray:
    """Frame de color sólido con etiqueta."""
    frame = np.full((height, width, 3), color, dtype=np.uint8)

    font        = cv2.FONT_HERSHEY_SIMPLEX
    font_scale  = max(0.8, min(width, height) / 700)
    thickness   = max(1, int(font_scale * 2))
    text_color  = (200, 200, 200) if color == (0, 0, 0) else (50, 50, 50)

    text_size, _ = cv2.getTextSize(label, font, font_scale, thickness)
    tx = (width  - text_size[0]) // 2
    ty = (height + text_size[1]) // 2
    cv2.putText(frame, label, (tx, ty), font, font_scale, text_color, thickness, cv2.LINE_AA)

    return frame


def make_smpte_frame(width: int, height: int) -> np.ndarray:
    """
    Barras de color SMPTE (HD 75 % versión estándar).
    Zona superior (~67 %): 7 barras SMPTE
    Zona media  (~8 %):  Banda de referencia
    Zona inferior (~25 %): Pluge + barras de referencia
    """
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # ── Colores SMPTE (BGR) ──────────────────────────────────────────────────
    # Barras superiores: 75 % White, Yellow, Cyan, Green, Magenta, Red, Blue
    top_bars_bgr = [
        (191, 191, 191),   # 75% White
        (  0, 191, 191),   # Yellow
        (191, 191,   0),   # Cyan
        (  0, 191,   0),   # Green
        (191,   0, 191),   # Magenta
        (  0,   0, 191),   # Red
        (191,   0,   0),   # Blue
    ]

    # Banda media: Blue, Black, Magenta, Black, Cyan, Black, 75% White
    mid_bars_bgr = [
        (191,   0,   0),   # Blue
        (  8,   8,   8),   # Near Black
        (191,   0, 191),   # Magenta
        (  8,   8,   8),   # Near Black
        (191, 191,   0),   # Cyan
        (  8,   8,   8),   # Near Black
        (191, 191, 191),   # 75% White
    ]

    # ── Proporciones verticales ──────────────────────────────────────────────
    top_h  = int(height * 0.67)
    mid_h  = int(height * 0.08)
    bot_h  = height - top_h - mid_h

    top_y  = 0
    mid_y  = top_h
    bot_y  = top_h + mid_h

    # ── Barras superiores ────────────────────────────────────────────────────
    n = len(top_bars_bgr)
    bar_w = [width // n] * n
    bar_w[-1] += width - sum(bar_w)  # absorbe residuo de pixel

    x = 0
    for i, bgr in enumerate(top_bars_bgr):
        bw = bar_w[i]
        frame[top_y:top_y + top_h, x:x + bw] = bgr
        x += bw

    # ── Banda media ──────────────────────────────────────────────────────────
    x = 0
    for i, bgr in enumerate(mid_bars_bgr):
        bw = bar_w[i]
        frame[mid_y:mid_y + mid_h, x:x + bw] = bgr
        x += bw

    # ── Zona inferior ────────────────────────────────────────────────────────
    # Proporciones: -I (4/12), White (3/12), +Q (3/12), Black (2/12)
    # + PLUGE (negro -4 IRE, 0 IRE, +4 IRE) en lugar de -I/+Q para HD
    seg_props = [4, 3, 3, 2]
    seg_total  = sum(seg_props)
    seg_colors = [
        (  0,  28,  28),   # -I (PLUGE, sub-black)
        (235, 235, 235),   # 100% White
        ( 28,   0,  28),   # +Q (PLUGE, sub-black)
        (  8,   8,   8),   # Near Black
    ]

    x = 0
    for prop, bgr in zip(seg_props, seg_colors):
        bw = int(width * prop / seg_total)
        frame[bot_y:bot_y + bot_h, x:x + bw] = bgr
        x += bw
    # Rellena el último pixel si hay residuo
    if x < width:
        frame[bot_y:bot_y + bot_h, x:width] = seg_colors[-1]

    # ── Etiqueta ─────────────────────────────────────────────────────────────
    font       = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = max(0.6, min(width, height) / 900)
    thickness  = max(1, int(font_scale * 2))
    label      = f"SMPTE COLOR BARS  {width}x{height}"
    text_size, _ = cv2.getTextSize(label, font, font_scale, thickness)
    tx = (width - text_size[0]) // 2
    ty = top_h - max(10, top_h // 20)
    cv2.putText(frame, label, (tx + 1, ty + 1), font, font_scale, (0,0,0),       thickness + 1, cv2.LINE_AA)
    cv2.putText(frame, label, (tx,     ty),     font, font_scale, (255,255,255),  thickness,     cv2.LINE_AA)

    return frame


# ─────────────────────────────────────────────
# ESCRITURA DE SEGMENTO
# ─────────────────────────────────────────────

def write_segment(writer: cv2.VideoWriter,
                  frame: np.ndarray,
                  duration_sec: int,
                  label: str) -> None:
    """Escribe <duration_sec> segundos del mismo frame con barra de progreso."""
    total = duration_sec * FPS
    print(f"  Generando: {label:30s} ({duration_sec}s × {FPS}fps = {total} frames)")
    for i in range(total):
        writer.write(frame)
        if (i + 1) % FPS == 0:
            elapsed = (i + 1) // FPS
            bar = "█" * elapsed + "░" * (duration_sec - elapsed)
            print(f"    [{bar}] {elapsed}/{duration_sec}s", end="\r")
    print()


# ─────────────────────────────────────────────
# ARGUMENTOS CLI
# ─────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera un video MP4 de patrones de prueba para proyección."
    )
    parser.add_argument("--width",          type=int, default=None,
                        help="Ancho en píxeles (ej. 1920)")
    parser.add_argument("--height",         type=int, default=None,
                        help="Alto en píxeles (ej. 1080)")
    parser.add_argument("--grid-duration",  type=int, default=10,
                        help="Duración del Grid Pattern en segundos (default: 10)")
    parser.add_argument("--white-duration", type=int, default=5,
                        help="Duración de la pantalla blanca en segundos (default: 5)")
    parser.add_argument("--black-duration", type=int, default=5,
                        help="Duración de la pantalla negra en segundos (default: 5)")
    parser.add_argument("--smpte-duration", type=int, default=10,
                        help="Duración de las barras SMPTE en segundos (default: 10)")
    parser.add_argument("--output",         type=str, default=None,
                        help="Nombre del archivo de salida (default: test_pattern_WxH.mp4)")
    return parser.parse_args()


def prompt_resolution() -> Tuple[int, int]:
    """Solicita la resolución interactivamente si no se proveyó por argumento."""
    presets = {
        "1": (1280, 720,  "HD 720p"),
        "2": (1920, 1080, "Full HD 1080p"),
        "3": (2560, 1440, "QHD 1440p"),
        "4": (3840, 2160, "4K UHD"),
        "5": (4096, 2160, "4K DCI"),
        "6": None,
    }
    print("\n── Resolución de salida ──────────────────────────")
    for k, v in presets.items():
        if v:
            print(f"  [{k}] {v[2]:20s}  ({v[0]}×{v[1]})")
        else:
            print(f"  [{k}] Resolución personalizada")
    choice = input("\n  Elige una opción [1-6]: ").strip()

    if choice in presets and presets[choice]:
        w, h, name = presets[choice]
        print(f"  → {name} ({w}×{h})")
        return w, h
    else:
        w = int(input("  Ancho (px): ").strip())
        h = int(input("  Alto  (px): ").strip())
        return w, h


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main() -> None:
    args = parse_args()

    # ── Resolución ───────────────────────────────────────────────────────────
    if args.width and args.height:
        width, height = args.width, args.height
    else:
        width, height = prompt_resolution()

    if width <= 0 or height <= 0:
        print("ERROR: La resolución debe ser mayor que cero.")
        sys.exit(1)

    # ── Duraciones ───────────────────────────────────────────────────────────
    durations = {
        "grid":  args.grid_duration,
        "white": args.white_duration,
        "black": args.black_duration,
        "smpte": args.smpte_duration,
    }

    total_sec = sum(durations.values())

    # ── Archivo de salida ────────────────────────────────────────────────────
    output = args.output or f"test_pattern_{width}x{height}.mp4"

    print(f"\n{'═'*55}")
    print(f"  Test Pattern Generator")
    print(f"{'─'*55}")
    print(f"  Resolución : {width}×{height}")
    print(f"  FPS        : {FPS}")
    print(f"  Duración   : {total_sec}s total")
    print(f"  Patrones   : Grid {durations['grid']}s · Blanco {durations['white']}s · "
          f"Negro {durations['black']}s · SMPTE {durations['smpte']}s")
    print(f"  Salida     : {output}")
    print(f"{'═'*55}\n")

    # ── VideoWriter ──────────────────────────────────────────────────────────
    fourcc = cv2.VideoWriter_fourcc(*CODEC)
    writer = cv2.VideoWriter(output, fourcc, FPS, (width, height))

    if not writer.isOpened():
        print("ERROR: No se pudo crear el VideoWriter. Verifica que OpenCV tenga soporte H.264.")
        sys.exit(1)

    # ── Generar frames por patrón ────────────────────────────────────────────
    segments = [
        (make_grid_frame(width, height),
         durations["grid"],  "Grid Test Pattern"),
        (make_solid_frame(width, height, (255, 255, 255), "WHITE"),
         durations["white"], "White Screen"),
        (make_solid_frame(width, height, (0, 0, 0), "BLACK"),
         durations["black"], "Black Screen"),
        (make_smpte_frame(width, height),
         durations["smpte"], "SMPTE Color Bars"),
    ]

    for frame, duration, label in segments:
        write_segment(writer, frame, duration, label)

    writer.release()
    print(f"\n✓ Video generado: {output}")
    print(f"  {total_sec}s · {total_sec * FPS:,} frames · {width}×{height} @ {FPS}fps\n")


if __name__ == "__main__":
    main()
