"""
Screen Calibration Interface for LookAlive Eye Tracker
Allows users to calibrate screen boundaries for accurate gaze detection
"""

import cv2
import time
from core import IrisGazeTracker
from utils.webcam import get_webcam_capture
import mediapipe as mp

def run_screen_calibration():
    """Run the interactive screen calibration process."""
    
    # Initialize components
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.8,
        min_tracking_confidence=0.8,
    )
    
    cap = get_webcam_capture()
    tracker = IrisGazeTracker()
    
    # Calibration positions in order
    positions = [
        ("left", "Look at the LEFT EDGE of your screen"),
        ("right", "Look at the RIGHT EDGE of your screen"), 
        ("top", "Look at the TOP EDGE of your screen"),
        ("bottom", "Look at the BOTTOM EDGE of your screen"),
        ("center", "Look at the CENTER of your screen")
    ]
    
    current_position = 0
    samples_collected = 0
    samples_needed = 15  # Collect multiple samples for stability
    
    print(f"\n🎯 Calibrating position: {positions[current_position][1]}")
    print(f"Samples needed: {samples_needed}")
    print("Press SPACE to collect sample, ESC to cancel")
    
    # Create window
    cv2.namedWindow("Screen Calibration", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Screen Calibration", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    while current_position < len(positions):
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        
        # Get current position info
        pos_name, instruction = positions[current_position]
        
        # Draw instruction
        cv2.putText(frame, instruction, (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
        
        cv2.putText(frame, f"Position {current_position + 1}/{len(positions)}", (50, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Samples: {samples_collected}/{samples_needed}", (50, 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.putText(frame, "Press SPACE to sample, ESC to cancel", (50, frame.shape[0] - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        
        # Draw calibration target based on position
        h, w = frame.shape[:2]
        if pos_name == "left":
            target_pos = (50, h//2)
        elif pos_name == "right":
            target_pos = (w-50, h//2)
        elif pos_name == "top":
            target_pos = (w//2, 50)
        elif pos_name == "bottom":
            target_pos = (w//2, h-50)
        else:  # center
            target_pos = (w//2, h//2)
            
        # Draw target
        cv2.circle(frame, target_pos, 30, (0, 0, 255), -1)  # Red circle
        cv2.circle(frame, target_pos, 35, (255, 255, 255), 3)  # White border
        
        # Draw iris positions if detected
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            iris_pos = tracker.get_iris_position(landmarks, frame.shape)
            if iris_pos:
                left_x, left_y, right_x, right_y = iris_pos
                cv2.circle(frame, (int(left_x), int(left_y)), 5, (0, 255, 0), -1)
                cv2.circle(frame, (int(right_x), int(right_y)), 5, (0, 255, 0), -1)
        
        cv2.imshow("Screen Calibration", frame)
        
        # Handle input
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Space to collect sample
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                if tracker.collect_calibration_sample(landmarks, frame.shape, pos_name):
                    samples_collected += 1
                    
                    if samples_collected >= samples_needed:
                        # Move to next position
                        current_position += 1
                        samples_collected = 0
                        
                        if current_position < len(positions):
                            print(f"\n🎯 Calibrating position: {positions[current_position][1]}")
                            print(f"Samples needed: {samples_needed}")
                else:
                    print("❌ Failed to collect sample - no face detected")
            else:
                print("❌ No face detected - try again")
                
        elif key == 27:  # ESC to cancel
            print("❌ Calibration cancelled")
            cv2.destroyAllWindows()
            cap.release()
            return False
    
    # Finalize calibration
    cv2.destroyAllWindows()
    success = tracker.finalize_calibration()
    
    if success:
        # Test the calibration
        print("\n✅ Calibration complete! Testing...")
        test_calibration(cap, face_mesh, tracker)
    
    cap.release()
    return success

def test_calibration(cap, face_mesh, tracker, duration=10):
    """Test the calibration for a few seconds."""
    print(f"Testing calibration for {duration} seconds...")
    print("Look around your screen to test accuracy")
    
    cv2.namedWindow("Calibration Test", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Calibration Test", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    start_time = time.time()
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            break
            
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            gaze = tracker.calculate_gaze_direction(landmarks, frame.shape)
            
            # Display gaze direction
            color = (0, 255, 0) if gaze == "center" else (0, 255, 255) if gaze != "away" else (0, 0, 255)
            cv2.putText(frame, f"Gaze: {gaze.upper()}", (50, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 2, color, 4)
            
            # Draw iris positions
            iris_pos = tracker.get_iris_position(landmarks, frame.shape)
            if iris_pos:
                left_x, left_y, right_x, right_y = iris_pos
                cv2.circle(frame, (int(left_x), int(left_y)), 5, (0, 255, 0), -1)
                cv2.circle(frame, (int(right_x), int(right_y)), 5, (0, 255, 0), -1)
        else:
            cv2.putText(frame, "No Face", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
        
        remaining = int(duration - (time.time() - start_time))
        cv2.putText(frame, f"Test ends in: {remaining}s", (50, 200),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        cv2.imshow("Calibration Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()
    print("✅ Calibration test complete!")

if __name__ == "__main__":
    print("🎯 LookAlive Screen Calibration")
    print("This will calibrate your screen boundaries for accurate gaze detection")
    
    input("Press Enter to start calibration...")
    
    if run_screen_calibration():
        print("🎉 Screen calibration successful!")
        print("Your main eye tracker will now accurately detect when you're looking at your screen")
    else:
        print("❌ Calibration failed or cancelled")