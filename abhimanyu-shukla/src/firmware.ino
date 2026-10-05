/*Esp32 wroom32 wifi based mini drone

*/
#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <WebServer.h>

// ---------------------------------------------------------------
// EDIT THESE: pins (already matched to your diagram)
// ---------------------------------------------------------------
#define SDA_PIN   21
#define SCL_PIN   22
#define INT_PIN   14

#define M1_PIN    32   // front-right, CCW
#define M2_PIN    33  // back-right,  CW
#define M3_PIN    26  // back-left,   CCW
#define M4_PIN    25  // front-left,  CW

// ---------------------------------------------------------------
// EDIT THESE: WiFi access point the drone creates
// ---------------------------------------------------------------
const char* WIFI_SSID = "MyDrone";
const char* WIFI_PASS = "drone1234";   // must be 8+ characters
const unsigned int UDP_PORT = 4210;

// ---------------------------------------------------------------
// Safety / tuning constants - EDIT AFTER BENCH TESTING
// ---------------------------------------------------------------
const unsigned long FAILSAFE_MS   = 500;   // cut motors if no packet in this long
const int   MAX_THROTTLE_PWM      = 255;   // 8-bit PWM ceiling
const int   MIN_SPIN_PWM          = 60;    // PWM below which motors barely spin (tune this!)
const float PID_KP_ROLL  = 0.72;
const float PID_KI_ROLL  = 0.00;
const float PID_KD_ROLL  = 0.02;
const float PID_KP_PITCH = 0.72;
const float PID_KI_PITCH = 0.0;
const float PID_KD_PITCH = 0.02;
const float PID_KP_YAW   = 1.2;

// ---------------------------------------------------------------
// MPU6050 registers
// ---------------------------------------------------------------
#define MPU6050_ADDR      0x68
#define REG_PWR_MGMT_1    0x6B
#define REG_GYRO_CONFIG   0x1B
#define REG_ACCEL_CONFIG  0x1C
#define REG_ACCEL_XOUT_H  0x3B

// ---------------------------------------------------------------
// Globals
// ---------------------------------------------------------------
WiFiUDP udp;
char packetBuffer[64];
WebServer server(80);   // browser control page + endpoints, port 80 (default http)

volatile float throttleIn = 0;   // 0-100
volatile float rollIn     = 0;   // -100 to 100
volatile float pitchIn    = 0;   // -100 to 100
volatile float yawIn      = 0;   // -100 to 100
volatile bool  armed      = false;
unsigned long lastPacketTime = 0;

float gyroOffsetX = 0, gyroOffsetY = 0, gyroOffsetZ = 0;

float pitchAngle = 0, rollAngle = 0;   // complementary-filter estimate (degrees)
unsigned long lastLoopTime = 0;

// PID state
float rollErrIntegral = 0, rollErrPrev = 0;
float pitchErrIntegral = 0, pitchErrPrev = 0;

// ESP32 LEDC PWM settings (core v3.x API: attach directly to the pin,
// no manual channel numbers needed)
const int PWM_FREQ = 20000;   // 20kHz, above audible range
const int PWM_RES  = 8;       // 0-255

// =====================================================================
void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(INT_PIN, INPUT);

  setupMotors();
  setupMPU6050();
  calibrateGyro();
  setupWiFiAndUDP();
  setupWebServer();

  lastLoopTime = millis();
  Serial.println("Setup complete. Send ARM over UDP to enable motors.");
}

// =====================================================================
void loop() {
  handleIncomingUDP();
  server.handleClient();

  // Safety: if we haven't heard from the controller recently, disarm.
  if (armed && (millis() - lastPacketTime > FAILSAFE_MS)) {
    armed = false;
    Serial.println("FAILSAFE: no control packet received, motors disarmed.");
  }

  float dt = (millis() - lastLoopTime) / 1000.0;
  if (dt <= 0) dt = 0.001;
  lastLoopTime = millis();

  updateAttitudeEstimate(dt);

  if (armed) {
    stabilizeAndDrive(dt);
  } else {
    setAllMotors(0, 0, 0, 0);
  }
}

