import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
from collections import deque

CAMERA_INDEX = 0
FRAME_W, FRAME_H = 100, 75
SMOOTHING = 0.35             # Más suavizado para menos jitter
DEAD_ZONE = 6                # Zona muerta más pequeña para control fino
PINCH_THRESHOLD = 0.03       # Umbral más estricto para clics accidentales
SCROLL_THRESHOLD = 0.009     # Scroll más sensible
GAIN = 2.0                   # Más ganancia para cubrir toda la pantalla
SCROLL_COOLDOWN = 0.03       # Scroll más frecuente
CLICK_COOLDOWN = 0.25        # Evita dobleclics accidentales

cap = cv2.VideoCapture(CAMERA_INDEX)
screen_w, screen_h = pyautogui.size()
mp_hands = mp.solutions.hands

prev_mouse_x, prev_mouse_y = pyautogui.position()
click_down = False
last_scroll_time = time.time()
prev_index_y = None
mode = "INACTIVE"
click_timer = 0
gesture_history = deque(maxlen=8)  # Para estabilidad de gestos

def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def fingers_up(lm):
    res = []
    for i in [8, 12, 16, 20]:
        res.append(lm[i].y < lm[i - 2].y)
    return res

def stable_mode(history, fallback="INACTIVE"):
    """Devuelve el modo más común en el historial para evitar cambios bruscos."""
    if not history: return fallback
    counts = {}
    for m in history:
        counts[m] = counts.get(m, 0) + 1
    return max(counts, key=counts.get)

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=0
) as hands:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.resize(frame, (FRAME_W, FRAME_H))
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        show_mode = mode
        color = (100, 100, 100)
        pinch_now = False

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            lm = hand_landmarks.landmark

            fingers = fingers_up(lm)
            total_fingers = sum(fingers)

            # --- GESTO DE ACTIVACIÓN (pulgar, índice Y medio arriba) ---
            act = fingers[0] and fingers[1] and fingers[2] and not fingers[3]
            # --- SCROLL: solo índice y medio arriba ---
            scroll_gesture = fingers[0] and fingers[1] and not fingers[2] and not fingers[3]
            # --- MOUSE: palma abierta (3+ dedos arriba) ---
            mouse_gesture = (total_fingers >= 3)
            # --- INACTIVO: puño cerrado ---
            inactive_gesture = (total_fingers == 0)

            # Decisión de modo usando el historial para robustez
            if mouse_gesture:
                gesture_history.append("MOUSE")
            elif scroll_gesture:
                gesture_history.append("SCROLL")
            elif inactive_gesture:
                gesture_history.append("INACTIVE")
            else:
                gesture_history.append("INACTIVE")

            mode = stable_mode(gesture_history)

            # --- Colores visuales de feedback ---
            if mode == "MOUSE":
                color = (0, 255, 0)
            elif mode == "SCROLL":
                color = (0, 165, 255)
            else:
                color = (80, 80, 80)

            show_mode = mode

            # --- SCROLL ---
            if mode == "SCROLL":
                now = time.time()
                if prev_index_y is not None and now - last_scroll_time > SCROLL_COOLDOWN:
                    dy = lm[8].y - prev_index_y
                    if abs(dy) > SCROLL_THRESHOLD:
                        pyautogui.scroll(-int(300 * dy))
                        last_scroll_time = now
                prev_index_y = lm[8].y
                # No mover mouse ni detectar clic
            elif mode == "MOUSE":
                prev_index_y = None

                # --- MOVIMIENTO DEL MOUSE CON GANANCIA Y SUAVIZADO ---
                x = lm[8].x
                y = lm[8].y
                x_inv = 1 - x

                x_centered = (x_inv - 0.5) * GAIN + 0.5
                y_centered = (y - 0.5) * GAIN + 0.5
                x_centered = min(max(x_centered, 0), 1)
                y_centered = min(max(y_centered, 0), 1)

                target_x = int(x_centered * screen_w)
                target_y = int(y_centered * screen_h)

                mouse_x = int(prev_mouse_x + (target_x - prev_mouse_x) * SMOOTHING)
                mouse_y = int(prev_mouse_y + (target_y - prev_mouse_y) * SMOOTHING)

                # --- ZONA MUERTA ---
                if abs(mouse_x - prev_mouse_x) > DEAD_ZONE or abs(mouse_y - prev_mouse_y) > DEAD_ZONE:
                    pyautogui.moveTo(mouse_x, mouse_y, duration=0)
                    prev_mouse_x, prev_mouse_y = mouse_x, mouse_y

                # --- GESTO DE CLIC ROBUSTO ---
                index_tip = np.array([lm[8].x, lm[8].y])
                thumb_tip = np.array([lm[4].x, lm[4].y])
                pinza_dist = distance(index_tip, thumb_tip)
                pinch_now = (pinza_dist < PINCH_THRESHOLD)

                now = time.time()
                if pinch_now and not click_down and (now - click_timer > CLICK_COOLDOWN):
                    pyautogui.mouseDown()
                    click_down = True
                    click_timer = now
                elif not pinch_now and click_down:
                    pyautogui.mouseUp()
                    click_down = False
            else:
                prev_index_y = None
                if click_down:
                    pyautogui.mouseUp()
                    click_down = False

        else:
            prev_index_y = None
            if click_down:
                pyautogui.mouseUp()
                click_down = False
            gesture_history.append("INACTIVE")
            mode = stable_mode(gesture_history)

        # --- FEEDBACK VISUAL ---
        cv2.rectangle(frame, (0, 0), (FRAME_W, 30), color, -1)
        cv2.putText(frame, f"MODO: {show_mode}", (5, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)

        # Dibuja landmarks para depuración avanzada
        if results.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow('Hand Control PRO', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()