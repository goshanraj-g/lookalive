# 👁️ LookAlive - 20-20-20 Eye Tracker

A real-time eye tracking tool that reminds you to take breaks according to the **20-20-20 Rule**: Every 20 minutes, look at something 20 feet away for 20 seconds to reduce digital eye strain.

## 🚀 Features

- Tracks your gaze direction using your webcam and MediaPipe Face Mesh.
- Identifies if you're looking at the center of the screen.
- If you've been looking at the screen for **20 minutes continuously**, it notifies you to take a **20-second break**.
- Displays real-time feedback in a window using OpenCV.

## 📦 Requirements

- Python 3.7+
- Webcam

### Install dependencies

```bash
pip install opencv-python mediapipe plyer
```

## ▶️ How to Run

```bash
python eye_tracker.py