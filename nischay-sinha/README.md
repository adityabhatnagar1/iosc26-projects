<!-- 📌 Nischay Sinha: edit ONLY inside this folder (/nischay-sinha). Fill in every section below, replacing [placeholders] with your own words. Delete this comment when you start. -->

# Project Title

> A 3-sensor autonomous guide robot that detects obstacles using ultrasonic sensors and automatically changes direction to navigate around them.

**Track:** GUIDE ROBOT
**Candidate:** Nischay Sinha  
**Github Username**: NooONE0026
**Phone Number**: 9205657793  
**Email ID**: nischaysinha260707@gmail.com 

---

## 1. Overview

### What & Why
The Guide Robot is a simulated assistive-navigation prototype designed to demonstrate how a mobile robot can detect obstacles and make basic navigation decisions.

The robot uses three ultrasonic sensors positioned toward the front, left and right sides. The Arduino reads the measured distances and decides whether the robot should move forward, turn left, turn right, or perform a recovery maneuver.

The project was developed as a simulation in Tinkercad so that the sensing, decision-making and motor-control logic could be tested before any physical implementation.

### Expected Outcome
The expected outcome of this project is to develop a working Tinkercad simulation of an assistive navigation robot that can:

- Detect obstacles using three ultrasonic sensors.
- Measure the distance of obstacles in front, left, and right directions.
- Automatically decide whether to move forward, turn left, or turn right.
- Compare the available space on the left and right sides to select a safer direction.
- Control two DC motors using an L293D motor driver.
- Provide visual feedback using green and red LEDs.
- Provide an audible warning using a buzzer when an obstacle is detected.
- Display sensor readings and navigation decisions through the Arduino Serial Monitor.
- Demonstrate basic autonomous obstacle avoidance through simulation.

---

## 2. Requirements

### Hardware
| Component | Qty | Purpose |
|---|---:|---|
| Arduino Uno R3 | 1 | Main controller for sensor processing and navigation logic |
| HC-SR04 Ultrasonic Sensor | 3 | Detect obstacles and measure distance in front, left, and right directions |
| L293D Motor Driver | 1 | Controls the direction and speed of the two DC motors |
| DC Motor | 2 | Simulates the left and right wheels of the robot |
| Green LED | 1 | Indicates that the path is clear |
| Red LED | 1 | Indicates that an obstacle has been detected |
| Piezo Buzzer | 1 | Provides an audible obstacle warning |
| 220Ω Resistor | 2 | Limits current through the LEDs |
| Breadboard | 1 | Used for circuit connections |
| Jumper Wires | As required | Used to connect the components |

### Software
| Tool / Library | Version | Purpose |
|---|---|---|
| Tinkercad Circuits | Web-based | Simulate the complete robot circuit |
| Arduino C/C++ | Arduino-compatible | Program the robot's sensing, decision-making, and motor control |
| Arduino Serial Monitor | 9600 baud | Display sensor readings and navigation decisions |

**Constraints:** The project was developed as a simulation-only prototype in Tinkercad due to the available time and hardware constraints. No physical robot hardware was used for the submitted demonstration.


---

## 3. Design

### System Overview

The Guide Robot follows a sensor-to-decision-to-action architecture.

Three HC-SR04 ultrasonic sensors continuously measure the distance around the robot from the front, left, and right directions. These distance readings are sent to the Arduino Uno, which processes them using predefined obstacle-detection and navigation rules.

If the front path is clear, the robot moves forward. If an obstacle is detected, the Arduino compares the left and right distances and selects the direction with more available space.

The Arduino sends control signals to the L293D motor driver, which controls the direction and speed of the two DC motors. A green LED indicates a clear path, while a red LED and buzzer provide feedback when an obstacle is detected.

System Flow:

Ultrasonic Sensors
        ↓
Distance Measurement
        ↓
Arduino Uno
        ↓
Navigation Decision
        ↓
L293D Motor Driver
        ↓
