// Motor A - forward/reverse
#define motorDriveForward 26
#define motorDriveBackward 27

// Motor B - left/right
#define motorTurnLeft 15
#define motorTurnRight 18
void setup() {
  Serial.begin(115200);

  // Set motor pins as outputs
  pinMode(motorDriveForward, OUTPUT);
  pinMode(motorDriveBackward, OUTPUT);
  pinMode(motorTurnLeft, OUTPUT);
  pinMode(motorTurnRight, OUTPUT);


  Serial.println("RC Car Ready! Use WASD to control.");
  digitalWrite(motorTurnLeft, HIGH);

  //digitalWrite(motorDriveBackward, LOW);
}

void loop() {
  digitalWrite(motorTurnLeft, HIGH);
  digitalWrite(motorTurnRight, LOW);

  delay(2000);
  digitalWrite(motorTurnLeft, LOW);
  digitalWrite(motorTurnRight, HIGH);
  delay(2000);

  digitalWrite(motorDriveBackward, LOW);
  digitalWrite(motorDriveForward, HIGH);
  delay(2000);
  digitalWrite(motorDriveBackward, HIGH);
  digitalWrite(motorDriveForward, LOW);
  delay(2000);

}

