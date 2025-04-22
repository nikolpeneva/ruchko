import cv2
import serial
import random
import time

try:
    ser = serial.Serial('COM4', 9600, timeout=1)  
    time.sleep(2)  
except Exception as e:
    print(f"Error connecting to Arduino: {e}")
    exit()

ASL_MODE = 0
MIRROR_MODE = 1
GAME_MODE = 2

current_mode = ASL_MODE  

GESTURES = ['rock', 'paper', 'scissors']

def get_hand_gesture():
    return random.choice(GESTURES)  

try:
    while True:
        if current_mode == ASL_MODE:
            print("ASL Mode: Type a word to spell (A-Z only):")
            word = input().upper()  
            for letter in word:
                if 'A' <= letter <= 'Z':
                    ser.write(letter.encode())  
                    time.sleep(0.5)  
                else:
                    print(f"Invalid character skipped: {letter}")

        elif current_mode == MIRROR_MODE:
            print("Mirror Mode: Performing live hand mirroring...")
            cap = cv2.VideoCapture(0)  
            if not cap.isOpened():
                print("Error: Webcam not detected!")
                break
            while current_mode == MIRROR_MODE:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Frame capture failed!")
                    break

                cv2.imshow("Live Feed", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'): 
                    break
                gesture = get_hand_gesture()  
                ser.write(gesture.encode())  
                time.sleep(0.1)  

            cap.release()
            cv2.destroyAllWindows()

        elif current_mode == GAME_MODE:
            print("Game Mode: Rock-Paper-Scissors")
            user_score = 0
            hand_score = 0
            while user_score < 3 and hand_score < 3:
                print("Make your move (rock, paper, scissors):")
                user_choice = input().lower()
                if user_choice not in GESTURES:
                    print("Invalid choice. Try again!")
                    continue

                hand_choice = random.choice(GESTURES)
                print(f"Hand chose: {hand_choice}")

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

            if user_score == 3:
                print("Congratulations, you won the game!")
            else:
                print("The hand wins the game. Better luck next time!")

        print("\nPress '0' for ASL, '1' for Mirror, '2' for Game, or 'q' to quit:")
        choice = input()
        if choice == '0':
            current_mode = ASL_MODE
        elif choice == '1':
            current_mode = MIRROR_MODE
        elif choice == '2':
            current_mode = GAME_MODE
        elif choice == 'q':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Try again.")

except KeyboardInterrupt:
    print("Program terminated.")

finally:
    ser.close() 