// =====================================================================
// Motor setup / output
// =====================================================================
void setupMotors() {
  ledcAttach(M1_PIN, PWM_FREQ, PWM_RES);
  ledcAttach(M2_PIN, PWM_FREQ, PWM_RES);
  ledcAttach(M3_PIN, PWM_FREQ, PWM_RES);
  ledcAttach(M4_PIN, PWM_FREQ, PWM_RES);

  setAllMotors(0, 0, 0, 0);
}

void setAllMotors(int m1, int m2, int m3, int m4) {
  ledcWrite(M1_PIN, constrain(m1, 0, MAX_THROTTLE_PWM));
  ledcWrite(M2_PIN, constrain(m2, 0, MAX_THROTTLE_PWM));
  ledcWrite(M3_PIN, constrain(m3, 0, MAX_THROTTLE_PWM));
  ledcWrite(M4_PIN, constrain(m4, 0, MAX_THROTTLE_PWM));
}

// =====================================================================
// MPU6050 setup / calibration / reading
// =====================================================================
void setupMPU6050() {
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000);

  writeMPURegister(REG_PWR_MGMT_1, 0x00);   // wake up
  delay(100);
  writeMPURegister(REG_GYRO_CONFIG, 0x00);  // +/-250 deg/s
  writeMPURegister(REG_ACCEL_CONFIG, 0x00); // +/-2g

  uint8_t who = readMPURegister8(0x75);
  if (who == 0x68) {
    Serial.println("MPU6050 I2C connection [OK].");
  } else {
    Serial.println("MPU6050 I2C connection [FAIL]. Check wiring before flying!");
  }
}

void writeMPURegister(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(reg);
  Wire.write(value);
  Wire.endTransmission();
}

uint8_t readMPURegister8(uint8_t reg) {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom((int)MPU6050_ADDR, 1, true);
  return Wire.available() ? Wire.read() : 0xFF;
}

void readMPURaw(int16_t &ax, int16_t &ay, int16_t &az,
                int16_t &gx, int16_t &gy, int16_t &gz) {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(REG_ACCEL_XOUT_H);
  Wire.endTransmission(false);
  Wire.requestFrom((int)MPU6050_ADDR, 14, true);

  ax = (Wire.read() << 8) | Wire.read();
  ay = (Wire.read() << 8) | Wire.read();
  az = (Wire.read() << 8) | Wire.read();
  Wire.read(); Wire.read();          // skip temperature
  gx = (Wire.read() << 8) | Wire.read();
  gy = (Wire.read() << 8) | Wire.read();
  gz = (Wire.read() << 8) | Wire.read();
}

// Averages gyro readings while the drone is still, to remove bias.
// KEEP THE DRONE COMPLETELY STILL AND LEVEL DURING THIS STEP.
void calibrateGyro() {
  Serial.println("Calibrating gyro - keep the drone completely still and level...");
  const int N = 1000;
  long sumX = 0, sumY = 0, sumZ = 0;
  int16_t ax, ay, az, gx, gy, gz;

  for (int i = 0; i < N; i++) {
    readMPURaw(ax, ay, az, gx, gy, gz);
    sumX += gx;
    sumY += gy;
    sumZ += gz;
    delay(3);
  }
  gyroOffsetX = sumX / (float)N;
  gyroOffsetY = sumY / (float)N;
  gyroOffsetZ = sumZ / (float)N;

  Serial.println("Gyro calibration done.");
  Serial.print("Offsets: ");
  Serial.print(gyroOffsetX); Serial.print(", ");
  Serial.print(gyroOffsetY); Serial.print(", ");
  Serial.println(gyroOffsetZ);
}

// Complementary filter: combines accelerometer (stable long-term,
// noisy short-term) with gyro (smooth short-term, drifts long-term).
void updateAttitudeEstimate(float dt) {
  int16_t ax, ay, az, gx, gy, gz;
  readMPURaw(ax, ay, az, gx, gy, gz);

  float gxDegS = (gx - gyroOffsetX) / 131.0;   // 131 LSB/(deg/s) at +/-250dps
  float gyDegS = (gy - gyroOffsetY) / 131.0;

  float accelPitch = atan2(-ax, sqrt((long)ay * ay + (long)az * az)) * 180.0 / PI;
  float accelRoll  = atan2(ay, az) * 180.0 / PI;

  const float ALPHA = 0.98;
  pitchAngle = ALPHA * (pitchAngle + gyDegS * dt) + (1 - ALPHA) * accelPitch;
  rollAngle  = ALPHA * (rollAngle  + gxDegS * dt) + (1 - ALPHA) * accelRoll;
}

