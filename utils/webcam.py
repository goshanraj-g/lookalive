import cv2

def get_webcam_capture():
    # try to use CAP_DSHOW on Windows, fallback for others [CHANGE THIS IF YOU'RE NOT ON WINDOWS!]
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if hasattr(cv2, 'CAP_DSHOW') else 0)
    if not cap.isOpened():
        raise RuntimeError("Cannot open webcam")
    return cap