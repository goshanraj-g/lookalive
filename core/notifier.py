from plyer import notification
import time

def notify_start_break():
    notification.notify(
        title="20-20-20 Rule",
        message="Look 20 feet away for 20 seconds!",
        timeout=3,
    )


def notify_end_break():
    notification.notify(
        title="Break Over",
        message="You can return to the screen",
        timeout=3,
    )


def notify_too_close():
    """Notify user that they are too close to the screen"""
    notification.notify(
        title="⚠️ Too Close!",
        message="Move back from the screen - you're too close!",
        timeout=3,
    )


def demo_notifications():
    """Demo mode - trigger all notifications in sequence for 30 seconds total"""
    print("Starting notification demo (30 seconds)...")
    
    # Demo 1: Too close warning
    print("Showing 'Too Close' notification...")
    notify_too_close()
    time.sleep(8)
    
    # Demo 2: Break time
    print("Showing 'Break Time' notification...")
    notify_start_break()
    time.sleep(8)
    
    # Demo 3: Break over
    print("Showing 'Break Over' notification...")
    notify_end_break()
    time.sleep(6)
    
    # Demo 4: Low blink rate warning
    print("Showing 'Remember to Blink' notification...")
    notification.notify(
        title="Blink Reminder",
        message="You're not blinking enough - try to blink more often!",
        timeout=3,
    )
    time.sleep(8)
    
    print("Demo complete!")
