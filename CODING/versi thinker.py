import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import psutil  # Import psutil for battery status
import threading  # Import threading for running update in a separate thread
import time
import screen_brightness_control as sbc  # Import screen_brightness_control


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenCV with Tkinter")

        # Setup the video capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open video capture")
            return

        # Get the width and height of the video capture
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # dimension in frame
        self.new_frame_width = 1600
        self.new_frame_height = 890

        # Create a canvas that can fit the video capture size
        self.canvas = tk.Canvas(root, width=self.width, height=self.height)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame for sliders and icons on the right
        self.slider_frame = tk.Frame(root)
        self.slider_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)

        # Load and resize icons
        self.clahe_icon = Image.open(
            "vena.png").resize((80, 80), Image.LANCZOS)
        self.clahe_icon = ImageTk.PhotoImage(self.clahe_icon)

        self.zoom_icon = Image.open("zoom.png").resize((80, 80), Image.LANCZOS)
        self.zoom_icon = ImageTk.PhotoImage(self.zoom_icon)

        self.brightness_icon = Image.open(
            "brightness.png").resize((80, 80), Image.LANCZOS)
        self.brightness_icon = ImageTk.PhotoImage(self.brightness_icon)

        # Icons and sliders for CLAHE, zoom, and brightness
        self.clahe_clip_limit = tk.DoubleVar(value=2.0)
        self.zoom = tk.DoubleVar(value=1.0)
        # Initial brightness value (0-100)
        self.brightness = tk.DoubleVar(value=50)

        self.battery_label = tk.Label(self.slider_frame)
        self.battery_label.grid(row=0, column=0, pady=(0, 0))

        self.brightness_label = tk.Label(
            self.slider_frame, image=self.brightness_icon)
        self.brightness_label.grid(row=1, column=0, pady=(200, 10))

        self.slider_brightness = tk.Scale(self.slider_frame, from_=0, to=100, resolution=1,
                                          orient=tk.HORIZONTAL, label="BRIGHTNESS", variable=self.brightness)
        self.slider_brightness.grid(
            row=2, column=0, padx=5, pady=5, sticky="ew")

        self.clahe_label = tk.Label(self.slider_frame, image=self.clahe_icon)
        self.clahe_label.grid(row=3, column=0, pady=(20, 10))

        self.slider_clahe = tk.Scale(self.slider_frame, from_=1, to=10, resolution=1,
                                     orient=tk.HORIZONTAL, label="CONTRAS", variable=self.clahe_clip_limit)
        self.slider_clahe.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

        self.zoom_label = tk.Label(self.slider_frame, image=self.zoom_icon)
        self.zoom_label.grid(row=5, column=0, pady=(20, 10))

        self.slider_zoom = tk.Scale(self.slider_frame, from_=1, to=3, resolution=1,
                                    orient=tk.HORIZONTAL, label="ZOOM", variable=self.zoom)
        self.slider_zoom.grid(row=6, column=0, padx=5, pady=5, sticky="ew")

        # Bind the brightness slider to update the screen brightness
        self.slider_brightness.bind("<Motion>", self.update_brightness)

        # Flag to control the video loop
        self.video_loop_flag = True

        # Start battery status update thread
        self.start_battery_status_update()

        # Start video loop
        self.video_loop()

    def start_battery_status_update(self):
        # Start a new thread to update battery status
        threading.Thread(target=self.update_battery_status,
                         daemon=True).start()

    def update_battery_status(self):
        while True:
            percent = psutil.sensors_battery().percent
            plugged = psutil.sensors_battery().power_plugged

            # Update battery status text
            status_text = f"Battery: {percent}% {'(Charging)' if plugged else '(Discharging)'}"
            self.battery_label.config(text=status_text)

            # Set battery icon based on percentage
            if percent >= 80:
                self.update_battery_icon("bat_full.png")
            elif percent >= 60:
                self.update_battery_icon("bat_3.png")
            elif percent >= 40:
                self.update_battery_icon("bat_2.png")
            elif percent >= 20:
                self.update_battery_icon("bat_1.png")
            else:
                self.update_battery_icon("bat_low.png")

            # Sleep for a while before updating again (e.g., every 5 seconds)
            time.sleep(5)

    def update_battery_icon(self, icon_path):
        # Load and resize battery icon
        battery_icon = Image.open(icon_path).resize((70, 70), Image.LANCZOS)
        self.battery_icon = ImageTk.PhotoImage(battery_icon)

        # Update battery label with new icon
        self.battery_label.config(image=self.battery_icon)
        # Keep reference to avoid garbage collection
        self.battery_label.image = self.battery_icon

    def video_loop(self):
        if self.video_loop_flag:
            ret, frame = self.cap.read()
            if ret:
                frame = self.apply_adjustments(frame)
                self.show_frame(frame)
            else:
                print("Error: Failed to read frame from video capture")
            # Call this function again after 10 milliseconds
            self.root.after(10, self.video_loop)

    def apply_adjustments(self, frame):
        # Apply CLAHE
        clahe = cv2.createCLAHE(
            clipLimit=self.clahe_clip_limit.get(), tileGridSize=(8, 8))
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l2 = clahe.apply(l)
        lab = cv2.merge((l2, a, b))
        frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        # Apply zoom
        zoom_factor = self.zoom.get()
        if zoom_factor > 1:
            frame = self.zoom_frame(frame, zoom_factor)

        return frame

    def update_brightness(self, event):
        # Get the brightness value from the slider
        brightness_value = self.brightness.get()
        # Update the screen brightness
        sbc.set_brightness(brightness_value)

    def zoom_frame(self, frame, zoom_factor):
        center_x, center_y = frame.shape[1] // 2, frame.shape[0] // 2
        radius_x, radius_y = int(
            center_x / zoom_factor), int(center_y / zoom_factor)

        min_x, max_x = center_x - radius_x, center_x + radius_x
        min_y, max_y = center_y - radius_y, center_y + radius_y

        cropped_frame = frame[min_y:max_y, min_x:max_x]
        frame = cv2.resize(cropped_frame, (frame.shape[1], frame.shape[0]))

        return frame

    def show_frame(self, frame):
        # Resize the frame to fit the canvas
        frame = cv2.resize(
            frame, (self.new_frame_width, self.new_frame_height))
        # Convert the frame to RGB format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert the frame to a PhotoImage
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        # Update the image on the canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        self.imgtk = imgtk  # Keep a reference to avoid garbage collection

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
