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

    thumb_base = landmarks[3]
    index_base = landmarks[6]
    middle_base = landmarks[10]
    ring_base = landmarks[14]
    pinky_base = landmarks[18]

    if all(tip.y < base.y - 0.1 for tip, base in zip(
        [index_tip, middle_tip, ring_tip, pinky_tip],
        [index_base, middle_base, ring_base, pinky_base])):
        return "paper"

    if all(tip.y > base.y + 0.1 for tip, base in zip(
        [index_tip, middle_tip, ring_tip, pinky_tip],
        [index_base, middle_base, ring_base, pinky_base])):
        return "rock"

    if (index_tip.y < index_base.y - 0.1 and middle_tip.y < middle_base.y - 0.1 and
        ring_tip.y > ring_base.y + 0.1 and pinky_tip.y > pinky_base.y + 0.1):
        return "scissors"

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
    word = input("Enter a word: ").upper()  
    for letter in word:
        if 'A' <= letter <= 'Z':  
            print(f"Sending letter: {letter}")
            ser.write(letter.encode()) 
            time.sleep(1)  
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

    cap = cv2.VideoCapture(0)  # Open the camera when Game Mode starts
    if not cap.isOpened():
        print("Error: Webcam not detected!")
        return

    print("Show your hand gesture to the camera (rock, paper, scissors).")
    while user_score < 3 and hand_score < 3:
        print("Get ready to make your move...")
        time.sleep(2)  # Give the user 2 seconds to prepare

        print("Recognizing your gesture...")
        user_choices = []
        start_time = time.time()

        # Capture frames for 3 seconds to recognize the user's gesture
        while time.time() - start_time < 3:
            user_choice = None  # Initialize user_choice
            ret, frame = cap.read()
            if not ret:
                print("Error: Frame capture failed!")
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(frame_rgb)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    user_choice = classify_gesture(hand_landmarks.landmark)
                    if user_choice:
                        user_choices.append(user_choice)

            cv2.putText(frame, "Recognizing...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.imshow("Game Mode - Rock Paper Scissors", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Exiting game mode.")
                cap.release()
                cv2.destroyAllWindows()
                return

        # Determine the most common gesture recognized
        if user_choices:
            user_choice = max(set(user_choices), key=user_choices.count)
        else:
            user_choice = None

        if user_choice:
            print(f"Your choice: {user_choice}")
            ser.write(f"USER:{user_choice}\n".encode())  # Send the user's choice to Arduino
        else:
            print("Gesture not recognized. Try again!")
            continue

        # Randomize the hand's choice
        hand_choice = random.choice(GESTURES)
        print(f"Hand chose: {hand_choice}")
        ser.write(f"{hand_choice}\n".encode())  # Send the hand's choice to Arduino

        # Determine the winner of the round
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

        # Send the updated scores to the Arduino
        ser.write(f"SCORE:{user_score},{hand_score}\n".encode())

        # Display the current score
        print(f"Score: You {user_score} - {hand_score} Hand")

        # Wait for the user to type 'next' to proceed to the next round
        while True:
            next_input = input("Type 'next' to start the next round or 'q' to quit: ").strip().lower()
            if next_input == 'next':
                break
            elif next_input == 'q':
                print("Exiting game mode.")
                cap.release()
                cv2.destroyAllWindows()
                return
            else:
                print("Invalid input. Please type 'next' or 'q'.")

    cap.release()
    cv2.destroyAllWindows()

    # Announce the winner
    if user_score == 3:
        print("Congratulations, you won the game!")
    else:
        print("The hand wins the game. Better luck next time!")

try:
    print("Select a mode:")
    print("0: ASL Mode")
    print("1: Mirror Mode")
    print("2: Game Mode")

    while True:
        mode_input = input("Enter the mode number (0, 1, 2) or 'q' to quit: ").strip()

        if mode_input == 'q':
            print("Exiting program.")
            break

        if mode_input == '0':
            print("Mode selected: ASL")
            run_asl_mode()
        elif mode_input == '1':
            print("Mode selected: Mirror")
            run_mirror_mode()
        elif mode_input == '2':
            print("Mode selected: Game")
            run_game_mode()
        else:
            print("Invalid input. Please enter 0, 1, 2, or 'q' to quit.")

except KeyboardInterrupt:
    print("\nProgram terminated by user.")

finally:
    ser.close()
