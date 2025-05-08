import tkinter as tk
import cv2
import time
import os
import numpy as np
from PIL import Image, ImageTk
from utils.hand_utils import landmark_to_array, vector_angle
from GestureControl.joint_control import process_joint_control_frame
from GestureControl.gesture_control import process_gesture_control_frame

# === GUI Setup ===
def launch_mode_selector():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Get native/default resolution
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Detected camera resolution: {width}x{height}")

    # Create root window with dynamic sizing
    root = tk.Tk()
    root.title("Robothon Controller")
    root.geometry(f"{width + 240}x{height}")  # Add space for sidebar

    active_mode = tk.StringVar(value="joint")

    # === UI Layout ===
    control_frame = tk.Frame(root, bg="#2c2f33", width=200)
    control_frame.pack(side="left", fill="y")

    canvas = tk.Label(root)
    canvas.pack(side="right", expand=True, fill="both")

    def switch_to_joint():
        active_mode.set("joint")

    def switch_to_gesture():
        active_mode.set("gesture")

    tk.Label(control_frame, text="Modes", fg="white", bg="#2c2f33",
             font=("Helvetica", 14)).pack(pady=10)
    tk.Button(control_frame, text="Joint Control", width=20, command=switch_to_joint).pack(pady=10)
    tk.Button(control_frame, text="Gesture Control", width=20, command=switch_to_gesture).pack(pady=10)

    prev_time = 0

    def update():
        nonlocal prev_time
        ret, frame = cap.read()
        if not ret:
            root.after(10, update)
            return

        frame = cv2.flip(frame, 1)

        if active_mode.get() == "joint":
            frame = process_joint_control_frame(frame)
        elif active_mode.get() == "gesture":
            frame = process_gesture_control_frame(frame)

        # Get canvas dimensions
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        if canvas_width > 0 and canvas_height > 0:
            original_height, original_width = frame.shape[:2]
            aspect_ratio = original_width / original_height

            if canvas_width / canvas_height > aspect_ratio:
                new_height = canvas_height
                new_width = int(aspect_ratio * canvas_height)
            else:
                new_width = canvas_width
                new_height = int(canvas_width / aspect_ratio)

            new_width = max(1, new_width)
            new_height = max(1, new_height)
            frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # FPS display
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time
        cv2.putText(frame, f'FPS: {int(fps)}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Convert and update GUI
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        canvas.imgtk = imgtk
        canvas.configure(image=imgtk)
        root.after(10, update)

    update()
    root.mainloop()
    cap.release()
    cv2.destroyAllWindows()