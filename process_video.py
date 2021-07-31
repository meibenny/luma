import cProfile
import video_tools
from datetime import datetime
from PIL import Image, ImageDraw
from pathlib import Path
import csv
from DataPoint import DataPoint

def process_points(regions_of_interest, rectangle_coordinates, img, datapoint):

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

def write_datapoints_to_file(filename, datapoints, regions_of_interest):
    metrics = 0

    # for datapoint in datapoints:
    #     metrics += len(datapoint.datapoints)
    #     print(datapoint.datapoints)

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

def analyze_video(video_file_name, regions_of_interest, rectangle_coordinates, progress_bar_q):
        pr = cProfile.Profile()
        pr.enable()
        player = video_tools.VideoPlayer(video_file_name)

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

        cv2image = player.grab_next_frame()
        
        if cv2image is None:
            return

        img = Image.fromarray(cv2image)

        video_file_path = Path(video_file_name)
        video_file_parent = video_file_path.parent.absolute()

        output_filename = video_file_name.split("/")[-1].split(".")[0]
        output_filename = output_filename + "." + file_postfix
        output_filename = Path(video_file_parent, output_filename)

        for name, _ in regions_of_interest.items():
            x1, y1, x2, y2 = rectangle_coordinates[name]

            draw = ImageDraw.Draw(img)
            draw.rectangle([x1, y1, x2, y2], outline="black")

        img.save("{}.png".format(output_filename), "png")

        while cv2image is not None:
            img = Image.fromarray(cv2image)
            frame_number = player.get_frame_number()
            datapoint = DataPoint(int(frame_number))

            process_points(regions_of_interest, rectangle_coordinates, img, datapoint)

            # for name, rectangle in regions_of_interest.items():
            #     x1, y1, x2, y2 = rectangle_coordinates[name]

            #     #print(x1, y1, x2, y2)

            #     luma_values = 0
            #     for x in range(int(x1), int(x2)):
            #         for y in range(int(y1), int(y2)):
            #             value = img.getpixel((x, y))
            #             r = value[0]
            #             g = value[1]
            #             b = value[2]

            #             # See Y' 601. https://en.wikipedia.org/wiki/Luma_(video)
            #             luma_value = 0.299 * r + 0.587 * g + 0.114 * b
            #             luma_values += luma_value


            #     datapoint.add_datapoint(name, luma_values)
            
            datapoints.append(datapoint)

            progress_bar_q.put(player.get_processed_frames_as_percent())

            cv2image = player.grab_next_frame()

        write_datapoints_to_file(output_filename, datapoints, regions_of_interest)

        player.close_video()
        pr.disable()
        pr.print_stats(sort='tottime')