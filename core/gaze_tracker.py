import cv2


def get_gaze_direction(landmarks, frame_shape):
    h, w = frame_shape[:2]
    x_left = int(landmarks[474].x * w)
    x_right = int(landmarks[469].x * w)
    eye_center_x = (x_left + x_right) // 2

    if eye_center_x < w * 0.4:
        return "left"
    elif eye_center_x > w * 0.6:
        return "right"
    else:
        return "center"
