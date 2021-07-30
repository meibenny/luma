from dataclasses import dataclass
from PIL import Image

@dataclass
class VideoFrame:
    
    image: Image
    frame_number: int
    processed_percent: int