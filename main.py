"""
LookAlive - 20-20-20 Eye Tracker
Precise gaze tracking, blink detection, eye health monitoring
"""

from core import BreakManager, notify_start_break, notify_end_break, IrisGazeTracker
from utils.webcam import get_webcam_capture

import mediapipe as mp
import cv2
import time

SCREEN_TIME_LIMIT = 20 * 60  # 20 minutes
BREAK_DURATION = 20  # 20 seconds

# init face mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8,
)

# camera setup
cap = get_webcam_capture()

# break setup
break_manager = BreakManager(SCREEN_TIME_LIMIT, BREAK_DURATION)

# iris tracker setup
iris_tracker = IrisGazeTracker()

# check callibration
if not iris_tracker.is_calibrated:
    print("\n" + "-" * 50)
    print("Screen not calibrated")
    print("Please calibrate your screen for best accuracy")
    
print("Starting application")

# settings
show_debug = True
last_health_warning = 0

# create window
cv2.namedWindow("LookAlive - Eye Strain Manager", cv2.WINDOW_NORMAL)

# cv2.setWindowProperty( -- full screen
#     "Enhanced 20-20-20 Eye Tracker", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
# )

while True:
    # cap.read() -> (ret: boolean, frame: [NumPy image array])
    ret, frame = cap.read()
    if not ret:
        break
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # OpenCV -> BGR, convert to RGB for mediapipe
    results = face_mesh.process(rgb) # let mediapipe process the mesh from RGB
    now = time.time()    
    
    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark # get only the first face found, and get landmarks
        
        analysis = iris_tracker.get_gaze_analysis(landmarks, frame.shape) # send landmarks to iris tracker
        gaze = analysis["gaze_direction"] # get gaze direction from analysis
        
        notify_event, now = break_manager.update_state(gaze)
        
        if notify_event == "start_break":
            notify_start_break()
        elif notify_event == "end_break":
            notify_end_break()

        if break_manager.break_in_progress:
            status_txt = "break... look away 20ft away for 20sec"
            color = (0, 165, 255) 
        else:
            status_txt = f"Gaze: {gaze.upper()}"
            color = (0, 255, 0) if gaze == "center" else (0, 255, 255)

        cv2.putText(
            frame, status_txt, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3
        )

        # break countdown
        if break_manager.break_in_progress:
            elapsed = now - break_manager.break_start_time
            remaining = max(0, int(BREAK_DURATION - elapsed))
            cv2.putText(
                frame,
                f"break: {remaining}s",
                (30, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 0),
                2,
            )

        # eye health monitoring
        blink_rate = analysis["blink_rate"]
        if blink_rate > 3:  # Only show after some data is collected
            if blink_rate < 10 and now - last_health_warning > 30:
                cv2.putText(
                    frame,
                    "⚠️ BLINK MORE! (Dry Eyes)",
                    (30, frame.shape[0] - 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 100, 255),
                    2,
                )
                last_health_warning = now
            elif blink_rate > 30 and now - last_health_warning > 30:
                cv2.putText(
                    frame,
                    "⚠️ High Blink Rate (Eye Strain?)",
                    (30, frame.shape[0] - 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 165, 255),
                    2,
                )
                last_health_warning = now

        # debug overlay
        if show_debug:
            frame = iris_tracker.draw_debug_overlay(frame, landmarks, analysis)

            # Additional debug info
            cv2.putText(
                frame,
                f"Screen Time: {int((now - (break_manager.start_screen_watch_time or now))/60)}min",
                (frame.shape[1] - 300, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
            )

            # if analysis["iris_diameter"]:
            #     cv2.putText(
            #         frame,
            #         f"Iris: {analysis['iris_diameter']:.1f}px",
            #         (frame.shape[1] - 300, 60),
            #         cv2.FONT_HERSHEY_SIMPLEX,
            #         0.6,
            #         (255, 255, 255),
            #         1,
            #     )

            # Calibration status
            cal_status = (
                "CALIBRATED" if iris_tracker.is_calibrated else "NOT CALIBRATED"
            )
            cal_color = (0, 255, 0) if iris_tracker.is_calibrated else (0, 165, 255)
            cv2.putText(
                frame,
                f"Screen: {cal_status}",
                (frame.shape[1] - 300, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                cal_color,
                1,
            )

    else:
        break_manager.reset()
        cv2.putText(
            frame,
            "No Face Detected",
            (30, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 0, 255),
            3,
        )

    # # Calibration reminder for non-calibrated users
    # if not iris_tracker.is_calibrated:
    #     cv2.putText(
    #         frame,
    #         "⚠️ Run 'python calibrate_screen.py' for better accuracy",
    #         (10, frame.shape[0] - 60),
    #         cv2.FONT_HERSHEY_SIMPLEX,
    #         0.5,
    #         (0, 165, 255),
    #         1,
    #     )

    # Controls info
    cv2.putText(
        frame,
        "Q-Quit | R-Reset Blinks | D-Debug",
        (10, frame.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (200, 200, 200),
        1,
    )


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

# cleanup
cap.release()
cv2.destroyAllWindows()

print("\n📊 Session Summary:")
print(f"Total blinks: {iris_tracker.blink_counter}")
print(f"Average blink rate: {iris_tracker.get_blink_rate():.1f}/min")
print("👋 Thanks for taking care of your eyes!")
