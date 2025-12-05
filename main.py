"""
LookAlive - 20-20-20 Eye Tracker
Precise gaze tracking, blink detection, eye health monitoring
"""

from core import BreakManager, notify_start_break, notify_end_break, notify_too_close, demo_notifications, IrisGazeTracker, UIOverlay, SessionTracker, SystemTray, TRAY_AVAILABLE
from utils.webcam import get_webcam_capture

import mediapipe as mp
import cv2
import time

SCREEN_TIME_LIMIT = 60 * 20  # 30 seconds (demo mode)
BREAK_DURATION = 20  # 20 seconds

# initialize face mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8,
)

# camera setup
cap = get_webcam_capture()

# initialize core components
break_manager = BreakManager(SCREEN_TIME_LIMIT, BREAK_DURATION)
iris_tracker = IrisGazeTracker()
ui = UIOverlay()
session_tracker = SessionTracker()

# system tray setup
running = True
window_visible = True

def on_tray_quit():
    global running
    running = False

def on_tray_show():
    global window_visible
    window_visible = True
    cv2.namedWindow("LookAlive", cv2.WINDOW_NORMAL)

tray = SystemTray(on_show_callback=on_tray_show, on_quit_callback=on_tray_quit)
if TRAY_AVAILABLE:
    tray.start()
    print("Press M to minimize to system tray")

print("LookAlive Started")
print("Controls: Q-Quit | C-Compact | D-Debug | H-Heatmap | P-Reset Position | T-Demo Notifications | M-Minimize")

show_debug = False
last_health_warning = 0
last_too_close_warning = 0

# create window
cv2.namedWindow("LookAlive", cv2.WINDOW_NORMAL)

while running:
    ret, frame = cap.read()
    if not ret:
        break
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    now = time.time()
    
    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        
        # get analysis from iris tracker
        analysis = iris_tracker.get_gaze_analysis(landmarks, frame.shape)
        gaze = analysis["gaze_direction"]
        too_close = analysis["too_close"]
        blink_rate = analysis["blink_rate"]
        
        # update session tracker
        session_tracker.update(gaze == "center")
        
        # handle break notifications
        notify_event, now = break_manager.update_state(gaze)
        
        if notify_event == "start_break":
            notify_start_break()
        elif notify_event == "end_break":
            notify_end_break()
        
        # calculate timing info
        if break_manager.break_in_progress:
            time_to_break = 0
            break_remaining = BREAK_DURATION - (now - break_manager.break_start_time)
        else:
            if break_manager.start_screen_watch_time:
                elapsed = now - break_manager.start_screen_watch_time
                time_to_break = max(0, SCREEN_TIME_LIMIT - elapsed)
            else:
                time_to_break = SCREEN_TIME_LIMIT
            break_remaining = 0
        
        screen_time_mins = int((now - (break_manager.start_screen_watch_time or now)) / 60)
        
        # draw ui overlay
        frame = ui.draw_status_bar(
            frame, 
            gaze=gaze,
            break_in_progress=break_manager.break_in_progress,
            time_to_break=time_to_break,
            break_remaining=break_remaining,
            blink_rate=blink_rate,
            too_close=too_close,
            screen_time_mins=screen_time_mins
        )
        
        # too close warning
        if too_close and now - last_too_close_warning > 5:
            frame = ui.draw_warning(frame, "Move back from screen!", "danger")
            notify_too_close()
            last_too_close_warning = now
        
        # low blink rate warning
        if blink_rate > 3 and blink_rate < 10 and now - last_health_warning > 30:
            frame = ui.draw_warning(frame, "Remember to blink!", "warning")
            last_health_warning = now
        
        # debug overlay
        if show_debug:
            if analysis['iris_positions']:
                left_x, left_y, right_x, right_y = analysis['iris_positions']
                cv2.circle(frame, (int(left_x), int(left_y)), 3, (0, 255, 0), -1)
                cv2.circle(frame, (int(right_x), int(right_y)), 3, (0, 255, 0), -1)
    
    else:
        # no face detected
        break_manager.reset()
        h, w = frame.shape[:2]
        ui.draw_rounded_rect(frame, w//2 - 150, h//2 - 30, 300, 60, (0, 0, 150), 0.8)
        cv2.putText(frame, "No Face Detected", (w//2 - 100, h//2 + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    if window_visible:
        cv2.imshow("LookAlive", frame)
    
    # update tray status
    if TRAY_AVAILABLE and tray.icon:
        if break_manager.break_in_progress:
            tray.update_status("Break Time", "orange")
        elif results.multi_face_landmarks and too_close:
            tray.update_status("Too Close!", "red")
        else:
            tray.update_status("Running", "green")
    
    # handle keyboard input
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        running = False
    elif key == ord("c"):
        mode = ui.toggle_compact()
        print(f"{'Compact' if mode else 'Full'} mode")
    elif key == ord("d"):
        show_debug = not show_debug
        print(f"Debug: {'ON' if show_debug else 'OFF'}")
    elif key == ord("r"):
        iris_tracker.reset_blink_counter()
        print("Blink counter reset")
    elif key == ord("h"):
        print(session_tracker.generate_heatmap_ascii())
    elif key == ord("p"):
        iris_tracker.reset_distance_calibration()
        print("Distance calibration reset - sit at normal position")
    elif key == ord("t"):
        print("\nPausing tracking for demo...")
        demo_notifications()
        print("Demo complete - resuming tracking\n")
    elif key == ord("m") and TRAY_AVAILABLE:
        window_visible = False
        cv2.destroyAllWindows()
        tray.minimize()
        print("Minimized to system tray")

# cleanup
tray.stop()
cap.release()
cv2.destroyAllWindows()

# end session and show summary
session_tracker.end_session()
print(f"\nTotal blinks: {iris_tracker.blink_counter}")
print(f"Average blink rate: {iris_tracker.get_blink_rate():.1f}/min")
print("Thanks for taking care of your eyes!")