Left & Right DC Motors
        ↓
Robot Movement

Additional feedback:

Arduino
   ↓
Green LED / Red LED / Buzzer

### Key Decisions

1. Three ultrasonic sensors were selected instead of one so that the robot can compare the available space on the left and right sides when an obstacle is detected.

2. Arduino Uno was selected as the main controller because it provides sufficient pins for the sensors, motor driver, LEDs, and buzzer.

3. The L293D motor driver was used to control the two DC motors and allow independent control of their direction.

4. A rule-based navigation approach was selected because it is simple, deterministic, easy to debug, and suitable for demonstrating basic autonomous obstacle avoidance.

5. A 25 cm obstacle threshold was selected. When the front sensor detects an object at or below this distance, the robot stops and starts its obstacle-avoidance decision.

6. Visual and audio feedback was added using LEDs and a buzzer so that the robot's current state can be easily understood during the simulation.
---

## 4. Implementation

The robot was implemented using an Arduino Uno, three HC-SR04 ultrasonic sensors, an L293D motor driver, two DC motors, LEDs, and a buzzer.

### Hardware Implementation

The three ultrasonic sensors are arranged as:

- Front sensor for detecting obstacles ahead.
- Left sensor for measuring available space on the left.
- Right sensor for measuring available space on the right.

The two DC motors are connected through the L293D motor driver. The Arduino controls the motor direction using digital output pins and controls the motor speed using PWM.

### Firmware Implementation

The firmware is written in Arduino C/C++.

The program continuously performs the following steps:

1. Read the front ultrasonic sensor.
2. Read the left ultrasonic sensor.
3. Read the right ultrasonic sensor.
4. Display the measured distances on the Serial Monitor.
5. Check whether the front path is clear.
6. Move forward if no obstacle is detected.
7. Stop and activate the warning indicators when an obstacle is detected.
8. Compare the left and right distances.
9. Turn toward the side with more available space.
10. Reverse and perform a recovery turn if both sides are blocked.

### Distance Calculation

The HC-SR04 measures the time taken by an ultrasonic pulse to travel to an obstacle and return.

The distance is calculated using:

Distance = (Echo Time × Speed of Sound) / 2

The division by 2 is required because the measured time represents the complete journey of the ultrasonic pulse to the obstacle and back.

### Navigation Logic

The robot uses a 25 cm obstacle threshold.

If:

Front Distance > 25 cm

the robot moves forward.

If:

Front Distance <= 25 cm

the robot considers the path blocked and compares the left and right distances.

If:

Left Distance > Right Distance

the robot turns left.

If:

Right Distance > Left Distance

the robot turns right.

If both left and right distances are also below the obstacle threshold, the robot reverses and performs a recovery turn.

### Motor Control

The Arduino sends control signals to the L293D motor driver.

The left motor uses Arduino pins D5, D6, and D9.

The right motor uses Arduino pins D7, D8, and D10.

The enable pins use PWM to control the motor speed.

### Source Code

The complete Arduino source code is available in:

src/guide_robot.ino

---

## 5. Demonstration

The demonstration covers the complete obstacle-detection and navigation process using the Tinkercad simulation.

### Demonstration 1 — Clear Path

The ultrasonic sensors are given distances greater than the 25 cm obstacle threshold.

Expected behavior:

- Green LED turns ON.
- Red LED remains OFF.
- Buzzer remains OFF.
- Both motors run in the forward direction.
- Serial Monitor displays the measured distances.

### Demonstration 2 — Front Obstacle Detected

The front sensor is given a distance of 25 cm or less.

Expected behavior:

- Robot stops.
- Green LED turns OFF.
- Red LED turns ON.
- Buzzer provides an audible warning.
- Serial Monitor displays "OBSTACLE DETECTED".

### Demonstration 3 — Left Side Has More Space

Example sensor readings:

Front = 10 cm
Left = 60 cm
Right = 20 cm

Expected behavior:

The robot detects the front obstacle, compares the side distances, and turns left because the left side has more available space.

### Demonstration 4 — Right Side Has More Space

Example sensor readings:

Front = 10 cm
Left = 20 cm
Right = 60 cm

Expected behavior:

The robot turns right because the right side has more available space.

### Demonstration 5 — Both Sides Blocked

Example sensor readings:

Front = 10 cm
Left = 10 cm
Right = 10 cm

Expected behavior:

The robot reverses and performs a recovery turn before continuing.

### Demonstration Video

Demo Video: (https://drive.google.com/file/d/1qGuynbudMY9ZiOW35StCeALj3npadTbp/view?usp=sharing)

### Tinkercad Simulation

Tinkercad Circuit: https://www.tinkercad.com/things/bRa7oBH2uab-guide-bot
---

## 6. Final Result

### Working

- Three ultrasonic sensors successfully provide front, left, and right distance measurements.
- The Arduino processes the sensor readings and makes navigation decisions.
- The robot moves forward when the front path is clear.
- The robot detects obstacles using a 25 cm threshold.
- The robot compares left and right distances when an obstacle is detected.
- The robot turns toward the side with more available space.
- The robot performs a reverse and recovery turn when both sides are blocked.
- The L293D motor driver controls the two DC motors.
- Green and red LEDs provide visual status feedback.
- The buzzer provides an audible obstacle warning.
- Sensor readings and navigation decisions are displayed through the Serial Monitor.

### Known Issues

- The current implementation is a Tinkercad simulation and has not been tested on a physical robot.
- Motor movement is represented through the simulated DC motors rather than an actual moving robot chassis.
- Turning duration is controlled using fixed delay values.
- The navigation system does not use wheel encoders for accurate distance or angle measurement.
- The system does not create or maintain a map of the environment.

**Demo:** (https://drive.google.com/file/d/1qGuynbudMY9ZiOW35StCeALj3npadTbp/view?usp=sharing)

![Final Build] https://drive.google.com/file/d/1tRbbRX7NOy0bPK0gEQvLqoFW7FRKIVTx/view?usp=sharing

---

## 7. Limitations & Improvements

### Limitations

- The project is currently implemented as a simulation in Tinkercad.
- The navigation system uses fixed distance thresholds.
- Motor turning is controlled using fixed time delays.
- No wheel encoders are currently used.
- The robot does not perform mapping or localization.
- The system has not yet been tested in a physical environment.

### Next Steps

With additional development time, the project could be improved by:

1. Building and testing the physical robot.
2. Adding wheel encoders for more accurate movement and turning.
3. Implementing smoother motor speed control.
4. Improving obstacle-avoidance behavior.
5. Adding mapping and localization capabilities.
6. Adding more advanced assistive feedback mechanisms.
7. Testing the system with different environments and obstacle configurations.
---

## 8. Key Learnings

Through this project, I learned the fundamentals of Arduino-based embedded systems and sensor-driven robotics.

The main concepts learned were:

- Arduino programming using C/C++.
- Digital input and output.
- PWM-based motor speed control.
- Ultrasonic distance sensing using HC-SR04 sensors.
- Motor control using the L293D driver.
- Using conditional statements for navigation decisions.
- Creating reusable functions for robot movement.
- Using the Serial Monitor for debugging and monitoring sensor values.
- Designing and testing electronic circuits in Tinkercad.
- Converting sensor data into real-time navigation decisions.
- Testing different obstacle scenarios systematically.

A key learning from this project was understanding how a robot can use sensor measurements to make autonomous decisions about its movement.
---

## 9. Repository Structure

```text
nischay-sinha/
├── README.md
├── src/
│   └── guide_robot.ino
├── hardware/
│   └── pinout.md
├── docs/
│   └── images/
│       ├── system-overview.png
│       ├── circuit.png
│       ├── obstacle-detected.png
│       └── serial-monitor.png
├── tests/
│   └── test-results.md
└── media/
    └── demo-link.md
```