// =====================================================================
// Stabilization + motor mixing
// =====================================================================
void stabilizeAndDrive(float dt) {
  // Desired angle comes from the stick input (small tilt range)
  float targetPitch = pitchIn * 0.3;   // stick 100 -> ~30 degrees target tilt
  float targetRoll   = rollIn  * 0.3;

  float pitchError = (targetPitch - pitchAngle);
  float rollError  = (targetRoll  - rollAngle);

  pitchErrIntegral += pitchError * dt;
  rollErrIntegral  += rollError  * dt;
  pitchErrIntegral = constrain(pitchErrIntegral, -50, 50); // anti-windup
  rollErrIntegral  = constrain(rollErrIntegral,  -50, 50);

  float pitchDeriv = (pitchError - pitchErrPrev) / dt;
  float rollDeriv  = (rollError  - rollErrPrev)  / dt;
  pitchErrPrev = pitchError;
  rollErrPrev  = rollError;

  float pitchCorrection = PID_KP_PITCH * pitchError
                         + PID_KI_PITCH * pitchErrIntegral
                         + PID_KD_PITCH * pitchDeriv;
  float rollCorrection  = PID_KP_ROLL  * rollError
                         + PID_KI_ROLL  * rollErrIntegral
                         + PID_KD_ROLL  * rollDeriv;
  float yawCorrection   = PID_KP_YAW * yawIn * 0.1;  // simple rate-only yaw

  // Base throttle: 0-100 input mapped to PWM range (with a floor so
  // motors don't stall out under correction at low throttle)
  float basePWM = map(throttleIn, 0, 100, 0, MAX_THROTTLE_PWM);

  // Standard X-frame mixing.
  // NOTE: signs here are a starting assumption based on your layout -
  // if a stick input tilts the drone the WRONG way during bench
  // testing (props off, watch motor speed changes), flip the sign of
  // that term.
  float m1 = basePWM + pitchCorrection - rollCorrection + yawCorrection; // front-right CCW
  float m2 = basePWM - pitchCorrection - rollCorrection - yawCorrection; // back-right  CW
  float m3 = basePWM - pitchCorrection + rollCorrection + yawCorrection; // back-left   CCW
  float m4 = basePWM + pitchCorrection + rollCorrection - yawCorrection; // front-left  CW

  // Only let motors spin at all once there's real throttle input,
  // and keep a minimum spin so corrections still have authority.
  if (throttleIn < 2) {
    setAllMotors(0, 0, 0, 0);
    return;
  }

  setAllMotors(
    (int)constrain(m1, MIN_SPIN_PWM, MAX_THROTTLE_PWM),
    (int)constrain(m2, MIN_SPIN_PWM, MAX_THROTTLE_PWM),
    (int)constrain(m3, MIN_SPIN_PWM, MAX_THROTTLE_PWM),
    (int)constrain(m4, MIN_SPIN_PWM, MAX_THROTTLE_PWM)
  );
}

// =====================================================================
// WiFi + UDP control link
// =====================================================================
void setupWiFiAndUDP() {
  WiFi.mode(WIFI_AP);
  WiFi.softAP(WIFI_SSID, WIFI_PASS);
  Serial.print("WiFi AP started. SSID: ");
  Serial.println(WIFI_SSID);
  Serial.print("Connect your phone to this network, then send UDP to: ");
  Serial.println(WiFi.softAPIP());

  udp.begin(UDP_PORT);
}

