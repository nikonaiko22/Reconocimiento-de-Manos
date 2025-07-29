# Control de Mouse por Gestos con MediaPipe y OpenCV

Controla el mouse de tu PC usando gestos de tu mano capturados por cámara, gracias a [MediaPipe](https://google.github.io/mediapipe/) y [OpenCV](https://opencv.org/).

## Características principales

- **Modo Mouse:** Control preciso del cursor con el dedo índice cuando tienes 2 o más dedos arriba.
- **Clic:** Haz una "pinza" (junta índice y pulgar) para hacer clic.
- **Scroll vertical:** Levanta solo el índice. Si está arriba de la línea central, scrollea arriba. Si está abajo, scrollea abajo. Si está en la zona central (destacada), no scrollea.
- **Suavizado y zona muerta:** Movimiento fluido y sin saltos por temblores.
- **Feedback visual:** El modo actual, la línea de scroll y la zona muerta se muestran en pantalla.
- **Ganancia configurable:** Ajusta para que pequeños movimientos recorran toda la pantalla.

## Requisitos

- Python 3.7+
- OpenCV
- mediapipe
- pyautogui
- numpy

Instala dependencias con:
```bash
pip install opencv-python mediapipe pyautogui numpy
```

## Uso

1. Conecta tu cámara web.
2. Ejecuta el script:
    ```bash
    python Reconocimiento-manos.py
    ```
3. Apunta tu mano a la cámara y utiliza los siguientes gestos:

### Gestos soportados

- **Mover mouse:** 2 o más dedos arriba (palma semiabierta).
- **Clic:** Junta el índice y el pulgar (pinza).
- **Scroll:** Solo el índice arriba.  
    - Arriba de la línea central → scroll arriba.  
    - Abajo de la línea central → scroll abajo.  
    - En la zona amarilla central → no scrollea (zona de descanso).

## Personalización

Modifica los siguientes parámetros al principio del archivo para ajustar sensibilidad, ganancia, suavizado, etc:

```python
SMOOTHING = 0.35    # Suavizado del movimiento
DEAD_ZONE = 6       # Zona muerta (en píxeles)
PINCH_THRESHOLD = 0.03   # Umbral para clic por pinza
GAIN = 2.0          # Ganancia del área de movimiento
SCROLL_STEP = 80    # Fuerza del scroll
SCROLL_DEADZONE = 0.08   # Zona neutra de scroll (proporción)
```

## Notas

- Cierra la ventana o presiona ESC para salir.
- Puede requerir permisos de control del mouse en algunos sistemas (especialmente macOS).
- Si el movimiento es incómodo, ajusta la ganancia (`GAIN`) o la suavidad (`SMOOTHING`).

---

¡Disfruta controlando tu PC sin tocar el mouse!
