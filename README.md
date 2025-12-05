# LookAlive 👀

LookAlive monitors your gaze through a webcam feed so you can manage screen time without having to watch a clock. It issues distance warnings when your face gets too close, keeps a compact overlay for quick diagnostics, creates session heatmaps, and minimizes to the tray with notifications

## Demo
https://github.com/user-attachments/assets/5055c858-d075-4655-a97d-9c2cf66d1a06





## Features
- real-time iris and gaze tracking using MediaPipe Face Mesh
- distance alerts when the face is too close to the camera
- compact overlay, debug view, and progress tracking for focus sessions
- heatmap generation plus hourly and weekly session summaries
- system tray controls with native notifications and quick keyboard shortcuts

## Requirements
- Windows 10 or later
- Python 3.11 (virtual environment recommended)
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

## Demo 



## Troubleshooting
- If PyInstaller reports missing MediaPipe models, ensure the files exist under `venv\Lib\site-packages\mediapipe\modules` and re-run the command above with the correct paths.
- If the build fails because `LookAlive.exe` is in use, close the running instance (check Task Manager) before rebuilding.
- Reinstall MediaPipe when files disappear from the virtual environment: `pip install --force-reinstall mediapipe`

