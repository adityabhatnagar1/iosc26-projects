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
