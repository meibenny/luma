from os import name
import tkinter as tk
from tkinter import ttk
from tkinter import Scrollbar, filedialog
from tkinter.constants import BOTTOM, HORIZONTAL, NW, RIGHT, VERTICAL, X, Y
from PIL import Image, ImageTk, ImageDraw
import video_tools
import cv2
from rectangle_name_generator import rectangle_name
from multiprocessing import Process, freeze_support, SimpleQueue
import csv
from datetime import datetime
from threading import Thread


class VideoFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()

class DataPoint:
    def __init__(self, frame):
        self.frame = frame
        self.datapoints = {}

    def add_datapoint(self, name, metric):
        self.datapoints[name] = metric

def update_progressbar(progress_bar, q):
    while(True):
        if not q.empty():
            value = q.get()
            if value == "kill program":
                break
            progress_bar["value"] = value

def update_analyze_button(analysis_process, button):
    analysis_process.join()
    button["state"] = "normal"

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

        filename = video_file_name.split("/")[-1].split(".")[0]
        filename = filename + "." + file_postfix

        for name, _ in regions_of_interest.items():
            x1, y1, x2, y2 = rectangle_coordinates[name]

            draw = ImageDraw.Draw(img)
            draw.rectangle([x1, y1, x2, y2], outline="black")

        img.save("{}.png".format(filename), "png")

        while cv2image is not None:
            img = Image.fromarray(cv2image)
            frame_number = player.get_frame_number()
            datapoint = DataPoint(int(frame_number))

            for name, rectangle in regions_of_interest.items():
                x1, y1, x2, y2 = rectangle_coordinates[name]

                #print(x1, y1, x2, y2)

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
            
            datapoints.append(datapoint)

            progress_bar_q.put(player.get_processed_frames_as_percent())

            cv2image = player.grab_next_frame()

        write_datapoints_to_file(filename, datapoints, regions_of_interest)

        player.close_video()

