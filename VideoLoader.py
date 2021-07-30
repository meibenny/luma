import VideoTools
from VideoFrame import VideoFrame
from multiprocessing import Queue
from PIL import Image

class VideoLoader:
    
    def __init__(self, filename: str, video_queue: Queue):
        self.filename = filename
        self.video_queue = video_queue
        self.player = None

    def open_video(self):
        self.player = VideoTools.VideoPlayer(self.filename)

    def load_frames(self):

        cv2image = self.player.grab_next_frame()
        while cv2image is not None:
            img = Image.fromarray(cv2image)
            frame_number = self.player.get_frame_number()
            processed_percent = self.player.get_processed_frames_as_percent()
            video_frame = VideoFrame(img, frame_number, processed_percent)
            self.video_queue.put(video_frame)
            cv2image = self.player.grab_next_frame()
        self.player.close_video()
        video_frame = VideoFrame(None, -1, 100)
        self.video_queue.put(video_frame)


