# 🚶‍♂️ People Counting System using YOLO

A simple people counting system that detects, tracks, and counts people entering and exiting an area using **YOLO** and **SORT tracking**.

This project is my **first hands-on experience with YOLO**, and although the system itself is relatively simple, it was a great learning experience that helped me understand many core concepts in computer vision through practical implementation.

---

## 📌 Features

- Person detection using **YOLOv8**
- Multi-object tracking with **SORT**
- In / Out people counting based on a virtual line
- Direction selection (Top-to-Bottom or Bottom-to-Top)
- Real-time visualization with bounding boxes, IDs, and counters
- Simple **Tkinter GUI** for interaction
- Video file input (CCTV-style videos)

---

## 🛠️ Technologies Used

- Python 3.11
- OpenCV
- YOLOv8 (Ultralytics)
- SORT Tracker
- NumPy
- Tkinter

---

## 📂 Project Structure

```text
people_counting_system/
│
├── people_counting.py        # Main application
├── sort.py                   # SORT tracker implementation
├── classes.txt               # Class labels (COCO)
├── requirements.txt          # Dependencies
├── sample_image/             # Saved frames (optional)
├── people_input/             # Input videos
└── README.md
⚙️ Installation

Clone the repository:

git clone https://github.com/your-username/people-counting-system.git
cd people-counting-system


Create and activate a virtual environment (recommended):

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate


Install dependencies:

pip install -r requirements.txt

▶️ How to Run
python people_counting.py

Steps inside the application:

Select the counting direction

Choose a video file

Select the line coordinate .txt file

Click Start Tracking

Press Q to stop video playback

📐 Line Coordinate File Format

The line coordinate file must contain two points (start and end of the line):

x1 y1
x2 y2


Example:

100 300
600 300

📊 Counting Logic

Each person is tracked using a unique ID

The midpoint of each bounding box is checked against the counting line

Direction of movement determines In or Out

A time threshold prevents double counting

🧠 What I Learned

Object detection pipelines with YOLO

Coordinate systems and resizing challenges

Tracking and ID assignment

Line-crossing logic for counting

Integrating computer vision with a GUI

Debugging real-world CV issues

🚀 Future Improvements

Support for live camera streams

Multiple counting lines

Export results to CSV

Improve robustness in crowded scenes

Use DeepSORT or ByteTrack

📷 Sample Output

Bounding boxes, tracking IDs, direction arrows, and real-time counters are displayed on the video stream.

🙌 Acknowledgments

Ultralytics YOLO

SORT Tracking algorithm

OpenCV community

💬 Feedback

This was a learning project, and I’d really appreciate any feedback, suggestions, or ideas for improvement.
Feel free to open an issue or reach out!