class LumaAnalyzer(tk.Frame):
    def __init__(self, progress_bar_q, master=None):
        super().__init__(master)

        self.gen_rectangle_name = rectangle_name()

        self.master = master
        self.pack()
        self.video_file_name = tk.StringVar()
        self.draw_rectangle = tk.BooleanVar(self.master, value=False)
        self.regions_of_interest = {}
        self.region_of_interest_x = tk.StringVar(self.master, value="25")
        self.region_of_interest_y = tk.StringVar(self.master, value="50")
        self.progress_bar_q = progress_bar_q
        self.create_widgets()


    def create_widgets(self):
        
        self.video_file_label = tk.Label(self, text="Video File:")
        self.video_file_label.grid(row=0, column=0)

        self.video_file_name_label = tk.Label(self, textvariable=self.video_file_name)
        self.video_file_name_label.grid(row=0, column=1)

        self.select_video_file = tk.Button(self)
        self.select_video_file["text"] = "Select Video File"
        self.select_video_file["command"] = self.select_file
        self.select_video_file.grid(row=1, column=0)

        self.open_video_file = tk.Button(self)
        self.open_video_file["text"] = "Open Video File"
        self.open_video_file["command"] = self.display_first_frame
        self.open_video_file["state"] = "disabled"
        self.open_video_file.grid(row=1, column=1)

        self.video_display_frame = tk.Canvas(self.master, width=1024, height=768)
        hbar=Scrollbar(self.master,orient=HORIZONTAL)
        hbar.pack(side=BOTTOM,fill=X)
        hbar.config(command=self.video_display_frame.xview)
        vbar=Scrollbar(self.master,orient=VERTICAL)
        vbar.pack(side=RIGHT,fill=Y)
        vbar.config(command=self.video_display_frame.yview)
        self.video_display_frame.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.video_display_frame.bind("<Button-1>", self.get_mouse_coordinates)
        self.video_display_frame.pack()

        self.video_file_name.trace("w", self.open_video_active)

        self.draw_region_of_interest_button = tk.Button(self)
        self.draw_region_of_interest_button["text"] = "Draw Region of Interest"
        self.draw_region_of_interest_button["state"] = "disabled"
        self.draw_region_of_interest_button["command"] = self.toggle_draw_rectangle
        self.draw_region_of_interest_button.grid(row=1, column=2)

        self.drawing_roi_label = tk.Label(self, textvariable=self.draw_rectangle)
        self.drawing_roi_label.grid(row=1, column=3)

        self.regions_of_interest_combobox = ttk.Combobox(self)
        self.regions_of_interest_combobox["values"] = []
        self.regions_of_interest_combobox["postcommand"] = lambda: self.regions_of_interest_combobox.configure(values=list(self.regions_of_interest.keys()))
        self.regions_of_interest_combobox.grid(row=1, column=4)

        self.delete_region_of_interest_button = tk.Button(self)
        self.delete_region_of_interest_button["text"] = "Delete ROI"
        self.delete_region_of_interest_button["command"] = self.delete_region_of_interest
        self.delete_region_of_interest_button.grid(row=1, column=5)

        self.begin_analysis_button = tk.Button(self)
        self.begin_analysis_button["text"] = "Begin Analysis"
        self.begin_analysis_button["command"] = self.analyze_luma
        self.begin_analysis_button.grid(row=1, column=6)
        

        self.region_of_interest_x_label = tk.Label(self, text="ROI Length:")
        self.region_of_interest_x_label.grid(row=2, column=0)
        self.region_of_interest_x_entry = tk.Entry(self, textvariable=self.region_of_interest_x)
        self.region_of_interest_x_entry.grid(row=2, column=1)

        self.region_of_interest_x_label = tk.Label(self, text="ROI Width:")
        self.region_of_interest_x_label.grid(row=2, column=2)
        self.region_of_interest_x_entry = tk.Entry(self, textvariable=self.region_of_interest_y)
        self.region_of_interest_x_entry.grid(row=2, column=3)

        self.progress_bar = ttk.Progressbar(self, orient=tk.HORIZONTAL, length = 100, mode = 'determinate')
        self.progress_bar["value"] = 0
        self.progress_bar.grid(row=2, column=4)


    def say_hi(self):
        print("hi there, everyone!")

    def select_file(self):
        file_path = filedialog.askopenfilename()
        self.video_file_name.set(file_path)

    def delete_region_of_interest(self):
        roi_key = self.regions_of_interest_combobox.get()
        self.video_display_frame.delete(self.regions_of_interest.get(roi_key))
        self.regions_of_interest.pop(roi_key, None)

    def analyze_luma(self):
        self.draw_rectangle.set(False)
        self.begin_analysis_button["state"] = "disabled"

        rectangle_coordinates = {}
        for name, rectangle in self.regions_of_interest.items():
            x1, y1, x2, y2 = self.video_display_frame.coords(rectangle)
            rectangle_coordinates[name] = [x1, y1, x2, y2]

        analyzer = Process(target=analyze_video, args=(self.video_file_name.get(), self.regions_of_interest, rectangle_coordinates, self.progress_bar_q))
        analyzer.start()
        begin_analysis_button_update_thread = Thread(target=update_analyze_button, args=(analyzer, self.begin_analysis_button))
        begin_analysis_button_update_thread.start()


        # player = video_tools.VideoPlayer(self.video_file_name.get())
        # cv2image = player.grab_next_frame()
        # img = Image.fromarray(cv2image)

        # for _, rectangle in self.regions_of_interest.items():
        #     x1, y1, x2, y2 = self.video_display_frame.coords(rectangle)

        #     draw = ImageDraw.Draw(img)
        #     draw.rectangle([x1, y1, x2, y2], outline="black")
        #     img.save("test_image.png", "png")


        # while cv2image is not None:
        #     img = Image.fromarray(cv2image)
        #     imgtk = ImageTk.PhotoImage(image=img)
        #     self.video_display_frame.imgtk = imgtk
        #     self.video_display_frame.itemconfig(self.image_on_video_display, image = imgtk)
        #     cv2image = player.grab_next_frame()
        # player.close_video()


    def get_mouse_coordinates(self, event):
        canvas_coords = event.widget
        c_x = canvas_coords.canvasx(event.x)
        c_y = canvas_coords.canvasy(event.y)

        if self.draw_rectangle.get():
            region = self.video_display_frame.create_rectangle(c_x, c_y, c_x + int(self.region_of_interest_x.get()), c_y + int(self.region_of_interest_y.get()))
            self.regions_of_interest[str(next(self.gen_rectangle_name))] = region

    def open_video_active(self, *args):
        filename = self.video_file_name.get()
        if filename:
            self.open_video_file["state"] = "normal"
            self.draw_region_of_interest_button["state"] = "normal"
        else:
            self.open_video_file["state"] = "disabled"
            self.draw_region_of_interest_button["state"] = "disabled"

    def toggle_draw_rectangle(self):
        self.draw_rectangle.set(not self.draw_rectangle.get())

    def display_first_frame(self):
        cv2image = video_tools.grab_first_frame(self.video_file_name.get())
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_display_frame.imgtk = imgtk
        self.image_on_video_display = self.video_display_frame.create_image(0, 0, anchor = NW, image=imgtk)
        self.video_display_frame.config(scrollregion=self.video_display_frame.bbox(tk.ALL))


if "__main__" == __name__:
    freeze_support()
    root = tk.Tk()
    progress_bar_q = SimpleQueue()
    app = LumaAnalyzer(progress_bar_q, master=root)
    progress_bar_update_thread = Thread(target=update_progressbar, args=(app.progress_bar, progress_bar_q))
    progress_bar_update_thread.start()
    app.mainloop()
    progress_bar_q.put("kill program")
    progress_bar_update_thread.join()