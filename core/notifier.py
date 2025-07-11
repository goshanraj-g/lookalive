from plyer import notification

def notify_start_break():
    notification.notify(
        title="20-20-20 Rule",
        message="Look 20 feet away for 20 seconds!",
        timeout=5,
    )


def notify_end_break():
    notification.notify(
        title="Break Over",
        message="You can return to the screen",
        timeout=5,
    )
