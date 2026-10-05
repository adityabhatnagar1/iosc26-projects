
# Simple Obstacle-Avoiding Guide Robot for Visually Impaired Navigation

> An Arduino-based obstacle-avoidance robot that uses a servo-mounted ultrasonic sensor to scan the surroundings and choose a clearer direction when an obstacle is detected.

**Track:** IOT/ROBOTICS  
**Candidate:** Nivranj Pahwa  
**Github Username**: nivranjpahwa9144   
**Phone Number**: 9871958280  
**Email ID**: nivranjpahwa@gmail.com  

---

## 1. Overview

### What & Why
This project is a simple obstacle-avoidance robot designed to detect obstacles in front of it and decide which direction has more space to move towards. I chose this idea because I had already built and tested a similar robot during my time at IIT Mandi, so I had a practical understanding of how the sensor, servo and motors work together. For the simulation, I recreated the main working of the robot in Tinkercad using an Arduino UNO, HC-SR04 ultrasonic sensor and a servo motor.

### Expected Outcome
The main goal was to make the robot continuously scan its surroundings, measure the distance to obstacles and make a basic movement decision based on the available space. I also wanted the simulation to give actual ultrasonic readings so that the decision-making could be seen through the Serial Monitor rather than using fixed or fake distances.

---

## 2. Requirements

### Hardware

| Component | Qty | Purpose |
|---|---:|---|
| Arduino UNO | 1 | Main controller for the robot |
| HC-SR04 Ultrasonic Sensor | 1 | Measures distance to obstacles |
| Servo Motor | 1 | Rotates the ultrasonic sensor to scan different directions |
| L293D Motor Driver | 1 | Controls the DC motors |
| DC Gear Motors | 2 | Drive the robot |
| Wheels | 2 | Provide movement |
| Castor Wheel | 1 | Supports the front/rear of the robot and helps it move smoothly |
| Robot Chassis | 1 | Holds the robot components |
| Battery Holder | 1 | Holds and supplies power from the batteries |
| Arduino USB Cable | 1 | Used to program and power the Arduino during testing |
| Jumper Wires | As required | Used for electrical connections |
| Electrical Tape | As required | Used for securing and insulating connections |
| Soldering Materials | As required | Used to make permanent electrical connections |

### Software

| Tool / Library | Version | Purpose |
|---|---|---|
| Tinkercad Circuits | — | Used to build and simulate the robot circuit |
| Arduino IDE | — | Used to write and upload the Arduino program |
| Arduino C/C++ | — | Used to program the obstacle detection and movement logic |
| Servo Library | — | Used to control the servo and rotate the ultrasonic sensor |

**Constraints:** The project was completed with the hardware available to me and within the limited submission time. The simulation mainly demonstrates the ultrasonic sensing, scanning and decision-making part of the robot.

---

## 3. Design

### System Overview
The robot uses an Arduino UNO as the main controller. An HC-SR04 ultrasonic sensor is mounted on a servo motor, which allows the sensor to rotate and scan different directions instead of only measuring the distance in one fixed direction.
While the servo rotates, the ultrasonic sensor measures the distance to nearby objects. The Arduino reads these measurements and uses them to decide which direction has more available space. When an obstacle is detected, the Arduino sends the required signals to the L293D motor driver, which then controls the DC motors and changes the robot's direction


### Key Decisions
I decided to use one ultrasonic sensor mounted on a servo instead of using multiple ultrasonic sensors. This makes the circuit simpler while still allowing the robot to scan different directions.
The Arduino handles the sensor readings and decides what the robot should do, while the servo changes the direction in which the sensor is looking. The L293D motor driver is used to control the DC motors because the Arduino cannot directly provide enough current to drive them.
The main idea is to continuously scan the surroundings, compare the distance readings and move towards a direction with more available space when an obstacle is detected

---

## 4. Implementation



### Setup

The robot was assembled using an Arduino UNO, HC-SR04 ultrasonic sensor, servo motor, L293D motor driver and two DC motors. The ultrasonic sensor was mounted on the servo so that it could rotate and scan different directions. The motors were connected through the L293D motor driver, while the Arduino handled the sensor readings, servo movement and decision-making.

For the simulation, the same basic setup was recreated in Tinkercad. The Arduino program was uploaded to the simulated circuit and the sensor readings were observed through the Serial Monitor.

### Core Logic

The servo rotates the ultrasonic sensor through different angles. At each angle, the HC-SR04 takes an actual distance measurement and sends the reading to the Arduino.

The Arduino compares the measured distances from different directions. If the path is clear, the robot continues moving forward. If an obstacle is detected, the program checks which direction has greater clearance and uses that direction for the turn.

The Serial Monitor was used during testing to check the actual distance readings and observe the decisions being made by the program.

### Testing