void handleIncomingUDP() {
  int packetSize = udp.parsePacket();
  if (packetSize <= 0) return;

  int len = udp.read(packetBuffer, sizeof(packetBuffer) - 1);
  if (len <= 0) return;
  packetBuffer[len] = 0;

  String msg = String(packetBuffer);
  msg.trim();

  if (msg == "ARM") {
    armed = true;
    lastPacketTime = millis();
    Serial.println("ARMED");
    return;
  }
  if (msg == "DISARM") {
    armed = false;
    Serial.println("DISARMED");
    return;
  }

  // Expect "T,R,P,Y"
  int firstComma  = msg.indexOf(',');
  int secondComma = msg.indexOf(',', firstComma + 1);
  int thirdComma  = msg.indexOf(',', secondComma + 1);
  if (firstComma < 0 || secondComma < 0 || thirdComma < 0) return;

  throttleIn = constrain(msg.substring(0, firstComma).toFloat(), 0, 100);
  rollIn     = constrain(msg.substring(firstComma + 1, secondComma).toFloat(), -100, 100);
  pitchIn    = constrain(msg.substring(secondComma + 1, thirdComma).toFloat(), -100, 100);
  yawIn      = constrain(msg.substring(thirdComma + 1).toFloat(), -100, 100);

  lastPacketTime = millis();
}

