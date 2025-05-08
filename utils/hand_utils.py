import numpy as np
import math

def landmark_to_array(landmark):
    """
    Converts a Mediapipe landmark to a NumPy array [x, y, z].
    """
    return np.array([landmark.x, landmark.y, landmark.z])

def vector_angle(v1, v2):
    """
    Computes the angle in degrees between two vectors using the dot product.
    """
    unit_v1 = v1 / np.linalg.norm(v1)
    unit_v2 = v2 / np.linalg.norm(v2)
    dot_product = np.dot(unit_v1, unit_v2)
    dot_product = np.clip(dot_product, -1.0, 1.0)  # Avoid numerical errors
    angle_rad = math.acos(dot_product)
    return math.degrees(angle_rad)

def compute_joint_angles(landmarks, joint_triplets):
    """
    Computes the angles (in degrees) between joint triplets.

    Args:
        landmarks: List of Mediapipe landmarks.
        joint_triplets: List of (j1, j2, j3) index tuples representing joint chains.

    Returns:
        List of angles.
    """
    angles = []
    for j1, j2, j3 in joint_triplets:
        v1 = landmark_to_array(landmarks[j2]) - landmark_to_array(landmarks[j1])
        v2 = landmark_to_array(landmarks[j3]) - landmark_to_array(landmarks[j2])
        angles.append(vector_angle(v1, v2))
    return angles

def angle_to_servo(angle, min_angle=30, max_angle=160):
    """
    Maps a joint angle to a servo angle in the 0-180 range.
    """
    return int(np.interp(angle, [min_angle, max_angle], [0, 180]))
