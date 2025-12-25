import cv2
from sort import *
from ultralytics import YOLO
from collections import defaultdict
import time
import sys
import ast
import numpy as np
import tkinter as tk
from tkinter import messagebox, filedialog
from threading import Thread

# Initialize global variables
in_count = 0
out_count = 0
choice = None
cap = None
tracker = None
model = None
stop_tracking_flag = False  # Flag to stop the video processing thread
line_coordinate_txt_file = None

# Helper function to check which side of the line a point is on
def point_side_of_line(point, line_start, line_end):
    return (point[0] - line_start[0]) * (line_end[1] - line_start[1]) - \
           (point[1] - line_start[1]) * (line_end[0] - line_start[0])


def load_line_coordinates(file_path):
    """
    Load coordinates from a text file containing a numpy array representation.

    Args:
        file_path (str): Path to the text file.

    Returns:
        np.ndarray: A 2D numpy array of points if successful.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read().strip()
            
            # Remove the 'np.array' prefix and evaluate the content as a Python literal
            if content.startswith("np.array"):
                content = content[len("np.array"):].strip()
                points = np.array(ast.literal_eval(content))
            else:
                raise ValueError("Input file does not contain a valid numpy array representation.")
            
            return points
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error reading the file: {e}")
        return None


# Initialize Tkinter window for input and result display
def start_tracking():
    global in_count, out_count, tracker, model, cap, choice, stop_tracking_flag

    # Get the choice for direction
    if choice is None:
        messagebox.showerror("Error", "Please choose a direction for counting.")
        return

    # Ask user to select video file if not already selected
    if cap is None:
        messagebox.showerror("Error", "No video file selected.")
        return

    model = YOLO('yolov8n.pt')
    tracker = Sort(max_age=30)

    # Load class names
    classnames = []
    with open('classes.txt', 'r') as f:
        classnames = f.read().splitlines()

    line_coordinates = load_line_coordinates(line_coordinate_txt_file)
    print(type(line_coordinates))
    print("line_coordinates",line_coordinates)

    if line_coordinates is not None:
        # Access the first two rows (index 0 and 1)
        line_start = line_coordinates[0]
        print("line_start",type(line_start))
        line_end = line_coordinates[1]
        print("line_end",type(line_end))

        print(f"Point 0: {line_start}")
        print(f"Point 1: {line_end}")

    else:
        messagebox.showerror("Error", "not valid polygon coordinate")

    tracked_positions = {}
    crossed_ids = set()
    last_count_time = defaultdict(lambda: 0)
    min_crossing_time = 1

    def process_video():
        global in_count, out_count

        while not stop_tracking_flag:
            ret, frame = cap.read()
            if not ret:
                break

            detections = np.empty((0, 5))
            results = model(frame, stream=1)

            # Extract bounding boxes for "person" class
            for info in results:
                boxes = info.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    conf = box.conf[0]
                    classindex = box.cls[0]
                    object_detected = classnames[int(classindex)]

                    if object_detected == 'person' and conf > 0.3:
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        new_detections = np.array([x1, y1, x2, y2, conf])
                        detections = np.vstack((detections, new_detections))

                        # Draw the bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, f"ID: {int(box.cls[0])}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Update tracker and draw the counting line
            track_result = tracker.update(detections)
            cv2.line(frame, tuple(line_start), tuple(line_end), (0, 255, 255), 3)

             # Get the selected direction
            selected_direction = direction_choice.get()

            # Calculate the midpoint of the line
            mid_x = (line_start[0] + line_end[0]) // 2
            mid_y = (line_start[1] + line_end[1]) // 2


            if selected_direction == "1":  # In: Top-to-Bottom, Out: Bottom-to-Top
                # Draw "In" arrow (Top-to-Bottom)
                cv2.arrowedLine(frame, (mid_x, mid_y - 80), (mid_x, mid_y + 80), (0, 255, 0), 4, tipLength=0.4)
                cv2.putText(frame, "In", (mid_x + 10, mid_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Draw "Out" arrow (Bottom-to-Top)
                cv2.arrowedLine(frame, (mid_x, mid_y + 80), (mid_x, mid_y - 80), (0, 0, 255), 4, tipLength=0.4)
                cv2.putText(frame, "Out", (mid_x + 10, mid_y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            elif selected_direction == "2":  # In: Bottom-to-Top, Out: Top-to-Bottom
                # Draw "In" arrow (Bottom-to-Top)
                cv2.arrowedLine(frame, (mid_x, mid_y + 80), (mid_x, mid_y - 80), (0, 255, 0), 4, tipLength=0.4)
                cv2.putText(frame, "In", (mid_x + 10, mid_y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Draw "Out" arrow (Top-to-Bottom)
                cv2.arrowedLine(frame, (mid_x, mid_y - 80), (mid_x, mid_y + 80), (0, 0, 255), 4, tipLength=0.4)
                cv2.putText(frame, "Out", (mid_x + 10, mid_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # In Count rectangle
            in_rect_start = (20, 20)  # Top-left corner
            in_rect_end = (300, 100)  # Bottom-right corner
            cv2.rectangle(frame, in_rect_start, in_rect_end, (0, 255, 0), -1)  # Filled rectangle
            cv2.putText(frame, f"In count:{in_count}", (30, 75), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)

            # Out Count rectangle
            out_rect_start = (20, 120)  # Top-left corner
            out_rect_end = (300, 200)  # Bottom-right corner
            cv2.rectangle(frame, out_rect_start, out_rect_end, (0, 0, 255), -1)  # Filled rectangle
            cv2.putText(frame, f"Out count:{out_count}", (30, 175), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)

            for result in track_result:
                x1, y1, x2, y2, obj_id = map(int, result)
                box_mid = np.array([(x1 + x2) // 2, (y1 + y2) // 2])


                # Check if the person is crossing the line
                crossing = False

                if obj_id in tracked_positions:
                    prev_position = tracked_positions[obj_id]
                    current_position = point_side_of_line(box_mid, line_start, line_end)

                    # Apply counting logic based on user choice
                    current_time = time.time()

                    if current_time - last_count_time[obj_id] > min_crossing_time:
                        if choice == 1:  # In: Bottom-to-Top, Out: Top-to-Bottom
                            if prev_position > 0 and current_position <= 0:
                                if obj_id not in crossed_ids:
                                    in_count += 1
                                    crossed_ids.add(obj_id)
                                    last_count_time[obj_id] = current_time
                                    crossing = True
                            elif prev_position < 0 and current_position >= 0:
                                if obj_id not in crossed_ids:
                                    out_count += 1
                                    crossed_ids.add(obj_id)
                                    last_count_time[obj_id] = current_time
                                    crossing = True
                        elif choice == 2:  # In: Top-to-Bottom, Out: Bottom-to-Top
                            if prev_position < 0 and current_position >= 0:
                                if obj_id not in crossed_ids:
                                    in_count += 1
                                    crossed_ids.add(obj_id)
                                    last_count_time[obj_id] = current_time
                                    crossing = True
                            elif prev_position > 0 and current_position <= 0:
                                if obj_id not in crossed_ids:
                                    out_count += 1
                                    crossed_ids.add(obj_id)
                                    last_count_time[obj_id] = current_time
                                    crossing = True

                # Update tracked positions
                tracked_positions[obj_id] = point_side_of_line(box_mid, line_start, line_end)

                # Update in and out count on the Tkinter window
                window.after(1, update_display)

            # Resize frame to fit within window (ensure frame is resized proportionally)
            height, width = frame.shape[:2]
            frame = cv2.resize(frame, (int(window.winfo_width()), int(window.winfo_height())))

            # Show resized frame
            cv2.imshow('Video Feed', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    # Start the video processing in a separate thread
    thread = Thread(target=process_video)
    thread.start()

def stop_tracking():
    global stop_tracking_flag
    stop_tracking_flag = True
    messagebox.showinfo("Tracking Stopped", "Video processing has been stopped.")
    sys.exit(1)

# Function to choose the video file
def choose_video_file():
    global cap
    video_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
    if video_path:
        cap = cv2.VideoCapture(video_path)
        start_button.config(state="normal")  # Enable start button once video is selected
    else:
        messagebox.showerror("Error", "Please choose a video file.")
        return

# Function to choose the txt file
def choose_line_coordinate_txt_file():
    global line_coordinate_txt_file
    line_coordinate_txt_file = filedialog.askopenfilename(title="Select line coordinate txt  File", filetypes=[("Txt Files", "*.txt")])
    if line_coordinate_txt_file:
        print("line_coordinate_txt_file",line_coordinate_txt_file)

    else:
        messagebox.showerror("Error", "Please choose a polygon coordinates file.")
        return

# Tkinter GUI setup
def update_display():
    in_count_label.config(text=f"In Count: {in_count}")
    out_count_label.config(text=f"Out Count: {out_count}")

def set_in_out_direction():
    global choice
    choice = int(direction_choice.get())
    messagebox.showinfo("Direction Set", "Direction for counting is set")

# Tkinter window initialization
window = tk.Tk()
window.title("People Counting System")
window.geometry("800x600")  # Set initial window size
window.configure(bg="#e0f7fa")  # Light blue background

# Header Label
header_label = tk.Label(window, text="People Counting System", bg="#00796b", fg="white", font=('Arial', 18, 'bold'))
header_label.pack(fill=tk.X, pady=10)

# Input for direction choice
direction_label = tk.Label(window, text="Choose direction for counting:", bg="#e0f7fa", font=('Arial', 12))
direction_label.pack(pady=5)

direction_choice = tk.StringVar()
direction_choice.set("1")  # Default selection
direction_radio1 = tk.Radiobutton(window, text="In: Bottom-to-Top, Out: Top-to-Bottom", variable=direction_choice, value="1", bg="#e0f7fa", font=('Arial', 12))
direction_radio1.pack()
direction_radio2 = tk.Radiobutton(window, text="In: Top-to-Bottom, Out: Bottom-to-Top", variable=direction_choice, value="2", bg="#e0f7fa", font=('Arial', 12))
direction_radio2.pack()

# Set direction button
set_button = tk.Button(window, text="Set Direction", command=set_in_out_direction, bg="#00796b", fg="white", font=('Arial', 12))
set_button.pack(pady=10)

# Choose Video file
video_button = tk.Button(window, text="Choose Video File", command=choose_video_file, bg="#00796b", fg="white", font=('Arial', 12))
video_button.pack(pady=10)

# Choose txt file
txt_button = tk.Button(window, text="Choose line coordinate txt File", command=choose_line_coordinate_txt_file, bg="#00796b", fg="white", font=('Arial', 12))
txt_button.pack(pady=10)

# Start Tracking button (disabled initially)
start_button = tk.Button(window, text="Start Tracking", command=start_tracking, state="disabled", bg="#00796b", fg="white", font=('Arial', 12))
start_button.pack(pady=10)

# Stop Tracking button
stop_button = tk.Button(window, text="Stop Tracking", command=stop_tracking, bg="#d32f2f", fg="white", font=('Arial', 12))
stop_button.pack(pady=10)

# Labels for countings
in_count_label = tk.Label(window, text=f"In Count: {in_count}", bg="#e0f7fa", font=('Arial', 12))
in_count_label.pack(pady=5)

out_count_label = tk.Label(window, text=f"Out Count: {out_count}", bg="#e0f7fa", font=('Arial', 12))
out_count_label.pack(pady=5)

# Start the Tkinter event loop
window.mainloop()





