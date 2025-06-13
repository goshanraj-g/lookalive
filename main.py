import cv2  # import open cv

# open default webcam (1)
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

print("trying to find webcam")

if not cap.isOpened():
    print("swapping index.")
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("can't open webcam")
        exit()


print("webcam opened successfully")

# start loop to read frames from camera
while True:
    ret, frame = cap.read()
    if not ret:
        print("failed to grab frame")
        break # if the frame isn't captured
    
    cv2.imshow("Webcam Feed -- press 'q' to quit", frame) # show the captured frame in a window called "Webcam"
    
    # wait 1ms and check if q is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("exitting")
        break
    
cap.release()
cv2.destroyAllWindows()