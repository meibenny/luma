import tkinter as tk
from tkinter import filedialog


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
        self.open_video_file.grid(row=1, column=1)

    def say_hi(self):
        print("hi there, everyone!")

    def select_file(self):
        file_path = filedialog.askopenfilename()
        self.video_file_name.set(file_path)


root = tk.Tk()
app = LumaAnalyzer(master=root)
app.mainloop()