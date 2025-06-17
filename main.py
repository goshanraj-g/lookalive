import cv2
import mediapipe as mp
import time
from plyer import notification

# Mediapipe -> Library handling hard ML work
# OpenCV -> Handles raw pixels & windows
# Plyer -> Talks to OS

SCREEN_TIME_LIMIT = 20 * 60  # 20 minutes -> 1200 seconds
BREAK_DURATION = 20  # 20 seconds

mp_face_mesh = (
    mp.solutions.face_mesh  # 468-point face mesh model
)  # Face Mesh vs Face Detection: Detection detects if a face is existent, mesh detects key points on the face
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,  # Unlocks iris points (without this flag, it would make pupil centers inaccurate)
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75,
)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Capture on main camera
if not cap.isOpened():
    raise RuntimeError("Cannot open webcam")

start_screen_watch_time = None
break_in_progress = False
break_start_time = None

# Left iris center: index 474
# Right iris center: index 469


def get_gaze_direction(landmarks, frame_shape):
    h, w = frame_shape[:2]  # Gets height and width of video frame
    x_left = int(
        landmarks[474].x * w
    )  # Access x-coordinates of left and right iris centers and multiply by w to convert to pixelized positions from normalized values [0.0, 1.0]
    x_right = int(landmarks[469].x * w)
    eye_center_x = (
        x_left + x_right
    ) // 2  # Take average of both iris centers to gauge the overal gaze center

    if eye_center_x < w * 0.4:  # Return 'left' if center is on the left side of width
        return "left"
    if eye_center_x > w * 0.6:  # Return 'right' if center is on the right side of width
        return "right"
    else:
        return "center"  # Assume user is looking at the center


while True:
    ret, frame = cap.read()
    if not ret:  # If frame wasn't read, disconnect
        break

    rgb = cv2.cvtColor(
        frame, cv2.COLOR_BGR2RGB
    )  # Convert from BGR to RGB since MediaPipe expects RGB
    results = face_mesh.process(rgb)  # MediaPipe to process the rgb frame
    now = time.time()  # Snapshot of the current frame's time

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[
            0
        ].landmark  # Access the landmarks of the detected result (.x, .y, .z)
        gaze = get_gaze_direction(landmarks, frame.shape)

        if gaze == "center" and not break_in_progress:
            if start_screen_watch_time is None:
                start_screen_watch_time = now
            elif now - start_screen_watch_time >= SCREEN_TIME_LIMIT:
                notification.notify(
                    title="20-20-20 Rule",
                    message="Look 20 feet away for 20 seconds",
                    timeout=5,
                )
                break_in_progress = True
                break_start_time = now
        else:
            start_screen_watch_time = None

        status_txt = "BREAK" if break_in_progress else f"Gaze: {gaze}"
        cv2.putText(
            frame,
            status_txt,
            (30, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0) if gaze == "center" else (0, 255, 255),
            2,
        )
    else:
        start_screen_watch_time = None
        gaze = "none"
        cv2.putText(
            frame, "No Face", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
        )

    if break_in_progress:
        elapsed = now - break_start_time
        cv2.putText(
            frame,
            f"Break: {int(BREAK_DURATION - elapsed)}s",
            (30, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            2,
        )

        if elapsed >= BREAK_DURATION:
            break_in_progress = False
            start_screen_watch_time = None
            notification.notify(
                title="Break Over", message="You can return to the screen", timeout=5
            )
    cv2.imshow("20-20-20 Eye Tracker --- q to quit", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
