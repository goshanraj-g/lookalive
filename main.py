from core import (
    get_gaze_direction,
    BreakManager,
    notify_start_break,
    notify_end_break,
)
from utils.webcam import get_webcam_capture

import mediapipe as mp
import cv2
import time

# constants of time
SCREEN_TIME_LIMIT = 20 * 60  # 20 minutes
BREAK_DURATION = 20  # 20 seconds

# Mediapipe Face Mesh setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75,
)

# setup webcam
cap = get_webcam_capture()

# setupo break manager
break_manager = BreakManager(SCREEN_TIME_LIMIT, BREAK_DURATION)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    now = time.time()

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        gaze = get_gaze_direction(landmarks, frame.shape)

        notify_event, now = break_manager.update_state(gaze)

        if notify_event == "start_break":
            notify_start_break()
        elif notify_event == "end_break":
            notify_end_break()

        status_txt = "BREAK" if break_manager.break_in_progress else f"Gaze: {gaze}"
        color = (0, 255, 0) if gaze == "center" else (0, 255, 255)
        cv2.putText(
            frame,
            status_txt,
            (30, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2,
        )
    else:
        break_manager.reset()
        cv2.putText(
            frame,
            "No Face",
            (30, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2,
        )

    # Break countdown overlay
    if break_manager.break_in_progress:
        elapsed = now - break_manager.break_start_time
        remaining = max(0, int(BREAK_DURATION - elapsed))
        cv2.putText(
            frame,
            f"Break: {remaining}s",
            (30, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            2,
        )

    cv2.imshow("20-20-20 Eye Tracker — q to quit", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# cleanup
cap.release()
cv2.destroyAllWindows()
