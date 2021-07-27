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

    def get_frame_number(self):
        return self.cap.get(cv2.CAP_PROP_POS_FRAMES)

    def get_total_frames(self):
        return self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

    def get_processed_frames_as_percent(self):
        frames_processed = self.get_frame_number()
        total_frames = self.get_total_frames()
        return int(100* (frames_processed / total_frames) )