import cv2
import numpy as np
import mediapipe as mp
import time
from typing import Tuple, Optional


class IrisGazeTracker:
    def __init__(self):
        
        # init mediapipe iris
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_iris = mp.solutions.face_mesh
        
        # face mesh w/ iris landmarks
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        
        # iris landmark indices
        self.LEFT_IRIS_CENTER = 468
        self.RIGHT_IRIS_CENTER = 473
        
        # eye corner landmarks for better gaze calculation
        self.LEFT_EYE_CORNERS = [33, 133]  # inner, outer corner
        self.RIGHT_EYE_CORNERS = [362, 263]
        
        # blink detection landmarks
        self.LEFT_EYE_TOP_BOTTOM = [159, 145]  # top, bottom
        self.RIGHT_EYE_TOP_BOTTOM = [386, 374]
        
        # tracking variables
        self.blink_counter = 0
        self.blink_start_time = time.time()
        self.last_blink_time = 0
        
        # callibration vars (DISABLED - using improved relative method instead)
        self.is_calibrated = False  # Always False - calibration disabled
        self.screen_bounds = None  
        self.calibration_points = []  
        self.calibration_file = "screen_calibration.json"
        
        # Don't load calibration - improved method doesn't need it
        # self.load_calibration()
        
    def get_iris_position(self, landmarks, frame_shape) -> Optional[Tuple[float, float, float, float]]:
        """
        Get precise iris positions for both eyes.
        Returns: (left_iris_x, left_iris_y, right_iris_x, right_iris_y) or None
        """
        if not landmarks:
            return None
            
        h, w = frame_shape[:2]
        
        # Get iris centers
        left_iris = landmarks[self.LEFT_IRIS_CENTER]
        right_iris = landmarks[self.RIGHT_IRIS_CENTER]
        
        left_x = left_iris.x * w
        left_y = left_iris.y * h
        right_x = right_iris.x * w  
        right_y = right_iris.y * h
        
        return (left_x, left_y, right_x, right_y)
    
    def calculate_gaze_direction(self, landmarks, frame_shape) -> str:
        """
        Improved gaze direction using multiple methods for better accuracy.
        """
        iris_pos = self.get_iris_position(landmarks, frame_shape)
        if not iris_pos:
            return "away"
            
        left_iris_x, left_iris_y, right_iris_x, right_iris_y = iris_pos
        h, w = frame_shape[:2]
        
        # 🎯 METHOD 1: Eye-relative positioning (most reliable)
        left_inner = landmarks[self.LEFT_EYE_CORNERS[0]]
        left_outer = landmarks[self.LEFT_EYE_CORNERS[1]]
        right_inner = landmarks[self.RIGHT_EYE_CORNERS[0]]
        right_outer = landmarks[self.RIGHT_EYE_CORNERS[1]]
        
        # Calculate relative iris position within each eye socket
        left_eye_width = abs((left_outer.x - left_inner.x) * w)
        right_eye_width = abs((right_outer.x - right_inner.x) * w)
        
        if left_eye_width > 0 and right_eye_width > 0:
            # Relative position (0 = inner corner, 1 = outer corner)
            left_relative = (left_iris_x - left_inner.x * w) / left_eye_width
            right_relative = (right_iris_x - right_inner.x * w) / right_eye_width
            
            # Average both eyes for stability
            avg_relative = (left_relative + right_relative) / 2
            
            # 🎯 METHOD 2: Absolute iris position (secondary check)
            avg_iris_x = (left_iris_x + right_iris_x) / 2
            frame_center = w / 2
            distance_from_center = abs(avg_iris_x - frame_center) / (w / 2)
            
            # 🎯 METHOD 3: Combined decision with dynamic thresholds
            # Adjust thresholds based on how far iris is from eye center
            base_threshold = 0.25  # More sensitive than before
            
            # If looking very far to sides, be more confident
            if distance_from_center > 0.3:
                threshold = base_threshold - 0.05  # Easier to trigger left/right
            else:
                threshold = base_threshold + 0.05  # Prefer center for small movements
            
            # Final decision with improved logic
            if avg_relative < (0.5 - threshold):
                return "left"
            elif avg_relative > (0.5 + threshold):
                return "right"
            else:
                return "center"
        
        return "center"  # Default safe fallback
    
    def detect_blink(self, landmarks, frame_shape) -> bool:
        """
        Detect if user is blinking using eye aspect ratio.
        """
        if not landmarks:
            return False
            
        h, w = frame_shape[:2]
        
        # Calculate eye aspect ratio for both eyes
        left_top = landmarks[self.LEFT_EYE_TOP_BOTTOM[0]]
        left_bottom = landmarks[self.LEFT_EYE_TOP_BOTTOM[1]]
        right_top = landmarks[self.RIGHT_EYE_TOP_BOTTOM[0]]
        right_bottom = landmarks[self.RIGHT_EYE_TOP_BOTTOM[1]]
        
        # Vertical distances
        left_height = abs((left_top.y - left_bottom.y) * h)
        right_height = abs((right_top.y - right_bottom.y) * h)
        
        # Average eye height
        avg_height = (left_height + right_height) / 2
        
        # Blink threshold (adjust based on testing)
        blink_threshold = 8.0  # pixels
        
        is_blinking = avg_height < blink_threshold
        
        if is_blinking and time.time() - self.last_blink_time > 0.3:
            self.blink_counter += 1
            self.last_blink_time = time.time()
            
        return is_blinking
    
    def get_blink_rate(self) -> float:
        """
        Calculate blinks per minute.
        Normal rate is 15-20 blinks/minute.
        """
        elapsed_minutes = (time.time() - self.blink_start_time) / 60.0
        if elapsed_minutes > 0:
            return self.blink_counter / elapsed_minutes
        return 0
    
    def get_iris_diameter(self, landmarks, frame_shape) -> Optional[float]:
        """
        Estimate iris diameter for pupil dilation detection.
        Can indicate eye strain or fatigue.
        """
        iris_pos = self.get_iris_position(landmarks, frame_shape)
        if not iris_pos:
            return None
            
        # This is a simplified estimation
        # In reality, you'd need additional iris boundary landmarks
        h, w = frame_shape[:2]
        
        # Rough estimation based on eye size
        left_inner = landmarks[self.LEFT_EYE_CORNERS[0]]
        left_outer = landmarks[self.LEFT_EYE_CORNERS[1]]
        eye_width = abs((left_outer.x - left_inner.x) * w)
        
        # Iris is typically ~25% of eye width
        estimated_iris_diameter = eye_width * 0.25
        return estimated_iris_diameter
    
    def get_gaze_analysis(self, landmarks, frame_shape) -> dict:
        """
        Comprehensive gaze analysis including all metrics.
        """
        gaze_direction = self.calculate_gaze_direction(landmarks, frame_shape)
        is_blinking = self.detect_blink(landmarks, frame_shape)
        blink_rate = self.get_blink_rate()
        iris_diameter = self.get_iris_diameter(landmarks, frame_shape)
        iris_pos = self.get_iris_position(landmarks, frame_shape)
        
        return {
            'gaze_direction': gaze_direction,
            'is_blinking': is_blinking,
            'blink_rate': blink_rate,
            'iris_diameter': iris_diameter,
            'iris_positions': iris_pos,
            'timestamp': time.time()
        }
    
    def draw_debug_overlay(self, frame, landmarks, analysis: dict):
        """
        Draw debug information on the frame.
        """
        if not landmarks:
            return frame
            
        h, w = frame.shape[:2]
        
        # Draw iris centers
        if analysis['iris_positions']:
            left_x, left_y, right_x, right_y = analysis['iris_positions']
            cv2.circle(frame, (int(left_x), int(left_y)), 3, (0, 255, 0), -1)
            cv2.circle(frame, (int(right_x), int(right_y)), 3, (0, 255, 0), -1)
        
        # Draw gaze direction
        gaze = analysis['gaze_direction']
        color = (0, 255, 0) if gaze == "center" else (0, 255, 255)
        cv2.putText(frame, f"Gaze: {gaze}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Draw blink rate
        blink_rate = analysis['blink_rate']
        blink_color = (0, 255, 0) if 15 <= blink_rate <= 20 else (0, 165, 255)
        cv2.putText(frame, f"Blinks/min: {blink_rate:.1f}", (30, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, blink_color, 2)
        
        # Blink indicator
        if analysis['is_blinking']:
            cv2.putText(frame, "BLINK", (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        return frame
    
    def reset_blink_counter(self):
        """Reset blink tracking (useful for new sessions)."""
        self.blink_counter = 0
        self.blink_start_time = time.time()
    
    # 🎯 SCREEN CALIBRATION METHODS
    def start_screen_calibration(self):
        """Start the screen calibration process."""
        print("\n🎯 SCREEN CALIBRATION")
        print("=" * 40)
        print("We'll calibrate your screen boundaries so the app knows")
        print("when you're looking at your monitor vs. looking away.")
        print("\nYou'll look at 5 positions:")
        print("1. Left edge of screen")
        print("2. Right edge of screen") 
        print("3. Top edge of screen")
        print("4. Bottom edge of screen")
        print("5. Center of screen")
        
        self.calibration_points = []
        return True
    
    def collect_calibration_sample(self, landmarks, frame_shape, position_name: str):
        """Collect iris position for a specific screen position."""
        iris_pos = self.get_iris_position(landmarks, frame_shape)
        if iris_pos:
            left_x, left_y, right_x, right_y = iris_pos
            # Average both eyes for more stable calibration
            avg_x = (left_x + right_x) / 2
            avg_y = (left_y + right_y) / 2
            
            sample = {
                'position': position_name,
                'iris_x': avg_x,
                'iris_y': avg_y,
                'timestamp': time.time()
            }
            self.calibration_points.append(sample)
            print(f"✅ Collected sample for {position_name}: iris at ({avg_x:.1f}, {avg_y:.1f})")
            return True
        return False
    
    def finalize_calibration(self):
        """Process calibration data and create screen boundaries."""
        if len(self.calibration_points) < 5:
            print("❌ Need at least 5 calibration points")
            return False
        
        # Extract positions
        positions = {point['position']: (point['iris_x'], point['iris_y']) 
                    for point in self.calibration_points}
        
        if not all(pos in positions for pos in ['left', 'right', 'top', 'bottom', 'center']):
            print("❌ Missing required calibration positions")
            return False
        
        # Calculate screen boundaries from calibration points
        left_x = positions['left'][0]
        right_x = positions['right'][0]
        top_y = positions['top'][1]
        bottom_y = positions['bottom'][1]
        center_x, center_y = positions['center']
        
        # Add margins for better detection (10% of range)
        x_margin = (right_x - left_x) * 0.1
        y_margin = (bottom_y - top_y) * 0.1
        
        self.screen_bounds = {
            'left': left_x - x_margin,
            'right': right_x + x_margin,
            'top': top_y - y_margin,
            'bottom': bottom_y + y_margin,
            'center_x': center_x,
            'center_y': center_y
        }
        
        self.is_calibrated = True
        self.save_calibration()
        
        print("🎉 Screen calibration completed!")
        print(f"Screen bounds: X({self.screen_bounds['left']:.1f} to {self.screen_bounds['right']:.1f})")
        print(f"              Y({self.screen_bounds['top']:.1f} to {self.screen_bounds['bottom']:.1f})")
        
        return True
    
    def save_calibration(self):
        """Save calibration to file."""
        import json
        try:
            data = {
                'screen_bounds': self.screen_bounds,
                'calibration_points': self.calibration_points,
                'is_calibrated': self.is_calibrated,
                'timestamp': time.time()
            }
            with open(self.calibration_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Calibration saved to {self.calibration_file}")
        except Exception as e:
            print(f"❌ Error saving calibration: {e}")
    
    def load_calibration(self):
        """Load calibration from file."""
        import json
        try:
            with open(self.calibration_file, 'r') as f:
                data = json.load(f)
            
            self.screen_bounds = data.get('screen_bounds')
            self.calibration_points = data.get('calibration_points', [])
            self.is_calibrated = data.get('is_calibrated', False)
            
            if self.is_calibrated:
                print(f"📄 Loaded screen calibration from {self.calibration_file}")
                print(f"Screen bounds: X({self.screen_bounds['left']:.1f} to {self.screen_bounds['right']:.1f})")
        except FileNotFoundError:
            print("No existing screen calibration found")
        except Exception as e:
            print(f"Error loading calibration: {e}")
            self.is_calibrated = False


def get_gaze_direction(landmarks, frame_shape):
    """
    Compatibility function for existing code.
    """
    # Create a temporary tracker for compatibility
    tracker = IrisGazeTracker()
    return tracker.calculate_gaze_direction(landmarks, frame_shape)