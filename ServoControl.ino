#include <Servo.h>

Servo myservo;
bool is_open = false;  // Track the state of the shutter

void setup() {
  myservo.attach(6);
  Serial.begin(9600); // Initialize serial communication
  myservo.write(0);   // Initialize the servo to the closed position
  Serial.println("Shutter Control Ready");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');

    if (command == "OPEN" && !is_open) {
      openShutter();
      is_open = true;
      Serial.println("Shutter Opened");
    } else if (command == "CLOSE" && is_open) {
      closeShutter();
      is_open = false;
      Serial.println("Shutter Closed");
    } else {
      Serial.println(is_open ? "Shutter already open" : "Shutter already closed");
    }
  }
}

void openShutter() {
  for (int pos = 0; pos <= 90; pos += 1) {
    myservo.write(pos);
    delay(5);
  }
}

void closeShutter() {
  for (int pos = 90; pos >= 0; pos -= 1) {
    myservo.write(pos);
    delay(5);
  }
}
