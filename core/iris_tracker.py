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
        
        # distance detection
        self.baseline_face_width = None  # will be set after a few frames
        self.face_width_samples = []
        self.TOO_CLOSE_THRESHOLD = 1.3  # 30% larger than baseline means that its  too close
        
    def get_iris_position(self, landmarks, frame_shape) -> Optional[Tuple[float, float, float, float]]:
        """
        get precise iris positions for both eyes
        returns: (left_iris_x, left_iris_y, right_iris_x, right_iris_y) or None
        ####### COOL, CHECK IF THERES MORE LANDMARKS
        """
        if not landmarks:
            return None
            
        h, w = frame_shape[:2]
        
        # get iris centers
        left_iris = landmarks[self.LEFT_IRIS_CENTER]
        right_iris = landmarks[self.RIGHT_IRIS_CENTER]
        
        left_x = left_iris.x * w
        left_y = left_iris.y * h
        right_x = right_iris.x * w  
        right_y = right_iris.y * h
        
        return (left_x, left_y, right_x, right_y)
    
    def calculate_gaze_direction(self, landmarks, frame_shape) -> str:
        """
        cakc  gaze direction using iris tracking
        """
        iris_pos = self.get_iris_position(landmarks, frame_shape)
        if not iris_pos:
            return "away"
            
        left_iris_x, left_iris_y, right_iris_x, right_iris_y = iris_pos
        h, w = frame_shape[:2]
        
        # get eye corner landmarks for reference
        left_inner = landmarks[self.LEFT_EYE_CORNERS[0]]
        left_outer = landmarks[self.LEFT_EYE_CORNERS[1]]
        right_inner = landmarks[self.RIGHT_EYE_CORNERS[0]]
        right_outer = landmarks[self.RIGHT_EYE_CORNERS[1]]
        
        # calc eye widths in pixels
        left_eye_width = abs((left_outer.x - left_inner.x) * w)
        right_eye_width = abs((right_outer.x - right_inner.x) * w)
        
        if left_eye_width > 0 and right_eye_width > 0:
            # calc relative iris position within each eye (0 = inner, 1 = outer)
            left_relative = (left_iris_x - left_inner.x * w) / left_eye_width
            right_relative = (right_iris_x - right_inner.x * w) / right_eye_width
            
            # avg both eyes for final position
            avg_relative = (left_relative + right_relative) / 2
            
            # threshold-based detection
            threshold = 0.15  # sens threshold
            
            if avg_relative < (0.5 - threshold):
                return "left"
            elif avg_relative > (0.5 + threshold):
                return "right"
            else:
                return "center"
        
        return "center"  # default safe fallback
    
    def detect_blink(self, landmarks, frame_shape) -> bool:
        """
        detect if user is blinking using eye aspect ratio
        """
        if not landmarks:
            return False
            
        h, w = frame_shape[:2]
        
        # calculate eye aspect ratio for both eyes
        left_top = landmarks[self.LEFT_EYE_TOP_BOTTOM[0]]
        left_bottom = landmarks[self.LEFT_EYE_TOP_BOTTOM[1]]
        right_top = landmarks[self.RIGHT_EYE_TOP_BOTTOM[0]]
        right_bottom = landmarks[self.RIGHT_EYE_TOP_BOTTOM[1]]
        
        # vertical distances
        left_height = abs((left_top.y - left_bottom.y) * h)
        right_height = abs((right_top.y - right_bottom.y) * h)
        
        # average eye height
        avg_height = (left_height + right_height) / 2
        
        # blink threshold (adjust based on testing)
        blink_threshold = 8.0  # pixels
        
        is_blinking = avg_height < blink_threshold
        
        if is_blinking and time.time() - self.last_blink_time > 0.3:
            self.blink_counter += 1
            self.last_blink_time = time.time()
            
        return is_blinking
    
    def get_blink_rate(self) -> float:
        """
        calculate blinks per minute
        normal rate is 15-20 blinks/minute
        """
        elapsed_minutes = (time.time() - self.blink_start_time) / 60.0
        if elapsed_minutes > 0:
            return self.blink_counter / elapsed_minutes
        return 0
    
    def get_iris_diameter(self, landmarks, frame_shape) -> Optional[float]:
        """
        estimate iris diameter for pupil dilation detection
        can indicate eye strain or fatigue
        """
        iris_pos = self.get_iris_position(landmarks, frame_shape)
        if not iris_pos:
            return None
            
        # This is a simplified estimation
        # In reality, you'd need additional iris boundary landmarks
        h, w = frame_shape[:2]
        
        # rough estimation based on eye size
        left_inner = landmarks[self.LEFT_EYE_CORNERS[0]]
        left_outer = landmarks[self.LEFT_EYE_CORNERS[1]]
        eye_width = abs((left_outer.x - left_inner.x) * w)
        
        # iris is typically ~25% of eye width
        estimated_iris_diameter = eye_width * 0.25
        return estimated_iris_diameter
    
    def get_gaze_analysis(self, landmarks, frame_shape) -> dict:
        """
        Comprehensive gaze analysis including all metrics
        """
        gaze_direction = self.calculate_gaze_direction(landmarks, frame_shape)
        is_blinking = self.detect_blink(landmarks, frame_shape)
        blink_rate = self.get_blink_rate()
        iris_diameter = self.get_iris_diameter(landmarks, frame_shape)
        iris_pos = self.get_iris_position(landmarks, frame_shape)
        too_close = self.is_too_close(landmarks, frame_shape)
        
        return {
            'gaze_direction': gaze_direction,
            'is_blinking': is_blinking,
            'blink_rate': blink_rate,
            'iris_diameter': iris_diameter,
            'iris_positions': iris_pos,
            'too_close': too_close,
            'timestamp': time.time()
        }
    
    def is_too_close(self, landmarks, frame_shape) -> bool:
        """
        Detect if user is too close to screen based on face size
        Uses face width relative to a calibrated baseline
        """
        if not landmarks:
            return False
        
        h, w = frame_shape[:2]
        
        # Get face width using outer eye corners (more stable than face edges)
        left_outer = landmarks[33]   # Left eye outer corner
        right_outer = landmarks[263] # Right eye outer corner
        
        face_width = abs(right_outer.x - left_outer.x) * w
        
        # Calibrate baseline from first few frames
        if len(self.face_width_samples) < 30:  # ~1 second of samples
            self.face_width_samples.append(face_width)
            if len(self.face_width_samples) == 30:
                # Use median to avoid outliers
                self.baseline_face_width = sorted(self.face_width_samples)[15]
            return False
        
        if self.baseline_face_width is None:
            return False
        
        # Check if face is significantly larger than baseline
        ratio = face_width / self.baseline_face_width
        return ratio > self.TOO_CLOSE_THRESHOLD
    
    def reset_distance_calibration(self):
        """Reset the distance baseline (if user changes position)"""
        self.baseline_face_width = None
        self.face_width_samples = []
    
    def draw_debug_overlay(self, frame, landmarks, analysis: dict):

        if not landmarks:
            return frame
            
        h, w = frame.shape[:2]
        
        # Draw iris centers
        if analysis['iris_positions']:
            left_x, left_y, right_x, right_y = analysis['iris_positions']
            cv2.circle(frame, (int(left_x), int(left_y)), 3, (0, 255, 0), -1)
            cv2.circle(frame, (int(right_x), int(right_y)), 3, (0, 255, 0), -1)
        
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
        """reset blink tracking"""
        self.blink_counter = 0
        self.blink_start_time = time.time()


def get_gaze_direction(landmarks, frame_shape):

    tracker = IrisGazeTracker()
    return tracker.calculate_gaze_direction(landmarks, frame_shape)