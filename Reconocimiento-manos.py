import cv2

# Tu URL de cámara IP (ajústala si tu app usa otro endpoint)
url = "ip webcam"

cap = cv2.VideoCapture(url)

while True:
    ret, frame = cap.read()
    if not ret:
        print("No se pudo recibir imagen. Saliendo...")
        break
    cv2.imshow('Camara IP', frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Presiona ESC para salir
        break

cap.release()
cv2.destroyAllWindows()