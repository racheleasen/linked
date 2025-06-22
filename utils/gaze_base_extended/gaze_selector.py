import time
import math
import cv2
from ui.overlay import draw_selector_overlay

class GazeSelector:
    def __init__(self, trigger_time=2, center=(0.5, 0.5), inner_radius=0.04, outer_radius=0.25):
        self.trigger_time = trigger_time
        self.center = center
        self.current_selection = None
        self.dwell_progress = 0.0
        self.last_frame_time = time.time()
        self.dwell_enabled = True
        self.last_radius = None
        self.last_theta = None

        self.button_actions = {
            "upper_left": {
                "label": "Deactivate", "func": "toggle", "corner": (0, 0), "allow_dwell": True
            },
            "upper_right": {
                "label": "Select", "func": "select_card", "corner": (1, 0), "allow_dwell": True
            },
        }

    def update_buttons(self, emergency_mode=False, deck_manager=None):
        if emergency_mode and deck_manager and deck_manager.is_active():
            self.button_actions["upper_left"]["label"] = "Deactivate"
            self.button_actions["upper_left"]["allow_dwell"] = True
            self.button_actions["upper_right"]["label"] = "Emergency"
            self.button_actions["upper_right"]["allow_dwell"] = False
        elif deck_manager and deck_manager.is_active():
            self.button_actions["upper_left"]["label"] = "Deactivate"
            self.button_actions["upper_left"]["allow_dwell"] = True
            self.button_actions["upper_right"]["label"] = "Select"
            self.button_actions["upper_right"]["allow_dwell"] = True
        else:
            self.button_actions["upper_left"]["label"] = "Blink to Activate"
            self.button_actions["upper_left"]["allow_dwell"] = False
            self.button_actions["upper_right"]["label"] = "Blink to Activate"
            self.button_actions["upper_right"]["allow_dwell"] = False

    def process(self, frame, gaze, deck_manager=None, emergency_mode=False):
        self.update_buttons(emergency_mode=emergency_mode, deck_manager=deck_manager)
        height, width = frame.shape[:2]
        hor = gaze.horizontal_ratio()
        ver = gaze.vertical_ratio()

        r = theta = None
        new_selection = None

        now = time.time()
        dt = now - self.last_frame_time
        self.last_frame_time = now

        if not self.dwell_enabled:
            return draw_selector_overlay(frame, self), None

        if hor is not None and ver is not None:
            dx = hor - self.center[0]
            dy = ver - self.center[1]
            r = math.hypot(dx, dy)
            theta = (math.degrees(math.atan2(dy, dx)) + 360) % 360

            self.last_radius = r
            self.last_theta = theta

            if r < 0.06:
                dx = dy = 0  # suppress small jitters near center

            if 210 <= theta < 250:
                new_selection = "upper_left"
            elif 280 <= theta < 320:
                new_selection = "upper_right"

        # Dwell logic
        if new_selection:
            if self.button_actions.get(new_selection, {}).get("allow_dwell", True):
                if new_selection == self.current_selection:
                    self.dwell_progress += dt
                else:
                    self.current_selection = new_selection
                    self.dwell_progress = 0.0
        else:
            self.dwell_progress -= dt * 0.75

        self.dwell_progress = max(0.0, min(self.dwell_progress, self.trigger_time))

        # Trigger event
        event = None
        if self.dwell_progress >= self.trigger_time and self.current_selection:
            event = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "action": self.current_selection,
                "gaze_point": {"x": round(hor, 6), "y": round(ver, 6)},
                "radius": round(r, 4) if r is not None else None,
                "theta": round(theta, 4) if theta is not None else None
            }
            self.dwell_progress = 0.0
            self.current_selection = None

        return draw_selector_overlay(frame, self), event
