# LookAlive

LookAlive monitors your gaze through a webcam feed so you can manage screen time without having to watch a clock. It issues distance warnings when your face gets too close, keeps a compact overlay for quick diagnostics, creates session heatmaps, and minimizes to the tray with notifications.

## Features
- real-time iris and gaze tracking using MediaPipe Face Mesh
- distance alerts when the face is too close to the camera
- compact overlay, debug view, and progress tracking for focus sessions
- heatmap generation plus hourly and weekly session summaries
- system tray controls with native notifications and quick keyboard shortcuts

## Requirements
- Windows 10 or later
- Python 3.11 or newer (virtual environment recommended)
- Webcam access granted to the Python process

## Setup (source)
1. Clone the repository and activate your virtual environment.
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Launch from source:
   ```powershell
   python main.py
   ```

## Packaging
Build a self-contained executable with PyInstaller. MediaPipe models must be bundled manually as shown below:
```powershell
pyinstaller main.py --onefile --name LookAlive \
  --add-data "venv\Lib\site-packages\mediapipe\modules\face_landmark\face_landmark_front_cpu.binarypb;mediapipe/modules/face_landmark" \
  --add-data "venv\Lib\site-packages\mediapipe\modules\face_landmark\face_landmark_with_attention.tflite;mediapipe/modules/face_landmark" \
  --add-data "venv\Lib\site-packages\mediapipe\modules\face_detection\face_detection_short_range.tflite;mediapipe/modules/face_detection"
```
Run `dist\LookAlive.exe` after the build to verify functionality.

## Installer / Distribution
PyInstaller writes the packaged binary and supporting files into `dist`. Ship the entire `dist` contents or point your installer (see `installer.iss`) to that folder. Running `dist\LookAlive.exe` installs or launches LookAlive depending on your deployment flow.

## Demo (placeholder)
Add a short description or link to a demo recording here once available. Mention whether the demo shows the overlay, system tray interaction, or heatmap visualization so reviewers know what to expect.

## Troubleshooting
- If PyInstaller reports missing MediaPipe models, ensure the files exist under `venv\Lib\site-packages\mediapipe\modules` and re-run the command above with the correct paths.
- If the build fails because `LookAlive.exe` is in use, close the running instance (check Task Manager) before rebuilding.
- Reinstall MediaPipe when files disappear from the virtual environment: `pip install --force-reinstall mediapipe`.# LookAlive

LookAlive tracks your eyes via webcam to keep screen time healthy. It monitors where you are looking, warns when you are too close or focused for too long, supports a compact overlay, displays session heatmaps, and minimizes to the system tray.

## Features
- real-time iris and gaze tracking with MediaPipe Face Mesh
- distance warnings when the face is too close to the camera
- compact overlay and optional debugging view with progress visualization
- heatmap generation and hourly/weekly session stats
- system tray control and native notifications

## Requirements
- Windows 10 or later
- Python 3.11+ (tested)
- Webcam

## Setup
1. Clone the repo and activate your virtual environment.
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Run the app from source:
   ```powershell
   python main.py
   ```

## Packaging
Use PyInstaller to build a single executable. MediaPipe models must be included manually.
```powershell
pyinstaller main.py --onefile --name LookAlive \
  --add-data "venv\Lib\site-packages\mediapipe\modules\face_landmark\face_landmark_front_cpu.binarypb;mediapipe/modules/face_landmark" \
  --add-data "venv\Lib\site-packages\mediapipe\modules\face_landmark\face_landmark_with_attention.tflite;mediapipe/modules/face_landmark" \
  --add-data "venv\Lib\site-packages\mediapipe\modules\face_detection\face_detection_short_range.tflite;mediapipe/modules/face_detection"
```
Rebuild whenever you change MediaPipe usage. After the build, run `dist\LookAlive.exe` to verify the package.

## Installer
Use the existing `installer.iss` with Inno Setup if you need an installer. The script references the `dist` folder output from PyInstaller.

## Troubleshooting
- If the EXE reports a missing MediaPipe file or PyInstaller cannot delete `LookAlive.exe`, make sure the file is not running and add the required file paths to the command shown above.
- Reinstall MediaPipe (`pip install --force-reinstall mediapipe`) if files go missing from `venv`.# 👁️ LookAlive - 20-20-20 Eye Tracker

A real-time eye tracking tool that reminds you to take breaks according to the **20-20-20 Rule**: Every 20 minutes, look at something 20 feet away for 20 seconds to reduce digital eye strain

## 🚀 Features

- Tracks your gaze direction using your webcam and MediaPipe Face Mesh
- Identifies if you're looking at the center of the screen
- If you've been looking at the screen for **20 minutes continuously**, it notifies you to take a **20-second break**
- Displays real-time feedback in a window using OpenCV

## 📦 Requirements

- Python 3.7+
- Webcam

### Install dependencies

```bash
pip install opencv-python mediapipe plyer
```

## ▶️ How to Run

```bash
python main.py
```

## 📸 How It Works

- Uses **MediaPipe Face Mesh** to detect iris landmarks (`469` for right eye, `474` for left eye)
- Calculates the average **x-position** of both irises to determine if you're looking:
  - **Left**
  - **Right**
  - **Center**
- If you're looking **center** for **20 minutes straight**, you’ll get a notification
- The program starts a **20-second break period**, after which it lets you return to the screen

---

## 🔔 Notifications

Uses **Plyer** to send native OS notifications:

- _"Look 20 feet away for 20 seconds!"_
- _"You can return to the screen"_

---

## 🧠 Libraries Used

- **OpenCV**: For webcam access and drawing on frames
- **MediaPipe**: For high-performance facial landmark detection
- **Plyer**: For cross-platform notifications

---
