"""
System Tray - Run LookAlive minimized to system tray
"""
import threading
import time

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("System tray not available. Install with: pip install pystray Pillow")


class SystemTray:
    def __init__(self, on_show_callback=None, on_quit_callback=None):
        self.on_show = on_show_callback
        self.on_quit = on_quit_callback
        self.icon = None
        self.status = "Running"
        self.is_minimized = False
        
    def create_icon_image(self, color="green"):
        """Create a simple colored circle icon."""
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Color mapping
        colors = {
            "green": (0, 200, 0),
            "orange": (255, 165, 0),
            "red": (255, 0, 0),
            "gray": (128, 128, 128)
        }
        fill_color = colors.get(color, colors["green"])
        
        # Draw eye icon (simple circle with dot)
        draw.ellipse([4, 4, size-4, size-4], fill=fill_color, outline=(255, 255, 255))
        draw.ellipse([size//2-8, size//2-8, size//2+8, size//2+8], fill=(0, 0, 0))
        
        return image
    
    def update_status(self, status, color="green"):
        """Update tray icon status."""
        self.status = status
        if self.icon:
            self.icon.icon = self.create_icon_image(color)
            self.icon.title = f"LookAlive - {status}"
    
    def _on_show(self, icon, item):
        """Show main window callback."""
        self.is_minimized = False
        if self.on_show:
            self.on_show()
    
    def _on_quit(self, icon, item):
        """Quit application callback."""
        if self.on_quit:
            self.on_quit()
        icon.stop()
    
    def start(self):
        """Start the system tray icon."""
        if not TRAY_AVAILABLE:
            return False
        
        menu = pystray.Menu(
            pystray.MenuItem("Show Window", self._on_show, default=True),
            pystray.MenuItem("Quit", self._on_quit)
        )
        
        self.icon = pystray.Icon(
            "LookAlive",
            self.create_icon_image("green"),
            "LookAlive - Running",
            menu
        )
        
        # Run in background thread
        tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        tray_thread.start()
        
        return True
    
    def stop(self):
        """Stop the system tray icon."""
        if self.icon:
            self.icon.stop()
    
    def minimize(self):
        """Set state to minimized."""
        self.is_minimized = True
        self.update_status("Minimized (running)", "gray")
    
    def restore(self):
        """Set state to restored."""
        self.is_minimized = False
        self.update_status("Running", "green")