// =====================================================================
// Browser-based control page - no app install needed.
// Connect your phone to the drone's WiFi, then open http://192.168.4.1
// in any browser (Chrome, Safari, etc). Two touch joysticks control
// throttle/yaw (left) and pitch/roll (right), same as a normal RC stick
// layout. This posts to the SAME control variables as the UDP path,
// so you can use either interchangeably.
// =====================================================================
const char CONTROL_PAGE[] PROGMEM = R"HTML(
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Drone Control</title>
<style>
  html,body{margin:0;height:100%;background:#111;color:#eee;font-family:sans-serif;
             overflow:hidden;touch-action:none;user-select:none;-webkit-user-select:none;}
  #top{display:flex;justify-content:space-between;align-items:center;padding:10px 16px;}
  #status{font-size:14px;}
  button{font-size:16px;padding:10px 18px;border-radius:8px;border:none;font-weight:bold;}
  #armBtn{background:#2ecc71;color:#111;}
  #armBtn.armed{background:#e74c3c;color:#fff;}
  #sticks{display:flex;justify-content:space-around;align-items:center;
          height:calc(100% - 60px);}
  .stickBase{width:42vw;height:42vw;max-width:260px;max-height:260px;border-radius:50%;
             background:#222;border:2px solid #444;position:relative;}
  .stickKnob{width:35%;height:35%;border-radius:50%;background:#3498db;
             position:absolute;top:32.5%;left:32.5%;pointer-events:none;}
  #readout{position:absolute;bottom:6px;width:100%;text-align:center;font-size:12px;color:#888;}
</style>
</head>
<body>
  <div id="top">
    <div id="status">Disarmed</div>
    <button id="armBtn" onclick="toggleArm()">ARM</button>
  </div>
  <div id="sticks">
    <div class="stickBase" id="leftBase"><div class="stickKnob" id="leftKnob"></div></div>
    <div class="stickBase" id="rightBase"><div class="stickKnob" id="rightKnob"></div></div>
  </div>
  <div id="readout">T:0 R:0 P:0 Y:0</div>

<script>
let armed = false;
let throttle = 0, yaw = 0, pitch = 0, roll = 0;

function toggleArm(){
  armed = !armed;
  fetch(armed ? '/arm' : '/disarm');
  document.getElementById('armBtn').classList.toggle('armed', armed);
  document.getElementById('armBtn').innerText = armed ? 'DISARM' : 'ARM';
  document.getElementById('status').innerText = armed ? 'ARMED' : 'Disarmed';
}

function setupStick(baseId, knobId, onMove, springBackX, springBackY){
  const base = document.getElementById(baseId);
  const knob = document.getElementById(knobId);
  let touchId = null;
  let lastX = 0, lastY = 0;

  function updateKnob(nx, ny){
    // Center is 50%, knob width is 35% (half width is 17.5%).
    // Max travel radius is 32.5% so knob stays within circle.
    knob.style.left = (50 - 17.5 + (nx * 32.5)) + '%';
    knob.style.top  = (50 - 17.5 + (ny * 32.5)) + '%';
  }

  function handleTouch(x, y){
    const rect = base.getBoundingClientRect();
    const r = rect.width / 2;
    let dx = x - (rect.left + r);
    let dy = y - (rect.top + r);
    const dist = Math.sqrt(dx*dx + dy*dy);
    if (dist > r){ 
      dx = (dx / dist) * r; 
      dy = (dy / dist) * r; 
    }
    const nx = dx / r;
    const ny = dy / r;
    lastX = nx;
    lastY = ny;
    updateKnob(nx, ny);
    onMove(nx, ny, true);
  }

  function endTouch(){
    touchId = null;
    const nx = springBackX ? 0 : lastX;
    const ny = springBackY ? 0 : lastY;
    lastX = nx;
    lastY = ny;
    updateKnob(nx, ny);
    onMove(nx, ny, false);
  }

  base.addEventListener('touchstart', e => {
    e.preventDefault();
    if (touchId !== null) return;
    const t = e.changedTouches[0];
    touchId = t.identifier;
    handleTouch(t.clientX, t.clientY);
  }, {passive: false});

  window.addEventListener('touchmove', e => {
    if (touchId === null) return;
    for (let i = 0; i < e.changedTouches.length; i++) {
      if (e.changedTouches[i].identifier === touchId) {
        handleTouch(e.changedTouches[i].clientX, e.changedTouches[i].clientY);
        break;
      }
    }
  }, {passive: false});

  window.addEventListener('touchend', e => {
    if (touchId === null) return;
    for (let i = 0; i < e.changedTouches.length; i++) {
      if (e.changedTouches[i].identifier === touchId) {
        endTouch();
        break;
      }
    }
  });

  window.addEventListener('touchcancel', e => {
    if (touchId === null) return;
    for (let i = 0; i < e.changedTouches.length; i++) {
      if (e.changedTouches[i].identifier === touchId) {
        endTouch();
        break;
      }
    }
  });
}

// Left stick: snaps back to center on release, keeps last throttle level
setupStick('leftBase', 'leftKnob', (nx, ny, isDragging) => {
  yaw = isDragging ? Math.round(nx * 100) : 0;
  if (isDragging) {
    // Top is -1 (100% throttle), Bottom is +1 (0% throttle)
    throttle = Math.round((-ny + 1) / 2 * 100);
  }
}, true, true);

// Right stick: snaps back to center on release, resets roll & pitch to 0
setupStick('rightBase', 'rightKnob', (nx, ny, isDragging) => {
  if (isDragging) {
    roll = Math.round(nx * 100);
    pitch = Math.round(-ny * 100);
  } else {
    roll = 0;
    pitch = 0;
  }
}, true, true);

// Continuously send current stick state so the drone's failsafe stays happy
setInterval(() => {
  document.getElementById('readout').innerText =
    'T:' + throttle + ' R:' + roll + ' P:' + pitch + ' Y:' + yaw;
  fetch('/control?t=' + throttle + '&r=' + roll + '&p=' + pitch + '&y=' + yaw);
}, 100);
</script>
</body>
</html>
)HTML";
void setupWebServer() {
  server.on("/", HTTP_GET, []() {
    server.send_P(200, "text/html", CONTROL_PAGE);
  });

  server.on("/control", HTTP_GET, []() {
    if (server.hasArg("t")) throttleIn = constrain(server.arg("t").toFloat(), 0, 100);
    if (server.hasArg("r")) rollIn     = constrain(server.arg("r").toFloat(), -100, 100);
    if (server.hasArg("p")) pitchIn    = constrain(server.arg("p").toFloat(), -100, 100);
    if (server.hasArg("y")) yawIn      = constrain(server.arg("y").toFloat(), -100, 100);
    lastPacketTime = millis();
    server.send(200, "text/plain", "ok");
  });

  server.on("/arm", HTTP_GET, []() {
    armed = true;
    lastPacketTime = millis();
    Serial.println("ARMED (web)");
    server.send(200, "text/plain", "armed");
  });

  server.on("/disarm", HTTP_GET, []() {
    armed = false;
    Serial.println("DISARMED (web)");
    server.send(200, "text/plain", "disarmed");
  });

  server.begin();
  Serial.println("Web control page ready - open http://192.168.4.1 in your phone's browser.");
}

/* open http://192.168.4.1 on your phone's browser to control the drone */



