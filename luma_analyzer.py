import tkinter as tk
from tkinter import Scrollbar, filedialog
from tkinter.constants import BOTTOM, HORIZONTAL, NW, RIGHT, VERTICAL, X, Y
from PIL import Image, ImageTk
import video_tools
import cv2

class VideoFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()


class LumaAnalyzer(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.video_file_name = tk.StringVar()
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
        self.open_video_file.grid(row=1, column=1)

        self.video_display_frame = tk.Canvas(self.master, width=1024, height=768)
        hbar=Scrollbar(self.master,orient=HORIZONTAL)
        hbar.pack(side=BOTTOM,fill=X)
        hbar.config(command=self.video_display_frame.xview)
        vbar=Scrollbar(self.master,orient=VERTICAL)
        vbar.pack(side=RIGHT,fill=Y)
        vbar.config(command=self.video_display_frame.yview)
        self.video_display_frame.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.video_display_frame.pack()

    def say_hi(self):
        print("hi there, everyone!")

    def select_file(self):
        file_path = filedialog.askopenfilename()
        self.video_file_name.set(file_path)

    def display_first_frame(self):
        
        #cap = cv2.VideoCapture(self.video_file_name.get())
        #_, frame = cap.read()
        #cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

        cv2image = video_tools.grab_first_frame(self.video_file_name.get())
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_display_frame.imgtk = imgtk
        self.video_display_frame.create_image(0, 0, anchor = NW, image=imgtk)
        self.video_display_frame.config(scrollregion=self.video_display_frame.bbox(tk.ALL))



        #frame = video_tools.grab_first_frame(self.video_file_name.get())
        #image = Image.fromarray(frame)
        #imagetk = ImageTk.PhotoImage(image=image)
        #print("displaying image")
        #self.video_display_frame.configure(image=imagetk, textvariable="Hello")
        #print("image displayed")


root = tk.Tk()
app = LumaAnalyzer(master=root)
app.mainloop()