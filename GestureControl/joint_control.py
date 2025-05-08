import cv2
import numpy as np
import mediapipe as mp
from utils.hand_utils import landmark_to_array, vector_angle

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Define joint triplets for each finger (base and tip segments)
joint_triplets = [
    (0, 2, 3, "Thumb-A"), (2, 3, 4, "Thumb-B"),
    (0, 5, 6, "Index-A"), (5, 6, 8, "Index-B"),
    (0, 9, 10, "Middle-A"), (9, 10, 12, "Middle-B"),
    (0, 13, 14, "Ring-A"), (13, 14, 16, "Ring-B"),
    (0, 17, 18, "Pinky-A"), (17, 18, 20, "Pinky-B")
]

# Setup MediaPipe hands model
hands_model = mp_hands.Hands(static_image_mode=False, max_num_hands=1,
                             min_detection_confidence=0.7, min_tracking_confidence=0.7)

def process_joint_control_frame(frame):
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands_model.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            servo_angles = []
            servo_labels = []

            for j1, j2, j3, label in joint_triplets:
                v1 = landmark_to_array(hand_landmarks.landmark[j2]) - landmark_to_array(hand_landmarks.landmark[j1])
                v2 = landmark_to_array(hand_landmarks.landmark[j3]) - landmark_to_array(hand_landmarks.landmark[j2])
                angle = vector_angle(v1, v2)

                # Draw angle value at the middle joint
                p1 = int(hand_landmarks.landmark[j1].x * w), int(hand_landmarks.landmark[j1].y * h)
                p2 = int(hand_landmarks.landmark[j2].x * w), int(hand_landmarks.landmark[j2].y * h)
                p3 = int(hand_landmarks.landmark[j3].x * w), int(hand_landmarks.landmark[j3].y * h)

                cv2.line(frame, p1, p2, (0, 255, 255), 2)
                cv2.line(frame, p2, p3, (255, 0, 255), 2)
                cv2.putText(frame, f"{int(angle)}", p2, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

                if label.endswith("B"):
                    servo_angle = int(np.interp(angle, [30, 160], [0, 180]))
                    servo_angles.append(servo_angle)
                    servo_labels.append(label.split("-")[0])

            for i, val in enumerate(servo_angles):
                y_offset = 60 + i * 30
                cv2.putText(frame, f"{servo_labels[i]}: {val} deg", (10, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            print("Servo Command:", ','.join(str(val) for val in servo_angles))

    return frame
