#include <ESP32Servo.h>

// ──--- PIN ASSIGNMENT ---──────────────────────────────────────
constexpr uint8_t SERVO_PINS[5] = { 32, 33, 14, 23, 22 };

// ──--- CALIBRATED ANGLES (edit these once for your hand) ---───
//   MIN_DEG → finger fully OPEN
//   MAX_DEG → finger fully CLOSED
constexpr uint8_t MIN_DEG[5] = {  5,  5,  5,  5,  5 };   // example
constexpr uint8_t MAX_DEG[5] = {175,175,175,175,175 };   // example

// ──--- GLOBALS ---─────────────────────────────────────────────
Servo servos[5];

/// Map a 0–100 command to an angle inside this finger’s range
inline uint8_t valueToAngle(uint8_t finger, uint8_t v)
{
  // clamp just in case someone sends <0 or >100
  if (v > 100) v = 100;
  uint8_t lo = MIN_DEG[finger];
  uint8_t hi = MAX_DEG[finger];
  return lo + (uint32_t)(hi - lo) * v / 100;      // linear interp
}

void setup()
{
  Serial.begin(115200);

  // attach each servo and park them at “open” (0 %)
  for (uint8_t i = 0; i < 5; ++i) {
    servos[i].setPeriodHertz(50);          // 50 Hz for hobby servos
    servos[i].attach(SERVO_PINS[i], 500, 2500);
    servos[i].write(MIN_DEG[i]);
  }

  Serial.println(F("READY – send 5 comma-separated values 0-100 + newline"));
}

void loop()
{
  static String inLine;
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      int v[5];
      if (sscanf(inLine.c_str(), "%d,%d,%d,%d,%d",
                 &v[0], &v[1], &v[2], &v[3], &v[4]) == 5) {

        for (uint8_t i = 0; i < 5; ++i)
          servos[i].write(valueToAngle(i, (uint8_t)v[i]));

      } else {
        Serial.println(F("ERR: need exactly 5 integers 0-100"));
      }
      inLine = "";
    } else {
      inLine += c;
    }
  }
}
