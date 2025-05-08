import mediapipe as mp
import cv2
import time
import math
import numpy as np

# Setup MediaPipe
mp_hands = mp.solutions.hands
drawing_utils = mp.solutions.drawing_utils

# Utilities
def landmark_to_array(landmark):
    return np.array([landmark.x, landmark.y, landmark.z])

def vector_angle(v1, v2):
    unit_v1 = v1 / np.linalg.norm(v1)
    unit_v2 = v2 / np.linalg.norm(v2)
    dot_product = np.dot(unit_v1, unit_v2)
    dot_product = np.clip(dot_product, -1.0, 1.0)
    return math.degrees(math.acos(dot_product))

# Compute angles between joints, draw visuals, and return both real & servo angles
def get_finger_joint_angles_and_servos(landmarks, frame, w, h):
    angle_specs = [
        (0, 2, 3, "Thumb-A"), (2, 3, 4, "Thumb-B"),
        (0, 5, 6, "Index-A"), (5, 6, 8, "Index-B"),
        (0, 9, 10, "Middle-A"), (9, 10, 12, "Middle-B"),
        (0, 13, 14, "Ring-A"), (13, 14, 16, "Ring-B"),
        (0, 17, 18, "Pinky-A"), (17, 18, 20, "Pinky-B")
    ]

    servo_angles = []  # Only 'B' angles go here
    servo_labels = []  # e.g. "Thumb", "Index", etc.
    for j1, j2, j3, label in angle_specs:
        v1 = landmark_to_array(landmarks[j2]) - landmark_to_array(landmarks[j1])
        v2 = landmark_to_array(landmarks[j3]) - landmark_to_array(landmarks[j2])
        angle = vector_angle(v1, v2)

        # Draw vectors and angle text
        p1 = int(landmarks[j1].x * w), int(landmarks[j1].y * h)
        p2 = int(landmarks[j2].x * w), int(landmarks[j2].y * h)
        p3 = int(landmarks[j3].x * w), int(landmarks[j3].y * h)
        cv2.line(frame, p1, p2, (0, 255, 255), 2)
        cv2.line(frame, p2, p3, (255, 0, 255), 2)
        cv2.putText(frame, f"{int(angle)}", p2,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

        # Store servo-mapped angle for "B" joints only
        if label.endswith("B"):
            servo_angle = int(np.interp(angle, [30, 160], [0, 180]))
            servo_angles.append(servo_angle)
            finger = label.split("-")[0]  # e.g., "Thumb"
            servo_labels.append(finger)

    return servo_labels, servo_angles

# Camera setup
cap = cv2.VideoCapture(0)
prev_time = 0

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) as hands:

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get joint angles and servo outputs
                servo_labels, servo_angles = get_finger_joint_angles_and_servos(hand_landmarks.landmark, frame, w, h)
                servo_string = ','.join(str(a) for a in servo_angles)
                print("Servo Command:", servo_string)
                degree_symbol = u'\u00B0'
                # Display servo angles on the left
                for i, angle in enumerate(servo_angles):
                    y_offset = 60 + i * 30
                    label = servo_labels[i]
                    cv2.putText(frame, f'{label}: {angle}', (10, y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # FPS overlay
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time
        cv2.putText(frame, f'FPS: {int(fps)}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Hand Tracker (Servo + Joint Angles)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
