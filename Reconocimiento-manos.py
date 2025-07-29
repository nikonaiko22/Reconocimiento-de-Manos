import cv2
import mediapipe as mp

# URL de tu cámara IP (ajusta si es necesario)
url = "ip webcam"

cap = cv2.VideoCapture(url)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5) as hands:

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo recibir imagen. Saliendo...")
            break

        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = hands.process(rgb)

        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

        cv2.imshow('Detección de mano', frame)

        
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()