"""
UI Overlay - Clean, modern overlay for LookAlive
"""
import cv2
import numpy as np
import time


class UIOverlay:
    def __init__(self):
        self.compact_mode = False
        self.compact_height = 80
        
    def draw_rounded_rect(self, frame, x, y, w, h, color, alpha=0.7, radius=10):
        """Draw a semi-transparent rounded rectangle."""
        overlay = frame.copy()
        
        # Draw rounded rectangle
        cv2.rectangle(overlay, (x + radius, y), (x + w - radius, y + h), color, -1)
        cv2.rectangle(overlay, (x, y + radius), (x + w, y + h - radius), color, -1)
        cv2.circle(overlay, (x + radius, y + radius), radius, color, -1)
        cv2.circle(overlay, (x + w - radius, y + radius), radius, color, -1)
        cv2.circle(overlay, (x + radius, y + h - radius), radius, color, -1)
        cv2.circle(overlay, (x + w - radius, y + h - radius), radius, color, -1)
        
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        return frame
    
    def draw_progress_bar(self, frame, x, y, width, height, progress, color_bg, color_fill):
        """Draw a progress bar with rounded ends."""
        # Background
        cv2.rectangle(frame, (x, y), (x + width, y + height), color_bg, -1)
        
        # Fill
        fill_width = int(width * progress)
        if fill_width > 0:
            cv2.rectangle(frame, (x, y), (x + fill_width, y + height), color_fill, -1)
        
        # Border
        cv2.rectangle(frame, (x, y), (x + width, y + height), (100, 100, 100), 1)
        
        return frame
    
    def draw_status_bar(self, frame, gaze, break_in_progress, time_to_break, break_remaining, 
                        blink_rate, too_close, screen_time_mins):
        """Draw the main status bar overlay."""
        h, w = frame.shape[:2]
        
        if self.compact_mode:
            return self.draw_compact_overlay(frame, gaze, break_in_progress, time_to_break, 
                                             break_remaining, too_close)
        
        # Main status panel (top)
        panel_height = 120
        self.draw_rounded_rect(frame, 10, 10, w - 20, panel_height, (40, 40, 40), 0.8)
        
        # Status icon and text
        if break_in_progress:
            status = "BREAK TIME"
            status_color = (0, 165, 255)  # Orange
            icon = "☕"
        elif too_close:
            status = "TOO CLOSE!"
            status_color = (0, 0, 255)  # Red
            icon = "⚠️"
        elif gaze == "center":
            status = "Looking at Screen"
            status_color = (0, 255, 0)  # Green
            icon = "👁️"
        else:
            status = f"Looking {gaze.title()}"
            status_color = (0, 255, 255)  # Yellow
            icon = "👀"
        
        # Main status text
        cv2.putText(frame, f"{icon} {status}", (30, 55), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, status_color, 2)
        
        # Progress bar to next break (or break countdown)
        bar_y = 75
        bar_width = w - 60
        
        if break_in_progress:
            # Break countdown bar (fills up as break progresses)
            progress = 1 - (break_remaining / 20) if break_remaining else 1
            self.draw_progress_bar(frame, 30, bar_y, bar_width, 20, progress, 
                                   (60, 60, 60), (0, 200, 255))
            cv2.putText(frame, f"Break: {int(break_remaining)}s remaining", (30, bar_y + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        else:
            # Time until next break
            progress = 1 - (time_to_break / (20 * 60)) if time_to_break else 0
            bar_color = (0, 255, 0) if progress < 0.8 else (0, 165, 255)
            self.draw_progress_bar(frame, 30, bar_y, bar_width, 20, progress,
                                   (60, 60, 60), bar_color)
            mins_left = int(time_to_break // 60)
            secs_left = int(time_to_break % 60)
            cv2.putText(frame, f"Next break in: {mins_left}:{secs_left:02d}", (30, bar_y + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        # Stats panel (bottom right)
        stats_w, stats_h = 200, 80
        stats_x = w - stats_w - 10
        stats_y = h - stats_h - 10
        self.draw_rounded_rect(frame, stats_x, stats_y, stats_w, stats_h, (40, 40, 40), 0.8)
        
        # Blink rate
        blink_color = (0, 255, 0) if 15 <= blink_rate <= 20 else (0, 165, 255)
        cv2.putText(frame, f"Blinks: {blink_rate:.0f}/min", (stats_x + 15, stats_y + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, blink_color, 1)
        
        # Screen time
        cv2.putText(frame, f"Screen: {screen_time_mins}min", (stats_x + 15, stats_y + 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Controls hint (bottom left)
        cv2.putText(frame, "Q-Quit | C-Compact | D-Debug", (15, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        
        return frame
    
    def draw_compact_overlay(self, frame, gaze, break_in_progress, time_to_break, 
                             break_remaining, too_close):
        """Draw minimal compact overlay."""
        h, w = frame.shape[:2]
        
        # Single slim bar at top
        bar_height = 50
        self.draw_rounded_rect(frame, 5, 5, w - 10, bar_height, (30, 30, 30), 0.85)
        
        # Status indicator (colored dot)
        if break_in_progress:
            color = (0, 165, 255)
            text = f"BREAK {int(break_remaining)}s"
        elif too_close:
            color = (0, 0, 255)
            text = "TOO CLOSE"
        elif gaze == "center":
            color = (0, 255, 0)
            text = "OK"
        else:
            color = (0, 255, 255)
            text = gaze.upper()
        
        # Status dot
        cv2.circle(frame, (25, 30), 10, color, -1)
        
        # Status text
        cv2.putText(frame, text, (45, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Mini progress bar
        bar_x = 150
        bar_width = w - 180
        if break_in_progress:
            progress = 1 - (break_remaining / 20)
        else:
            progress = 1 - (time_to_break / (20 * 60)) if time_to_break else 0
        
        self.draw_progress_bar(frame, bar_x, 20, bar_width, 15, progress,
                               (60, 60, 60), color)
        
        # Compact hint
        cv2.putText(frame, "C-Expand", (w - 70, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)
        
        return frame
    
    def draw_warning(self, frame, message, warning_type="warning"):
        """Draw a warning banner."""
        h, w = frame.shape[:2]
        
        if warning_type == "warning":
            color = (0, 165, 255)  # Orange
        elif warning_type == "danger":
            color = (0, 0, 255)  # Red
        else:
            color = (0, 255, 255)  # Yellow
        
        # Warning banner
        banner_y = h // 2 - 30
        self.draw_rounded_rect(frame, 20, banner_y, w - 40, 60, color, 0.9)
        
        # Warning text
        text_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        text_x = (w - text_size[0]) // 2
        cv2.putText(frame, message, (text_x, banner_y + 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        return frame
    
    def toggle_compact(self):
        """Toggle compact mode."""
        self.compact_mode = not self.compact_mode
        return self.compact_mode
