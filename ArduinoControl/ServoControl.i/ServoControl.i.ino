#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

#define SERVOMIN 100
#define SERVOMAX 500

void setup() {
  Serial.begin(115200);
  Wire.begin();
  pwm.begin();
  pwm.setPWMFreq(50);
  delay(1000);  // let everything initialize
  Serial.println("✅ ESP32 + PCA9685 is ready.");
}

void loop() {
  static String input = "";
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      Serial.print("🔄 Received command: ");
      Serial.println(input);
      handleCommand(input);
      input = "";
    } else {
      input += c;
    }
  }
}

void handleCommand(String cmd) {
  int angles[5];
  int index = 0;
  char *token = strtok((char *)cmd.c_str(), ",");
  while (token != NULL && index < 5) {
    angles[index++] = atoi(token);
    token = strtok(NULL, ",");
  }

  for (int i = 0; i < index; i++) {
    int pulse = map(angles[i], 0, 180, SERVOMIN, SERVOMAX);
    pwm.setPWM(i, 0, pulse);
    Serial.print("➡️ Servo ");
    Serial.print(i);
    Serial.print(" angle ");
    Serial.print(angles[i]);
    Serial.print(" → PWM ");
    Serial.println(pulse);
  }
}
