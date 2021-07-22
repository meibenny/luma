import cv2

def grab_first_frame(filename):
    cap = cv2.VideoCapture(filename)
    _, frame = cap.read()
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    cap.release()
    return cv2image

class VideoPlayer:
    def __init__(self, filename):
        self.filename = filename
        self.cap = cv2.VideoCapture(filename)

    def grab_next_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        return cv2image

    def close_video(self):
        self.cap.release()