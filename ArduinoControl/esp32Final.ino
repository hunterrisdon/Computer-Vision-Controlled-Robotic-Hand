#include <ESP32Servo.h>

/* ?? User-tunable command range ??????????????????????????????? */
constexpr uint8_t RANGE_MAX = 180;   // Input format 0-RANGE_MAX

/* ?? Pin assignment ??????????????????????????????????????????? */
constexpr uint8_t SERVO_PINS[5] = { 32, 33, 14, 23, 22 };

/* ?? Calibrated angles (edit once for your hand) ?????????????? */
constexpr uint8_t MIN_DEG[5] = {  5,  30,  0,  5,  100 };   // fully open
constexpr uint8_t MAX_DEG[5] = {175,100,180,10,160 };   // fully closed

/* ?? Servo inversion flags (true to invert) ?????????????????? */
// Servos are 1-indexed for this definition: Servo 2, 3, 5 are inverted.
// Corresponding to 0-indexed: 1, 2, 4.
constexpr bool SERVO_INVERTED[5] = {
  false,  // Servo 1 (index 0)
  true,   // Servo 2 (index 1) - Inverted
  true,   // Servo 3 (index 2) - Inverted
  false,  // Servo 4 (index 3)
  true    // Servo 5 (index 4) - Inverted
};

/* ?? Globals ?????????????????????????????????????????????????? */
Servo servos[5];

/* Map a 0?RANGE_MAX command to the finger?s angle range */
inline uint8_t valueToAngle(uint8_t finger, uint8_t v_command)
{
  uint8_t v_processed = v_command; // Use a new variable for the command after potential inversion

  if (v_processed > RANGE_MAX) v_processed = RANGE_MAX; // Clamp command

  // Apply inversion if this servo is marked as inverted
  if (SERVO_INVERTED[finger]) {
    v_processed = RANGE_MAX - v_processed;
  }

  uint8_t lo = MIN_DEG[finger];
  uint8_t hi = MAX_DEG[finger];
  
  // The rest of the mapping logic remains the same, using v_processed.
  // If not inverted: 0 maps to lo, RANGE_MAX maps to hi.
  // If inverted: input 0 -> v_processed=RANGE_MAX -> maps to hi.
  //              input RANGE_MAX -> v_processed=0 -> maps to lo.
  return lo + (uint32_t)(hi - lo) * v_processed / RANGE_MAX;
}

void setup()
{
  Serial.begin(115200);

  for (uint8_t i = 0; i < 5; ++i) {
    servos[i].setPeriodHertz(50);                // hobby-servo PWM
    servos[i].attach(SERVO_PINS[i], 500, 2500);  // 0–180° pulse range
    servos[i].write(MIN_DEG[i]);                 // park open
  }

  Serial.printf("READY – send 5 comma-separated values 0-%u + newline\n", RANGE_MAX);
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
        Serial.printf("ERR: need exactly 5 integers 0-%u\n", RANGE_MAX);
      }
      inLine = "";
    } else if (c != '\r') {      // skip CR in Windows line endings
      inLine += c;
    }
  }
}