The simulation was tested with different obstacle positions and distances. The ultrasonic sensor produced different readings depending on the position of the obstacle, and the robot's decision changed accordingly.

The physical version of the robot was also previously built and tested during IIT Mandi, where the obstacle-avoidance setup used an ultrasonic sensor mounted on a servo.

**Source Code:** `src/obstacle_avoidance.ino` 


---

## 5. Demonstration


The project was demonstrated using a Tinkercad simulation along with the physical prototype that I built and tested during IIT Mandi.

### 1. Obstacle Detection

The HC-SR04 ultrasonic sensor is mounted on a servo motor and rotates through different angles to scan the surroundings. At each angle, the sensor takes an actual distance measurement. The Arduino reads these values and identifies whether an obstacle is present.

The Tinkercad Serial Monitor was used to observe these real-time distance readings during the simulation.


### 2. Navigation and Decision Making

The Arduino compares the distances measured in different directions. If the path is clear, the robot can continue forward. When an obstacle is detected, the program checks the available clearance in different directions and selects the direction with more space for the next movement.

This allows the robot to react to obstacles based on the sensor readings rather than using fixed distance values.

### 3. Physical Prototype

A physical version of the obstacle-avoidance robot was built and tested during IIT Mandi. The prototype used an Arduino, ultrasonic sensor mounted on a servo motor, DC motors and a motor driver. The physical testing helped verify the basic obstacle-detection and avoidance concept.

**Physical Prototype – Video :** [Watch Video ](https://youtu.be/9JG4JooUQ-Q)
### 4. Tinkercad Simulation

The complete sensing and decision-making logic was recreated in Tinkercad. The simulation allows the ultrasonic sensor readings and the decisions made by the Arduino program to be observed through the Serial Monitor.

**Tinkercad Simulation:** [Open Tinkercad Simulation](https://www.tinkercad.com/things/bGbim250NyA-iosc-project)
### 5. Assistive Technology Application

The project is based on a concept that can be developed further for assistive navigation. A similar system could detect obstacles in the path of a visually impaired user and provide an appropriate response through a robotic navigation system. The current project demonstrates the basic obstacle-sensing and decision-making part of this idea.

## 6. Final Result



### Working

- The ultrasonic sensor successfully measures the actual distance to obstacles at different angles.
- The servo allows the sensor to scan multiple directions, and the Arduino compares the readings to identify a clearer direction.
- The Tinkercad simulation successfully shows the sensor readings and the resulting obstacle-detection and direction decisions through the Serial Monitor.

### Known Issues

- The Tinkercad simulation mainly demonstrates the sensing and decision-making logic and does not visually represent the complete physical robot moving through a maze.
- The current prototype uses a single ultrasonic sensor, so the robot scans different directions sequentially instead of sensing all directions at the same time.

### Demo

Physical Prototype –[ Video 2](https://youtube.com/shorts/uMZt43qh9w0?feature=share)


## 7. Limitations & Improvements

### Limitations

One of the main limitations of the current setup is that I am using only one ultrasonic sensor. Since it is mounted on a servo, the sensor has to scan different directions one by one instead of checking everything at the same time.

The current decision-making is also fairly simple. It mainly compares the distance readings and chooses the direction with more space, so it would not be enough for more complicated environments or proper path planning.

Another limitation is that the Tinkercad simulation focuses mainly on the sensing and decision-making part. It does not show the complete physical robot moving around a real maze or obstacle course.

### Next Steps

If I had more time, I would improve the sensing part by adding more sensors so the robot could get a better idea of what is happening around it without having to scan everything sequentially.

I would also work on a better navigation algorithm so the robot could handle more complicated paths instead of simply choosing whichever direction has more space.

Finally, I would test the robot in a proper maze or obstacle course and look into adding audio or vibration feedback, which would make the project more relevant to its intended use as an assistive navigation system.

## 8. Key Learnings


Building this project helped me understand how different hardware components work together instead of just using them individually. I got a better understanding of how an ultrasonic sensor measures distance, how a servo can be used to scan different directions, and how a motor driver allows the Arduino to control DC motors.

I also learned that getting the circuit and code right is only half the work. A small wiring mistake or an incorrect sensor reading can completely change the robot's behaviour, so testing each part separately was really useful.

Working with the Tinkercad simulation also helped me understand the debugging process better. Looking at the actual sensor readings in the Serial Monitor made it much easier to figure out what the robot was detecting and why it was making a particular decision.


## 9. Repository Structure


```text
nivranj-pahwa/
├── README.md
├── src/
│   └── obstacle_avoidance.ino
├── hardware/
│   ├── Hardware1.jpeg
│   ├── Hardware2.jpeg
│   ├── Hardware3.jpeg
│   └── tinkercad-circuit.png
└── docs/
    └── images/
        └── serial-monitor.png
