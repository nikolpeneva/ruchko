import cv2
import mediapipe as mp
import serial
import time

arduino = serial.Serial('COM4', 9600)
time.sleep(2)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

current_mode = "mirror"  

def get_finger_states(landmarks):
    tips = [4, 8, 12, 16, 20]
    fingers = []

    fingers.append(int(landmarks[tips[0]].x < landmarks[tips[0] - 1].x))

    for tip in tips[1:]:
        fingers.append(int(landmarks[tip].y < landmarks[tip - 2].y))

    return fingers  

def mirror_mode():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(frame_rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                fingers = get_finger_states(hand_landmarks.landmark)
                servo_positions = [str(pos * 90) for pos in fingers]
                wrist = "90"
                servo_positions.append(wrist)
                data = ','.join(servo_positions) + "\n"
                arduino.write(data.encode())

        cv2.imshow("Hand Mirror", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def send_asl_word(word):
    arduino.write(b"ASL\n")
    time.sleep(1)
    arduino.write((word + "\n").encode())

while True:
    choice = input("Type 'm' for mirror mode or 'a' for ASL mode (q to quit): ").lower()
    if choice == 'm':
        current_mode = "mirror"
        arduino.write(b"MIRROR\n")
        mirror_mode()
    elif choice == 'a':
        current_mode = "asl"
        word = input("Enter a word to spell: ").upper()
        send_asl_word(word)
    elif choice == 'q':
        break
