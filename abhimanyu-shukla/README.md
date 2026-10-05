<!-- 📌 Abhimanyu Shukla: edit ONLY inside this folder (/abhimanyu-shukla). Fill in every section below, replacing [placeholders] with your own words. Delete this comment when you start. -->

# Manushya-v1
> One sentence: what you built + what it does.

**Track:** Manushya-v1(mini dorne) 
**Candidate:** Abhimanyu Shukla  
**Github Username**: abhimanyushukla1214-design  
**Phone Number**: 9288531262 
**Email ID**: abhimanyushukla1214@gmail.com 

---

## 1. Overview

### What & Why
I built Manushya V1, a custom micro-quadcopter flight platform developed completely from the hardware and firmware level up.It runs on an ESP32 microcontroller paired with an MPU-6050 6-axis IMU (accelerometer and gyroscope).

It calculates tilt angles in real time and uses a custom PID loop to adjust motor speeds via PWM for stable flight. The ESP32 handles flight calculations on one core and Wi-Fi control with telemetry on the other, featuring automatic motor cutoffs for signal loss or extreme tilts while leaving room for future sensor and telemetry additions.

I built it as the critical first stepping stone toward my dream humanoid project, Manushya, which requires mastering dynamic physical balance, PID control theory, and embedded hardware before layering on high-level AI brains. It also represents the direct evolution of my electronics journey since fourth grade, taking my years of hands-on circuit and soldering experience and applying it to complex, autonomous robotics.


### Expected Outcome
I built this to get hands-on experience with PID tuning, PWM control, communication protocols, failsafes, and power circuit design. Learning these basics helps prepare me to build a larger 8-inch ai integrated autonomous BLDC drone in my second semester that will use ultrasonic sensors and onboard AI for obstacle avoidance and navigation.

---

## 2. Requirements

### Hardware

| Component | Description and purpose | Quantity|
| :--- | :--- |
| **Microcontroller** | ESP32-WROOM-32 (Dual Core 240MHz, 2.4GHz Wi-Fi) | 1 |
| **IMU** | MPU-6050 (3-Axis Gyroscope + 3-Axis Accelerometer) | 1 |
| **Motors** | 4x Coreless Brushed DC Motors (2x CW, 2x CCW) | 4 |
| **Switches / Drivers**| smd si2301 MOSFETs | 4 |
| **Power Source** | 1S 3.7V LiPo Battery (800 mAh) | 4 |
| **Frame** | Lightweight DIY / 3D-Printed Frame | 1 |

### Software
### Software & Libraries

| Tool / Library | Version | Purpose |
| :--- | :--- | :--- |
| **Arduino IDE** | `2.3.10` | Firmware development, board flashing, and serial debugging |
| **ESP32 by espressif** | `3.3.12` | Board support package, FreeRTOS dual-core API, and hardware timers |
| **Wire.h** | Built-in | Direct I2C hardware bus communication (400 kHz) to read raw MPU-6050 registers |
| **WiFi.h** | Built-in | Manages the ESP32 standalone Soft-AP wireless access point |
| **WiFiUdp.h** | Built-in | Low-latency packet reception on port 4210 for real-time mobile app control |
| **WebServer.h** | Built-in | Hosts the zero-install HTTP browser dashboard and touch joystick UI on port 80 |


### Constraints

| Category | Constraint | Impact / Mitigation |
| :--- | :--- | :--- |
| **Budget** | Low-cost hobbyist components | Relies on brushed coreless motors and standard ESP32 rather than specialized UAV stacks (e.g., Pixhawk/Betaflight boards). |
| **Hardware** | Zero external flight libraries | Uses direct register read/writes via `Wire.h` to minimize memory overhead and eliminate library latency. |
| **Power** | 1S LiPo battery (~3.7V) | Requires dedicated step-down/LDO regulation for stable 3.3V logic; rapid voltage sag under full motor throttle can cause MCU brownouts if unisolated. |
| **Compute & Timing** | Real-time PID loop vs. Wi-Fi overhead | ESP32 soft-AP and web serving must remain strictly non-blocking so the complementary filter and motor PWM updates maintain an uninterrupted update rate. |
| **Safety / Range** | Local Wi-Fi range (~20–30 meters) | Hard cutoff timeout (`FAILSAFE_MS = 500`) automatically disarms all motors upon signal drop or packet loss to avoid flyaways. |

---

## 3. Design

