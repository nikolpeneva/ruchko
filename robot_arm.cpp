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
  