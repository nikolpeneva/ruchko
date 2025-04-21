#include <Servo.h>
#include <LiquidCrystal.h>

Servo thumb, index, middle, ring, pinky, wrist, base;
int servoPins[] = {3, 4, 5, 6, 7, 8, 9};

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

const int modeButton = 10;
const int resetButton = 11;

int mode = 0;
int userScore = 0;
int handScore = 0;

const int aslAlphabet[26][7] = {
  {90, 90, 90, 90, 90, 90, 90},
  {90, 0, 0, 90, 90, 90, 90},
  {0, 0, 90, 90, 90, 90, 90},
  {90, 0, 90, 90, 90, 90, 90},
  {0, 90, 90, 90, 90, 90, 90},
  {0, 0, 0, 90, 90, 90, 90},
  {90, 90, 0, 90, 90, 90, 90},
  {90, 0, 0, 0, 90, 90, 90},
  {90, 90, 0, 0, 90, 90, 90},
  {90, 90, 0, 0, 0, 90, 90},
  {90, 0, 90, 90, 0, 90, 90},
  {90, 90, 90, 0, 90, 90, 90},
  {0, 0, 0, 0, 90, 90, 90},
  {0, 0, 0, 90, 90, 90, 90},
  {0, 0, 90, 90, 90, 90, 90},
  {0, 0, 0, 0, 0, 90, 90},
  {0, 0, 90, 0, 90, 90, 90},
  {90, 0, 0, 90, 0, 90, 90},
  {90, 90, 90, 90, 0, 90, 90},
  {90, 90, 90, 90, 0, 0, 90},
  {90, 0, 0, 0, 0, 90, 90},
  {90, 0, 0, 0, 90, 90, 90},
  {90, 0, 0, 90, 90, 90, 90},
  {90, 90, 0, 0, 0, 90, 90},
  {90, 0, 0, 90, 0, 90, 90},
  {90, 90, 90, 90, 0, 0, 90}
};

void moveServos(const int positions[]) {
  for (int i = 0; i < 7; i++) {
    Servo &servo = (i == 0 ? thumb : i == 1 ? index : i == 2 ? middle : i == 3 ? ring : i == 4 ? pinky : i == 5 ? wrist : base);
    servo.write(positions[i]);
  }
}
void setup() {
    Serial.begin(9600);
    lcd.begin(20, 4);
  
    thumb.attach(servoPins[0]);
    index.attach(servoPins[1]);
    middle.attach(servoPins[2]);
    ring.attach(servoPins[3]);
    pinky.attach(servoPins[4]);
    wrist.attach(servoPins[5]);
    base.attach(servoPins[6]);
  
    pinMode(modeButton, INPUT_PULLUP);
    pinMode(resetButton, INPUT_PULLUP);
  
    lcd.print("Mode: ASL");
  }
  void loop() {
    if (digitalRead(modeButton) == LOW) {
      mode = (mode + 1) % 3;
      delay(500);
      lcd.clear();
      if (mode == 0) {
        lcd.print("Mode: ASL");
      } else if (mode == 1) {
        lcd.print("Mode: Mirror");
      } else if (mode == 2) {
        lcd.print("Mode: Game");
        userScore = 0;
        handScore = 0;
      }
    }
  
    if (mode == 0) {
      if (Serial.available()) {
        char letter = Serial.read();
        if (letter >= 'A' && letter <= 'Z') {
          int index = letter - 'A';
          moveServos(aslAlphabet[index]);
          lcd.setCursor(0, 1);
          lcd.print("Spelling: ");
          lcd.print(letter);
        }
      }
    } else if (mode == 1) {
      if (Serial.available()) {
        String gesture = Serial.readString();
        if (gesture == "rock") {
          int rockPos[7] = {90, 90, 90, 90, 90, 90, 90};
          moveServos(rockPos);
        } else if (gesture == "paper") {
          int paperPos[7] = {0, 0, 0, 0, 0, 90, 90};
          moveServos(paperPos);
        } else if (gesture == "scissors") {
          int scissorsPos[7] = {90, 0, 0, 90, 90, 90, 90};
          moveServos(scissorsPos);
        }
      }
    }
    else if (mode == 2) {
        if (Serial.available()) {
          String command = Serial.readString();
          if (command == "reset") {
            userScore = 0;
            handScore = 0;
            lcd.clear();
            lcd.print("Mode: Game");
          } else if (command == "rock" || command == "paper" || command == "scissors") {
            int randomChoice = random(0, 3);
            String handChoice = (randomChoice == 0 ? "rock" : randomChoice == 1 ? "paper" : "scissors");
    
            lcd.setCursor(0, 1);
            lcd.print("Hand: ");
            lcd.print(handChoice);
            lcd.setCursor(0, 2);
            lcd.print("User: ");
            lcd.print(command);
    
            if (command == handChoice) {
              lcd.setCursor(0, 3);
              lcd.print("Result: Draw");
            } else if ((command == "rock" && handChoice == "scissors") ||
                       (command == "paper" && handChoice == "rock") ||
                       (command == "scissors" && handChoice == "paper")) {
              userScore++;
              lcd.setCursor(0, 3);
              lcd.print("Result: You Win");
            } else {
              handScore++;
              lcd.setCursor(0, 3);
              lcd.print("Result: Hand Wins");
            }
    
            delay(2000);
            lcd.setCursor(0, 0);
            lcd.print("Score: You ");
            lcd.print(userScore);
            lcd.print(" Hand ");
            lcd.print(handScore);
          } else {
            lcd.clear();
            lcd.print("Invalid Gesture!");
            delay(2000);
            lcd.clear();
            lcd.print("Mode: Game");
          }
    
          if (userScore == 3 || handScore == 3) {
            lcd.clear();
            lcd.print((userScore == 3) ? "You Win the Game!" : "Hand Wins the Game!");
            delay(3000);
            userScore = 0;
            handScore = 0;
          }
        }
      }
    
      if (mode == 2 && digitalRead(resetButton) == LOW) {
        userScore = 0;
        handScore = 0;
        lcd.clear();
        lcd.print("Mode: Game");
        delay(500);
      }
    }
    