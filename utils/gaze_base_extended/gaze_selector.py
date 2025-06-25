import time
import math
import cv2
import numpy as np
from ui.overlay import draw_selector_overlay

class GazeSelector:
    def __init__(self, trigger_time=2, center=(0.5, 0.5), inner_radius=0.04, outer_radius=0.25):
        self.trigger_time = trigger_time
        self.center = center
        self.current_selection = None
        self.dwell_progress = 0.0
        self.last_frame_time = time.time()
        self.dwell_enabled = True
        self._radius_buffer = []
        self._theta_buffer = []

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

            if self.current_selection:
                self._radius_buffer.append(r)
                self._theta_buffer.append(theta)

            if r < 0.06:
                dx = dy = 0  # suppress small jitters near center

            if 210 <= theta < 250:
                new_selection = "upper_left"
            elif 275 <= theta < 320:
                new_selection = "upper_right"

        # Dwell logic
        if new_selection:
            if self.button_actions.get(new_selection, {}).get("allow_dwell", True):
                if new_selection == self.current_selection:
                    self.dwell_progress += dt
                else:
                    self.current_selection = new_selection
                    self.dwell_progress = 0.0
                    self._radius_buffer = []
                    self._theta_buffer = []
        else:
            self.dwell_progress -= dt * 0.75

        self.dwell_progress = max(0.0, min(self.dwell_progress, self.trigger_time))

        # Trigger event
        event = None
        if self.dwell_progress >= self.trigger_time and self.current_selection:
            radius_arr = np.array(self._radius_buffer)
            theta_arr = np.array(self._theta_buffer)

            # Radius stats
            avg_r = float(np.mean(radius_arr))
            std_r = float(np.std(radius_arr))
            min_r = float(np.min(radius_arr))
            max_r = float(np.max(radius_arr))
            range_r = max_r - min_r
            jitter_r = std_r / avg_r if avg_r != 0 else 0

            # Theta stats
            avg_t = float(np.mean(theta_arr))
            std_t = float(np.std(theta_arr))
            min_t = float(np.min(theta_arr))
            max_t = float(np.max(theta_arr))
            angular_range = (max_t - min_t) if max_t >= min_t else (360 + max_t - min_t)
            jitter_t = std_t / 360

            r_stats = {
                "avg_radius": avg_r,
                "std_radius": std_r,
                "min_radius": min_r,
                "max_radius": max_r,
                "range_radius": range_r,
                "gaze_jitter_radius": jitter_r,
                "samples_radius": len(radius_arr)
            }

            t_stats = {
                "avg_theta": avg_t,
                "std_theta": std_t,
                "min_theta": min_t,
                "max_theta": max_t,
                "angular_range_theta": angular_range,
                "gaze_jitter_theta": jitter_t,
                "samples_theta": len(theta_arr)
            }

            event = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "action": self.current_selection,
                "gaze_point": {"x": round(hor, 6), "y": round(ver, 6)},
                "radius": round(r, 4) if r is not None else None,
                "theta": round(theta, 4) if theta is not None else None,
                **r_stats,
                **t_stats
            }

            self.dwell_progress = 0.0
            self.current_selection = None
            self._radius_buffer = []
            self._theta_buffer = []

        return draw_selector_overlay(frame, self), event
