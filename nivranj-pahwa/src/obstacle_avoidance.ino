#include <Servo.h>

const int trigPin = 10;
const int echoPin = 9;

const int servoPin = 13;

const int leftEnable = 12;
const int leftIn1 = 7;
const int leftIn2 = 4;

const int rightEnable = 8;
const int rightIn1 = 3;
const int rightIn2 = 2;

const int safeDistance = 30;
const int stepAngle = 15;

Servo sensorServo;

int distances[13];
int angles[13];


void setup() {
  Serial.begin(9600);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  pinMode(leftEnable, OUTPUT);
  pinMode(leftIn1, OUTPUT);
  pinMode(leftIn2, OUTPUT);

  pinMode(rightEnable, OUTPUT);
  pinMode(rightIn1, OUTPUT);
  pinMode(rightIn2, OUTPUT);

  sensorServo.attach(servoPin);
  sensorServo.write(90);

  stopRobot();

  Serial.println();
  Serial.println("Obstacle Avoidance Robot");
  Serial.println("System started...");
  Serial.println();

  delay(1000);
}


void loop() {

  scanEnvironment(0, 180);
  makeDecision();

  scanEnvironment(180, 0);
  makeDecision();
}


void scanEnvironment(int startAngle, int endAngle) {

  Serial.println();

  if (startAngle < endAngle)
    Serial.println(">>> SCANNING LEFT TO RIGHT <<<");
  else
    Serial.println(">>> SCANNING RIGHT TO LEFT <<<");

  int direction;

  if (startAngle < endAngle)
    direction = 1;
  else
    direction = -1;

  for (int angle = startAngle;
       (direction == 1) ? angle <= endAngle : angle >= endAngle;
       angle += direction * stepAngle) {

    sensorServo.write(angle);
    delay(100);

    int distance = readDistance();

    int index = angle / stepAngle;

    angles[index] = angle;
    distances[index] = distance;

    Serial.print("Angle: ");

    if (angle < 100)
      Serial.print(" ");

    if (angle < 10)
      Serial.print(" ");

    Serial.print(angle);
    Serial.print(" deg | Distance: ");

    if (distance < 100)
      Serial.print(" ");

    if (distance < 10)
      Serial.print(" ");

    Serial.print(distance);
    Serial.print(" cm");

    if (distance <= safeDistance)
      Serial.print("  <<< OBSTACLE");

    Serial.println();
  }
}


int readDistance() {

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);

  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 30000);

  if (duration == 0)
    return 400;

  int distance = duration * 0.0343 / 2;

  if (distance > 400)
    distance = 400;

  if (distance < 2)
    distance = 2;

  return distance;
}


void makeDecision() {

  int leftClearance = 0;
  int rightClearance = 0;
  int frontClearance = 400;

  for (int i = 0; i < 13; i++) {

    int angle = angles[i];
    int distance = distances[i];

    if (angle < 60) {

      if (distance > rightClearance)
        rightClearance = distance;
    }

    else if (angle <= 120) {

      if (distance < frontClearance)
        frontClearance = distance;
    }

    else {

      if (distance > leftClearance)
        leftClearance = distance;
    }
  }

  Serial.println();
  Serial.println("--------------------------------");
  Serial.println("       ANALYSING ENVIRONMENT");
  Serial.println("--------------------------------");

  Serial.print("LEFT CLEARANCE  : ");
  Serial.print(leftClearance);
  Serial.println(" cm");

  Serial.print("FRONT CLEARANCE : ");
  Serial.print(frontClearance);
  Serial.println(" cm");

  Serial.print("RIGHT CLEARANCE : ");
  Serial.print(rightClearance);
  Serial.println(" cm");

  Serial.println();

  if (frontClearance > safeDistance) {

    Serial.println("STATUS : PATH CLEAR");
    Serial.println("DECISION: MOVE FORWARD");

    moveForward();
  }

  else {

    Serial.println("STATUS : OBSTACLE DETECTED!");
    Serial.println("DECISION: FINDING CLEARER DIRECTION");

    stopRobot();
    delay(200);

    if (leftClearance > rightClearance) {

      Serial.println("CLEARER SIDE : LEFT");
      Serial.println("ACTION       : TURN LEFT");

      turnLeft();
      delay(400);
    }

    else {

      Serial.println("CLEARER SIDE : RIGHT");
      Serial.println("ACTION       : TURN RIGHT");

      turnRight();
      delay(400);
    }

    stopRobot();
  }

  Serial.println("--------------------------------");
}


void moveForward() {

  digitalWrite(leftEnable, HIGH);
  digitalWrite(rightEnable, HIGH);

  digitalWrite(leftIn1, HIGH);
  digitalWrite(leftIn2, LOW);

  digitalWrite(rightIn1, HIGH);
  digitalWrite(rightIn2, LOW);
}


void stopRobot() {

  digitalWrite(leftEnable, LOW);
  digitalWrite(rightEnable, LOW);

  digitalWrite(leftIn1, LOW);
  digitalWrite(leftIn2, LOW);

  digitalWrite(rightIn1, LOW);
  digitalWrite(rightIn2, LOW);
}


void turnLeft() {

  digitalWrite(leftEnable, HIGH);
  digitalWrite(rightEnable, HIGH);

  digitalWrite(leftIn1, LOW);
  digitalWrite(leftIn2, HIGH);

  digitalWrite(rightIn1, HIGH);
  digitalWrite(rightIn2, LOW);
}


void turnRight() {

  digitalWrite(leftEnable, HIGH);
  digitalWrite(rightEnable, HIGH);

  digitalWrite(leftIn1, HIGH);
  digitalWrite(leftIn2, LOW);

  digitalWrite(rightIn1, LOW);
  digitalWrite(rightIn2, HIGH);
}