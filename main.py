import cv2  # import open cv
import mediapipe as mp  # face detection
import time
from plyer import notification

BREAK_INTERVAL = 5

# track when face was last continuously seen
start_time = None
notified = False

# setup face detection model from MediaPipe
mp_face = mp.solutions.face_detection
# face detector object, good for faces within 2m, and will only count detection if it's 75% confident
face_detection = mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.75)


# open default webcam (0)
def get_camera():
    return cv2.VideoCapture(0, cv2.CAP_DSHOW)


print("trying to find webcam")
cap = get_camera()

if not cap.isOpened():
    print("could not open webcam")
    exit()

print("webcam opened successfully")

# start loop to read frames from camera
while True:
    ret, frame = (
        cap.read()
    )  # ret -> boolean if frame is read correctly, and frame is the image captures as an NumPy array
    if not ret:
        print("failed to grab frame")
        break  # if the frame isn't captured
    rgb_frame = cv2.cvtColor(
        frame, cv2.COLOR_BGR2RGB
    )  # convert to RGB since opencv uses BGR, and media pipe needs RGB
    results = face_detection.process(
        rgb_frame
    )  # face detection model on the current frame

    if results.detections:  # if a face is detected
        for detection in results.detections:  # go through face
            bboxC = (
                detection.location_data.relative_bounding_box
            )  # get the bounding box of the face
            h, w, _ = frame.shape  # get the height, width of image
            x = int(bboxC.xmin * w)
            y = int(bboxC.ymin * h)
            width = int(bboxC.width * w)
            height = int(bboxC.height * h)
            # since we need to convert the relative box to pixel values, we have to convert the precent of the image from the bounding box to real pixel coordinates
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 0, 0), 2)
            # draw a box around the frame
            cv2.putText(
                frame,
                "face detected",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
            )
        if start_time is None:
            start_time = time.time()
        else:
            elapsed = time.time() - start_time
            if elapsed > BREAK_INTERVAL and not notified:
                notification.notify(
                    title="Time for a break!",
                    message="You've been watching the screen for too long!",
                    timeout=5,
                )
                notified = True
    else:
        start_time = None
        notificed = False
        cv2.putText(
            frame,
            "no face detected",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2,
        )

    cv2.imshow(
        "Webcam Feed -- press 'q' to quit", frame
    )  # show the captured frame in a window called "Webcam"

    # wait 1ms and check if q is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("exitting")
        break

cap.release()
cv2.destroyAllWindows()