### System Overview
The system forms a continuous closed-loop feedback pipeline:
1. **Pilot Inputs & Commands:** A web browser or UDP client on a smartphone sends throttle, pitch, roll, and yaw demands over Wi-Fi (Soft-AP mode).
2. **Attitude Sensing:** The MPU-6050 samples angular velocity and linear acceleration over the I2C bus at 400 kHz.
3. **State Estimation:** A complementary filter blends high-pass gyro integration with low-pass accelerometer tilt angles to calculate clean pitch and roll estimates ($\alpha = 0.98$).
4. **PID Control Loop:** The firmware computes the error between pilot setpoints and estimated angles, generating individual PID correction values for pitch, roll, and yaw.
5. **Motor Mixing & Actuation:** Corrections are mixed with baseline throttle across an X-frame geometry and translated into 20 kHz PWM signals via the ESP32 `ledc` hardware peripheral to spin four coreless DC motors.

![System Diagram](<img width="3000" height="2875" alt="Circuit_image " src="https://github.com/user-attachments/assets/e58b71ff-13c4-494d-a3fd-aee62e02b41e" />
)

### Key Decisions
| Subsystem | Chosen Solution | Why | Rejected Alternatives | Why Rejected |
| :--- | :--- | :--- | :--- | :--- |
| **Telemetry & Control** | Built-in ESP32 Soft-AP (Web + UDP) | Zero external apps needed; zero added hardware cost; native Wi-Fi stack on ESP32. | 2.4 GHz NRF24L01 / dedicated RC receiver | Requires extra transmitter hardware, separate receiver modules, and PCB trace complexity. |
| **Sensor Interface** | Direct I2C register access via `Wire.h` | Minimal flash footprint, zero third-party library overhead, deterministic timing. | Adafruit MPU-6050 / DMP library | Heavy abstractions, slower register polling, unpredictable execution overhead for high-rate loops. |
| **Motor PWM Frequency** | 20 kHz Hardware PWM (`ledc`) | Ultrasonic frequency eliminates audible motor whine and ensures smooth current delivery to coreless coils. | Low-frequency PWM (500 Hz – 1 kHz) | Causes loud acoustic buzzing and inefficient switching losses across small brushed motors. |

---

## 4. Implementation

* **Hardware & Circuits:** Powered by an ESP32 Dev Module (240 MHz) and an MPU-6050 6-DOF IMU over 3.3V logic. Four brushed coreless DC motors are driven via low-side N-channel MOSFET switches with flyback diodes on pins `GPIO 32` (M1, CCW), `GPIO 33` (M2, CW), `GPIO 26` (M3, CCW), and `GPIO 25` (M4, CW).
* **Protocols & Communication:** Hardware I2C runs at 400 kHz on `GPIO 21` (SDA) and `GPIO 22` (SCL). The ESP32 hosts a local Wi-Fi SoftAP (`MyDrone`) serving an embedded HTML5 touch-joystick UI via HTTP (Port 80) and receiving real-time command packets over UDP (Port 4210).
* **Algorithms & Calculations:**
  * *Attitude Estimation (Complementary Filter):*  
    $$\theta = 0.98 \cdot (\theta + \omega_{\text{gyro}} \cdot \Delta t) + 0.02 \cdot \theta_{\text{accel}}$$
  * *PID Stabilization:* Computes error between stick setpoints and estimated angles with anti-windup integral clamping ($\pm 50$).
  * *X-Frame Motor Mixer:*  
    $$M_1 = T + P - R + Y \quad\mid\quad M_2 = T - P - R - Y$$  
    $$M_3 = T - P + R + Y \quad\mid\quad M_4 = T + P + R - Y$$
  * *Failsafe:* Disarms all motors if packet interval exceeds 500 ms or throttle drops below 2%.

*Source File:* [`src/firmware.ino`]

---

## 5. Demonstration

https://github.com/user-attachments/assets/a4925777-9f74-4d91-8fbb-c29e23fef082

---

## 6. Final Result

### Working
drone body
<img width="4080" height="2296" alt="20261004_155501" src="https://github.com/user-attachments/assets/ef84b83c-a156-4b8a-9dc7-26599b6daa65" />


https://github.com/user-attachments/assets/c6b1f3e2-fec8-4cdd-9adf-3e791b535d15


<img width="2340" height="1080" alt="Screenshot_20261004_160238_Samsung Browser" src="https://github.com/user-attachments/assets/47c49529-2def-4a52-9aa3-23ba4e1ae750" />
wifi based control

### Known Issues
- need to tune pid manually

**Demo:** 

https://github.com/user-attachments/assets/a4925777-9f74-4d91-8fbb-c29e23fef082



![Final Build](<img width="4080" height="2296" alt="20261004_155501" src="https://github.com/user-attachments/assets/894f16cd-c2e8-4a65-908e-1c10614f3b17" />
)

---

## 7. Limitations & Improvements

**Limitations:** [Manual PID Tuning]

**Next Steps:** First to make its fly smooth and then Integrating with sensors then train with ai and try to make it fully autonomous.

