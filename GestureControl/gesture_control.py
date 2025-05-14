import os
import cv2
import time
import numpy as np
import serial
import serial.tools.list_ports
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import GestureRecognizer, GestureRecognizerOptions

# === Auto-Detect Serial Port ===
def auto_connect_serial():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "usbserial" in port.device:
            try:
                print(f"🔌 Connecting to {port.device}")
                s = serial.Serial(port.device, 115200, timeout=1)
                time.sleep(2)
                return s
            except serial.SerialException:
                continue
    print("⚠️ No serial device found. Servo commands will not be sent.")
    return None

# Initialize serial connection
ser = auto_connect_serial()

# === Load Gesture Model ===
model_path = os.path.join(os.path.dirname(__file__), "gesture_recognizer.task")
gesture_recognizer = GestureRecognizer.create_from_options(
    GestureRecognizerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
        running_mode=vision.RunningMode.VIDEO
    )
)

# === Gesture-to-Servo Mapping ===
GESTURE_TO_SERVO = {
    "Closed_Fist": [180, 180, 180, 180, 180],
    "Open_Palm": [0, 0, 0, 0, 0],
    "Pointing_Up": [180, 0, 180, 180, 180],
    "Thumb_Up": [0, 180, 180, 180, 180],
    "Victory": [0, 0, 180, 180, 180],
    "ILoveYou": [0, 0, 180, 180, 0]
}

# === Helper: Send Servo Angles to ESP32 ===
def send_servo_angles(angles):
    if ser and ser.is_open:
        command = ','.join(str(a) for a in angles) + '\n'
        ser.write(command.encode())

# === Main Gesture Processor ===
def process_gesture_control_frame(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    gesture_result = gesture_recognizer.recognize_for_video(mp_image, int(time.time() * 1000))
    gesture_label = None

    if gesture_result.gestures:
        gesture_label = gesture_result.gestures[0][0].category_name

    if gesture_label:
        servo_values = GESTURE_TO_SERVO.get(gesture_label, None)
        cv2.putText(frame, f"Gesture: {gesture_label}", (10, 420),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        if servo_values:
            send_servo_angles(servo_values)  # Send to ESP32
            for i, val in enumerate(servo_values):
                y_offset = 60 + i * 30
                cv2.putText(frame, f"Finger {i+1}: {val} deg", (10, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            print("Servo Command:", ','.join(str(val) for val in servo_values))

    return frame
