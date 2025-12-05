"""
Session Tracker - Track usage patterns and generate heatmaps
"""
import json
import os
import time
from datetime import datetime, timedelta
from collections import defaultdict


class SessionTracker:
    def __init__(self, data_file="session_data.json"):
        self.data_file = data_file
        self.session_start = time.time()
        self.hourly_data = defaultdict(float)  # hour is key, value is minutes at screen
        self.current_hour = datetime.now().hour
        self.last_update = time.time()
        
        # load any previous data if it exists
        self.all_data = self.load_data()
        
    def load_data(self) -> dict:
        # load session data from file if it exists
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"daily": {}, "weekly_summary": {}}
    
    def save_data(self):
        # save session data to file
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.all_data, f, indent=2)
        except Exception as e:
            print(f"Error saving session data: {e}")
    
    def update(self, is_looking_at_screen: bool):
        # update tracking with current state
        now = time.time()
        current_hour = datetime.now().hour
        
        # if hour changed, save previous hour data
        if current_hour != self.current_hour:
            self._save_hourly_data()
            self.current_hour = current_hour
        
        # add minutes to current hour if user is looking at screen
        if is_looking_at_screen:
            elapsed = (now - self.last_update) / 60  # minutes
            self.hourly_data[current_hour] += elapsed
        
        self.last_update = now
    
    def _save_hourly_data(self):
        # save hourly data to the daily record
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today not in self.all_data["daily"]:
            self.all_data["daily"][today] = {}
        
        for hour, minutes in self.hourly_data.items():
            hour_key = str(hour)
            if hour_key in self.all_data["daily"][today]:
                self.all_data["daily"][today][hour_key] += minutes
            else:
                self.all_data["daily"][today][hour_key] = minutes
        
        self.hourly_data.clear()
        self.save_data()
    
    def get_today_heatmap(self) -> dict:
        # get hourly breakdown for today
        today = datetime.now().strftime("%Y-%m-%d")
        saved_data = self.all_data["daily"].get(today, {})
        
        # merge with current session data
        result = {str(h): 0 for h in range(24)}
        
        for hour, minutes in saved_data.items():
            result[hour] = minutes
        
        for hour, minutes in self.hourly_data.items():
            result[str(hour)] = result.get(str(hour), 0) + minutes
        
        return result
    
    def get_weekly_summary(self) -> dict:
        # get daily totals for the past 7 days
        result = {}
        today = datetime.now()
        
        for i in range(7):
            day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            day_data = self.all_data["daily"].get(day, {})
            total_minutes = sum(day_data.values())
            result[day] = total_minutes
        
        return result
    
    def end_session(self):
        # call this when the app closes
        self._save_hourly_data()
        
        # show session duration
        session_duration = (time.time() - self.session_start) / 60
        print(f"\nSession Duration: {session_duration:.1f} minutes")
        
        # show today's summary
        today_data = self.get_today_heatmap()
        total_today = sum(today_data.values())
        print(f"Total screen time today: {total_today:.0f} minutes")
        
        # find peak hours
        peak_hours = sorted(today_data.items(), key=lambda x: x[1], reverse=True)[:3]
        if peak_hours and peak_hours[0][1] > 0:
            print("Peak usage hours:")
            for hour, mins in peak_hours:
                if mins > 0:
                    print(f"   {int(hour):02d}:00 - {mins:.0f} min")
    
    def generate_heatmap_ascii(self) -> str:
        # make ascii heatmap for terminal display
        today_data = self.get_today_heatmap()
        
        lines = ["\nToday's Screen Time Heatmap:", "=" * 50]
        
        # find max for scaling
        max_mins = max(today_data.values()) if today_data.values() else 1
        
        for hour in range(24):
            mins = today_data.get(str(hour), 0)
            bar_len = int((mins / max(max_mins, 1)) * 30) if max_mins > 0 else 0
            bar = "█" * bar_len
            lines.append(f"{hour:02d}:00 | {bar} {mins:.0f}m")
        
        return "\n".join(lines)
