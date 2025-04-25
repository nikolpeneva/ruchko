import cv2
import mediapipe as mp
import serial
import random
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def classify_gesture(landmarks):
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]

    if all(landmark.y < landmarks[0].y for landmark in [index_tip, middle_tip, ring_tip, pinky_tip]):
        return "paper"
    elif all(landmark.y > landmarks[0].y for landmark in [index_tip, middle_tip, ring_tip, pinky_tip]):
        return "rock"
    elif index_tip.y < landmarks[0].y and middle_tip.y < landmarks[0].y and ring_tip.y > landmarks[0].y and pinky_tip.y > landmarks[0].y:
        return "scissors"
    else:
        return None

def calculate_finger_angles(landmarks):
    angles = []

    finger_tips = [4, 8, 12, 16, 20]
    finger_base = [3, 6, 10, 14, 18]

    for tip, base in zip(finger_tips, finger_base):
        if landmarks[tip].y < landmarks[base].y:  
            angles.append(0)
        elif abs(landmarks[tip].y - landmarks[base].y) < 0.05: 
            angles.append(90)
        else:  
            angles.append(180)

    return angles

try:
    ser = serial.Serial('COM4', 9600, timeout=1)
    time.sleep(2)
except Exception as e:
    print(f"Error connecting to Arduino: {e}")
    exit()

asl_mode = 0
mirror_mode = 1
game_mode = 2

GESTURES = ['rock', 'paper', 'scissors']

def run_asl_mode():
    print("ASL Mode: Type a word to spell (A-Z only):")
    word = input().upper()
    for letter in word:
        if 'A' <= letter <= 'Z':
            ser.write(letter.encode())
            time.sleep(0.5)
        else:
            print(f"Invalid character skipped: {letter}")

def run_mirror_mode():
    print("Mirror Mode: Performing live hand mirroring...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Webcam not detected!")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Frame capture failed!")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(frame_rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                angles = calculate_finger_angles(hand_landmarks.landmark)
                print(f"Finger angles: {angles}")

                angles_str = ','.join(map(str, angles))
                ser.write(angles_str.encode())
                time.sleep(0.1)

        cv2.imshow("Live Feed", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def run_game_mode():
    print("Game Mode: Rock-Paper-Scissors")
    user_score = 0
    hand_score = 0

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Webcam not detected!")
        return

    print("Show your hand gesture to the camera (rock, paper, scissors).")
    while user_score < 3 and hand_score < 3:
        ret, frame = cap.read()
        if not ret:
            print("Error: Frame capture failed!")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(frame_rgb)

        user_choice = None
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                user_choice = classify_gesture(hand_landmarks.landmark)

        cv2.putText(frame, "Make your move!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        if user_choice:
            cv2.putText(frame, f"Your choice: {user_choice}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Game Mode - Rock Paper Scissors", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Exiting game mode.")
            break

        if user_choice in GESTURES:
            hand_choice = random.choice(GESTURES)
            print(f"Hand chose: {hand_choice}")
            print(f"You chose: {user_choice}")

            if user_choice == hand_choice:
                print("It's a draw!")
            elif (user_choice == 'rock' and hand_choice == 'scissors') or \
                 (user_choice == 'paper' and hand_choice == 'rock') or \
                 (user_choice == 'scissors' and hand_choice == 'paper'):
                print("You win this round!")
                user_score += 1
            else:
                print("Hand wins this round!")
                hand_score += 1

            print(f"Score: You {user_score} - {hand_score} Hand")
            ser.write(hand_choice.encode())
            time.sleep(0.5)

    cap.release()
    cv2.destroyAllWindows()

    if user_score == 3:
        print("Congratulations, you won the game!")
    else:
        print("The hand wins the game. Better luck next time!")

try:
    current_mode = asl_mode
    while True:
        if current_mode == asl_mode:
            run_asl_mode()
        elif current_mode == mirror_mode:
            run_mirror_mode()
        elif current_mode == game_mode:
            run_game_mode()

        print("\nPress '0' for ASL, '1' for Mirror, '2' for Game, or 'q' to quit:")
        choice = input()
        if choice == '0':
            current_mode = asl_mode
        elif choice == '1':
            current_mode = mirror_mode
        elif choice == '2':
            current_mode = game_mode
        elif choice == 'q':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Try again.")

except KeyboardInterrupt:
    print("Program terminated.")

finally:
    ser.close()
