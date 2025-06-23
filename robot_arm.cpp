#include <Servo.h>
#include <LiquidCrystal_I2C.h>

Servo thumb, index, middle, ring, pinky, wrist, base;
int servoPins[] = {3, 5, 6, 9, 10, 11, 12};

LiquidCrystal_I2C lcd(0x27, 20, 4);

const int modeButton = 2;
const int resetButton = 13;

int mode = 0; 
int userScore = 0;
int handScore = 0;

const int aslAlphabet[26][7] = {
  {0, 90, 90, 90, 90, 0}, //a
  {150, 0, 0, 0, 0, 0 },  //b
  {0, 90, 90, 90, 90, 0}, //c
  {150, 0, 150, 150, 150, 0},  //d
  {150, 90, 90, 90, 90, 0},  //e
  {90, 90, 0, 0, 0, 0}, //f
  {0, 0, 180, 180, 180, 90},  //g
  {0, 0, 0, 180, 180, 90}, //h
  {150, 150, 150, 150, 0, 0},  //i
  {150, 150, 150, 150, 0, 0}, //j
  {0, 0, 0, 150, 150, 0},  //k
  {0, 0, 150, 150, 150, 0},  //l
  {180, 0, 0, 0, 180, 90},  //m
  {180, 0, 0, 180, 180, 90}, //n
  {120, 120, 120, 120, 120, 90},  //o
  {120, 0, 120, 120, 120, 90}, //p
  {0, 0, 180, 180, 180, 90}, //q
  {150, 150, 150, 0, 0, 90}, //r
  {180, 180, 180, 180, 180, 90}, //s
  {180, 0, 180, 180, 180, 90}, //t
  {150, 0, 0, 150, 150, 0},  //v
  {150, 0, 0, 0, 150, 0},  //w
  {150, 90, 150, 150, 150, 0}, //x
  {150, 0, 150, 150, 0, 0},  //y
  {180, 0, 180, 180, 180, 90} //z
};

void moveServos(const int positions[]) {
    Servo servos[] = {thumb, index, middle, ring, pinky, wrist}; 
    for (int i = 0; i < 6; i++) {
        servos[i].write(positions[i]); 
    }
}

void setup() {
    Serial.begin(9600);
    lcd.begin();
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Initializing...");
  
    thumb.attach(servoPins[0]);
    index.attach(servoPins[1]);
    middle.attach(servoPins[2]);
    ring.attach(servoPins[3]);
    pinky.attach(servoPins[4]);
    wrist.attach(servoPins[5]);
  
    pinMode(modeButton, INPUT_PULLUP);
    pinMode(resetButton, INPUT_PULLUP);
  
    lcd.clear();
    lcd.print("Mode: ASL");
}

void loop() {
    if (digitalRead(modeButton) == LOW) {
        mode = (mode + 1) % 3; 
        delay(500); 
        lcd.clear();
        if (mode == 0) {
            lcd.print("Mode: ASL");
            Serial.println("ASL");
        } else if (mode == 1) {
            lcd.print("Mode: Mirror");
            Serial.println("Mirror");
        } else if (mode == 2) {
            lcd.print("Mode: Game");
            Serial.println("Game");
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
                lcd.clear();
                lcd.setCursor(0, 0);
                lcd.print("Spelling: ");
                lcd.print(letter); 
            } else {
                lcd.clear();
                lcd.setCursor(0, 0);
                lcd.print("Invalid Letter!");
                delay(2000);
                lcd.clear();
                lcd.print("Mode: ASL");
            }
        }
    }

    else if (mode == 1) {
        if (Serial.available()) {
            String anglesString = Serial.readString(); 
            int angles[7]; 
            int index = 0;

            for (int i = 0; i < anglesString.length(); i++) {
                char c = anglesString[i];
                if (c >= '0' && c <= '9') {
                    int angle = 0;
                    while (c >= '0' && c <= '9') {
                        angle = angle * 10 + (c - '0');
                        i++;
                        if (i < anglesString.length()) {
                            c = anglesString[i];
                        } else {
                            break;
                        }
                    }
                    angles[index++] = angle;
                    if (index >= 7) break; 
                }
            }

            if (index == 7) { 
                moveServos(angles);
            } else {
                lcd.clear();
                lcd.print("Invalid Angles!");
                delay(2000);
                lcd.clear();
                lcd.print("Mode: Mirror");
            }
        }
    }

    else if (mode == 2) { // Game Mode
        if (Serial.available()) {
            String command = Serial.readStringUntil('\n'); 
            command.trim(); 

            if (command.startsWith("USER:")) {
                String userGesture = command.substring(5); 
                userGesture.trim();

                while (!Serial.available()) {
                    lcd.clear();
                    lcd.setCursor(0, 0);
                    lcd.print("Waiting for hand...");
                    delay(1000); 
                }
                String handChoice = Serial.readStringUntil('\n'); 
                handChoice.trim();

                if (handChoice == "rock") {
                    int rockPositions[6] = {150, 150, 150, 150, 150, 0};
                    moveServos(rockPositions);
                } else if (handChoice == "paper") {
                    int paperPositions[6] = {0, 0, 0, 0, 0, 0};
                    moveServos(paperPositions);
                } else if (handChoice == "scissors") {
                    int scissorsPositions[6] = {150, 0, 0, 150, 150, 0};
                    moveServos(scissorsPositions);
                }

                lcd.clear();
                lcd.setCursor(0, 0);
                lcd.print("Hand: ");
                lcd.print(handChoice);
                lcd.setCursor(0, 1);
                lcd.print("User: ");
                lcd.print(userGesture);
            } else if (command.startsWith("SCORE:")) {
                // Parse the scores from the command
                int separatorIndex = command.indexOf(',');
                userScore = command.substring(6, separatorIndex).toInt();
                handScore = command.substring(separatorIndex + 1).toInt();

                // Display the scores on the LCD
                lcd.clear();
                lcd.setCursor(0, 0);
                lcd.print("Score:");
                lcd.setCursor(0, 1);
                lcd.print("User ");
                lcd.print(userScore);
                lcd.print(" - Hand ");
                lcd.print(handScore);

                // Check if someone has won
                if (userScore == 3 || handScore == 3) {
                    lcd.clear();
                    lcd.print((userScore == 3) ? "You Win!" : "Hand Wins!");
                    delay(3000);
                    userScore = 0;
                    handScore = 0;
                }
            }
        }
    }
}
