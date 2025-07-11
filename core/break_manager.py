import time


class BreakManager:
    def __init__(self, screen_limit, break_duration):
        self.screen_limit = screen_limit
        self.break_duration = break_duration
        self.start_screen_watch_time = None
        self.break_in_progress = False
        self.break_start_time = None

    def update_state(self, gaze):
        now = time.time()
        notify = None

        if gaze == "center" and not self.break_in_progress:
            if self.start_screen_watch_time is None:
                self.start_screen_watch_time = now
            elif now - self.start_screen_watch_time >= self.screen_limit:
                self.break_in_progress = True
                self.break_start_time = now
                notify = "start_break"
        else:
            self.start_screen_watch_time = None

        if (
            self.break_in_progress
            and now - self.break_start_time >= self.break_duration
        ):
            self.break_in_progress = False
            self.start_screen_watch_time = None
            notify = "end_break"

        return notify, now

    def reset(self):
        self.start_screen_watch_time = None
