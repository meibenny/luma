import cProfile
import VideoTools
from datetime import datetime
from PIL import Image, ImageDraw
from pathlib import Path
import csv
from DataPoint import DataPoint
from multiprocessing import Process, SimpleQueue, Queue
from VideoLoader import VideoLoader

def load_video_frames(filename:str, queue: Queue):
    loader = VideoLoader(filename, queue)
    loader.open_video()
    loader.load_frames()


def process_points(regions_of_interest: dict, rectangle_coordinates: dict, img, datapoint: DataPoint):

    for name, rectangle in regions_of_interest.items():
        x1, y1, x2, y2 = rectangle_coordinates[name]

        luma_values = 0
        for x in range(int(x1), int(x2)):
            for y in range(int(y1), int(y2)):
                value = img.getpixel((x, y))
                r = value[0]
                g = value[1]
                b = value[2]

                # See Y' 601. https://en.wikipedia.org/wiki/Luma_(video)
                luma_value = 0.299 * r + 0.587 * g + 0.114 * b
                luma_values += luma_value


        datapoint.add_datapoint(name, luma_values)

DataPoints = [DataPoint]

def write_datapoints_to_file(filename: str, datapoints: DataPoints, regions_of_interest: dict):
    metrics = 0

    with open("{}.csv".format(filename), "w", newline='', encoding="utf-8") as csvfile:
        field_names = ["frame"]
        roi_names = ["ROI " + name for name, _ in regions_of_interest.items()]
        field_names.extend(roi_names)
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        
        for datapoint in datapoints:
            row_data = {"frame": datapoint.frame}
            for roi, metric in datapoint.datapoints.items():
                #writer.writerow({"frame": datapoint.frame, "ROI": roi, "Luma": metric})
                row_data["ROI " + roi] = metric
            writer.writerow(row_data)

def analyze_video(video_file_name:str , regions_of_interest: dict, rectangle_coordinates: dict, progress_bar_q: SimpleQueue):
        starttime = datetime.now()
        # pr = cProfile.Profile()
        # pr.enable()

        progress_bar_q.put(1)
        current_datetime = datetime.now()
        file_postfix = "{}.{}.{}-{}.{}.{}.{}".format(
            current_datetime.year,
            current_datetime.month,
            current_datetime.day,
            current_datetime.hour,
            current_datetime.minute,
            current_datetime.second,
            current_datetime.microsecond
        )

        datapoints = []

        video_file_path = Path(video_file_name)
        video_file_parent = video_file_path.parent.absolute()

        output_filename = video_file_name.split("/")[-1].split(".")[0]
        output_filename = output_filename + "." + file_postfix
        output_filename = Path(video_file_parent, output_filename)

        video_queue = Queue(50)
        video_loader = Process(target=load_video_frames, args=(video_file_name, video_queue))
        video_loader.start()

        img = video_queue.get()

        for name, _ in regions_of_interest.items():
            x1, y1, x2, y2 = rectangle_coordinates[name]

            draw = ImageDraw.Draw(img.image)
            draw.rectangle([x1, y1, x2, y2], outline="black")

        img.image.save("{}.png".format(output_filename), "png")

        while img.frame_number != -1:
            frame_number = img.frame_number
            datapoint = DataPoint(int(frame_number))

            process_points(regions_of_interest, rectangle_coordinates, img.image, datapoint)
            
            datapoints.append(datapoint)

            progress_bar_q.put(img.processed_percent)

            img = video_queue.get()

        write_datapoints_to_file(output_filename, datapoints, regions_of_interest)

        # pr.disable()
        # pr.print_stats(sort='tottime')
        endtime = datetime.now()
        elapsed = endtime - starttime
        print("Elapsed Time")
        print(elapsed)