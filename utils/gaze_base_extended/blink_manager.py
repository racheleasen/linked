import time

class BlinkManager:
    def __init__(self, cooldown=0.3):
        self.cooldown = cooldown
        self.timestamps = []
        self.last_blink = 0

    def register_blink(self, now):
        if now - self.last_blink > self.cooldown:
            self.last_blink = now
            self.timestamps.append(now)
            # Keep only the last 2.5 seconds of blinks
            self.timestamps = [t for t in self.timestamps if now - t <= 2.5]
            
            if len(self.timestamps) >= 3:
                self.timestamps.clear()
                return "triple"
            return "single"
        return None

        def on_blink(self, now=None):
            """Advance deck if active and cooldown passed."""
            if not self.active:
                return None
            now = now or time.time()
            if now - self.last_blink > self.cooldown:
                self.last_blink = now
                card = self.next()
                return card
            return None