---

## 8. Key Learnings

PID meaning, PWM channels, WIFI based control, nrf transceiver use, working with sensors like mpu6050 and bmp280 for accelerometer, gyroscope and pressure, arduino ide use and coding, git and github basics, drone motors orientation, thrust and weight impact. 

---

## 9. Repository Structure

```text
project-name/
├── README.md
├── src/
├── hardware/
├── docs/
├── tests/
└── media/
```

# Manushya V1 

**Manushya V1** is an open-source, Wi-Fi-controlled micro-quadcopter built from the ground up using an ESP32 microcontroller, an MPU6050 6-DOF IMU, and coreless DC motors driven by MOSFET switches. It incorporates real-time attitude estimation via sensor fusion, dual-axis PID control loops, and an integrated Wi-Fi Access Point accepting low-latency UDP flight commands from any smartphone controller app.

---


---

##  Features

- **Standalone ESP32 Access Point:** Broadcasts its own private Wi-Fi network (`ESP32_Drone`) — no external router needed.
- **Low-Latency UDP Communication:** Real-time parsing of incoming throttle, roll, pitch, and yaw commands over UDP port `8888`.
- **Automatic Sensor Calibration:** Samples and zeroes out accelerometer and gyroscope biases over 1,000 iterations on every cold boot.
- **Attitude Stabilization:** Sensor fusion via complementary filter coupled with a tuned proportional-integral-derivative (PID) loop running at ~250 Hz.
- **Fail-Safe Mechanism:** Automatic motor cut-off if signal loss exceeds 500 ms to prevent flyaways.
- **Quad-X Motor Mixer:** Dynamic PWM mixing mapped across four MOSFET-driven coreless motors.

---

##  Hardware & Components

| Component | Description / Specification |
| :--- | :--- |
| **Microcontroller** | ESP32-WROOM-32 (Dual Core 240MHz, 2.4GHz Wi-Fi) |
| **IMU** | MPU-6050 (3-Axis Gyroscope + 3-Axis Accelerometer) |
| **Motors** | 4x Coreless Brushed DC Motors (2x CW, 2x CCW) |
| **Switches / Drivers**| 4x smd MOSFETs |
| **Power Source** | 1S 3.7V LiPo Battery (800 mAh) |
| **Frame** | Lightweight DIY / 3D-Printed Frame |

---

##  Wiring & Pinout Reference

| Peripheral | ESP32 GPIO | Description |
| :--- | :--- | :--- |
| **MPU6050 SDA** | `GPIO 21` | I2C Serial Data |
| **MPU6050 SCL** | `GPIO 22` | I2C Serial Clock |
| **Motor 1 (Front-Right, CCW)** | `GPIO 32` | PWM Channel 0 |
| **Motor 2 (Rear-Right, CW)** | `GPIO 33` (RX2) | PWM Channel 1 |
| **Motor 3 (Rear-Left, CCW)** | `GPIO 25` (TX2) | PWM Channel 2 |
| **Motor 4 (Front-Left, CW)** | `GPIO 26` | PWM Channel 3 |

---

##  Software Prerequisites & Installation

1. Install [Arduino IDE](https://www.arduino.cc/en/software) (version 2.0+ recommended).
2. Add ESP32 board support via **Tools > Board > Boards Manager**:
   - Search for `esp32` by **Espressif Systems** and install.
3. Install the required libraries via **Sketch > Include Library > Manage Libraries**:
   - `Adafruit MPU6050`
   - `Adafruit BusIO`
   - `Adafruit Unified Sensor`
4. Open `firmware/Manushya_V1.ino`.
5. Select **ESP32 Dev Module** from the board list, plug in your board via micro-USB, select the COM port, and click **Upload**.

---

##  Flight & Controller Configuration

1. **Power Up:** Connect the 1S LiPo battery. Place the drone **completely flat and still** on the floor for 3 seconds while the calibration routine computes gyro/accel offsets.
2. **Connect Phone to Drone:**
   - SSID: `MyDrone`
   - Password: `12345678`
3. **Configure App:**
   - Open any standard UDP controller app (e.g., *UDP WiFi Remote*, *RoboRemo*, or *Packet Sender*).
   - Target IP: `192.168.4.1`
   - Port: `8888`
   - Expected packet string:  
     `T:<throttle>,R:<roll>,P:<pitch>,Y:<yaw>`  
     *(e.g., `T:110,R:0.0,P:0.0,Y:0.0`)*

---

##  Safety Notes

- Always remove propellers when testing motor directions or uploading firmware on the bench.
- Ensure the center of gravity (CoG) is centered relative to all 4 motors for stable hovering.
- Always monitor 1S LiPo battery voltage to prevent over-discharging below 3.3V.

---

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

