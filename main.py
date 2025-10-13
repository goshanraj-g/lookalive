"""
LookAlive - 20-20-20 Eye Tracker
Precise gaze tracking, blink detection, eye health monitoring
"""

from core import BreakManager, notify_start_break, notify_end_break, IrisGazeTracker
from utils.webcam import get_webcam_capture

import mediapipe as mp
import cv2
import time

# Constants
SCREEN_TIME_LIMIT = 20 * 60  # 20 minutes
BREAK_DURATION = 20  # 20 seconds

# Initialize components
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8,
)

# Setup
cap = get_webcam_capture()
break_manager = BreakManager(SCREEN_TIME_LIMIT, BREAK_DURATION)
iris_tracker = IrisGazeTracker()

print("🚀 Starting Enhanced Eye Tracker with Iris Detection")
print("Features: Precise gaze tracking, blink detection, eye health monitoring")
print("Controls:")
print("  Q - Quit")
print("  R - Reset blink counter")
print("  D - Toggle debug overlay")

# Settings
show_debug = True
last_health_warning = 0

# Create window
cv2.namedWindow("Enhanced 20-20-20 Eye Tracker", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Enhanced 20-20-20 Eye Tracker", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Process frame
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    now = time.time()

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        
        # Get comprehensive gaze analysis
        analysis = iris_tracker.get_gaze_analysis(landmarks, frame.shape)
        gaze = analysis['gaze_direction']
        
        # Update break manager
        notify_event, now = break_manager.update_state(gaze)
        
        if notify_event == "start_break":
            notify_start_break()
        elif notify_event == "end_break":
            notify_end_break()

        # Main status display
        if break_manager.break_in_progress:
            status_txt = "BREAK TIME - Look Away!"
            color = (0, 165, 255)  # Orange
        else:
            status_txt = f"Gaze: {gaze.upper()}"
            color = (0, 255, 0) if gaze == "center" else (0, 255, 255)
        
        cv2.putText(frame, status_txt, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        
        # Break countdown
        if break_manager.break_in_progress:
            elapsed = now - break_manager.break_start_time
            remaining = max(0, int(BREAK_DURATION - elapsed))
            cv2.putText(frame, f"Break: {remaining}s", (30, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        
        # Eye health monitoring
        blink_rate = analysis['blink_rate']
        if blink_rate > 0:  # Only show after some data is collected
            if blink_rate < 10 and now - last_health_warning > 30:
                cv2.putText(frame, "⚠️ BLINK MORE! (Dry Eyes)", (30, frame.shape[0] - 100),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 100, 255), 2)
                last_health_warning = now
            elif blink_rate > 30 and now - last_health_warning > 30:
                cv2.putText(frame, "⚠️ High Blink Rate (Eye Strain?)", (30, frame.shape[0] - 100),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
                last_health_warning = now
        
        # Debug overlay
        if show_debug:
            frame = iris_tracker.draw_debug_overlay(frame, landmarks, analysis)
            
            # Additional debug info
            cv2.putText(frame, f"Screen Time: {int((now - (break_manager.start_screen_watch_time or now))/60)}min",
                       (frame.shape[1] - 300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            if analysis['iris_diameter']:
                cv2.putText(frame, f"Iris: {analysis['iris_diameter']:.1f}px",
                           (frame.shape[1] - 300, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    else:
        break_manager.reset()
        cv2.putText(frame, "No Face Detected", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    # Controls info
    cv2.putText(frame, "Q-Quit | R-Reset Blinks | D-Debug", (10, frame.shape[0] - 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    cv2.imshow("Enhanced 20-20-20 Eye Tracker", frame)
    
    # Handle keys
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("r"):
        print("🔄 Resetting blink counter...")
        iris_tracker.reset_blink_counter()
    elif key == ord("d"):
        show_debug = not show_debug
        print(f"Debug overlay: {'ON' if show_debug else 'OFF'}")

# Cleanup
cap.release()
cv2.destroyAllWindows()

print("\n📊 Session Summary:")
print(f"Total blinks: {iris_tracker.blink_counter}")
print(f"Average blink rate: {iris_tracker.get_blink_rate():.1f}/min")
print("👋 Thanks for taking care of your eyes!")