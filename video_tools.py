import cv2

def grab_first_frame(filename):
    cap = cv2.VideoCapture(filename)
    _, frame = cap.read()
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    cap.release()
    return cv2image