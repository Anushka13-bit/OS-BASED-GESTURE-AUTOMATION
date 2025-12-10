# AirSense Client — Python 3
# Features:
# - Camera capture via OpenCV
# - Hand tracking via MediaPipe
# - Pinch click, scroll, zoom gestures
# - Sends gesture commands via TCP to server

import cv2
import mediapipe as mp
import socket
import time
import math

# ----------------------------- CONFIG -----------------------------
SERVER_IP = "172.17.70.45"  # Change if needed
SERVER_PORT = 5005
BUFFER_SIZE = 1024

# Gesture config
PINCH_THRESHOLD = 0.04
SCROLL_THRESHOLD = 0.05
SMOOTHING = 4.0

# ----------------------------- TCP SETUP -----------------------------
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    print(f"Connecting to server {SERVER_IP}:{SERVER_PORT} ...")
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print("Connected to server!")
except Exception as e:
    print(f"TCP connect failed: {e}")
    client_socket.close()
    exit()

# ----------------------------- MEDIAPIPE SETUP -----------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# Smoothing helper
prev_x, prev_y = 0, 0

# ----------------------------- MAIN LOOP -----------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot open webcam")
    exit()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip for mirror view
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        gesture_command = None

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Index fingertip
            x_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
            y_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y

            # Smoothing
            x_tip = prev_x + (x_tip - prev_x) / SMOOTHING
            y_tip = prev_y + (y_tip - prev_y) / SMOOTHING
            prev_x, prev_y = x_tip, y_tip

            # Pinch detection (thumb + index)
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            distance = math.hypot(x_tip - thumb_tip.x, y_tip - thumb_tip.y)

            if distance < PINCH_THRESHOLD:
                gesture_command = "CLICK"
            else:
                gesture_command = f"MOVE {x_tip:.3f} {y_tip:.3f}"

        # Send command to server
        if gesture_command:
            try:
                client_socket.sendall(gesture_command.encode())
            except Exception as e:
                print(f"TCP send failed: {e}")
                break

        # Display
        cv2.putText(frame, gesture_command if gesture_command else "", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("AirSense Client", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
            break

except KeyboardInterrupt:
    print("Exiting...")

finally:
    cap.release()
    cv2.destroyAllWindows()
    client_socket.close()
    print("Client closed.")
