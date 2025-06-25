import time
import numpy as np
from gaze.base.gaze_tracking import GazeTracking

class ExtendedGazeTracker(GazeTracking):
    def __init__(self, dwell_threshold=1.0, debug=False):
        super().__init__()
        self._gaze_x = None
        self._gaze_y = None
        self.dwell_threshold = dwell_threshold
        self.debug = debug

    def refresh(self, frame):
        super().refresh(frame)

        if self.pupils_located:
            self._cache_gaze_ratios()

    def _cache_gaze_ratios(self):
        le = self.eye_left
        re = self.eye_right

        # Horizontal (X)
        le.x_min = min(p[0] for p in le.landmark_points)
        le.x_max = max(p[0] for p in le.landmark_points)
        re.x_min = min(p[0] for p in re.landmark_points)
        re.x_max = max(p[0] for p in re.landmark_points)

        le.x_abs = le.origin[0] + le.pupil.x
        re.x_abs = re.origin[0] + re.pupil.x

        lx_ratio = (le.x_abs - le.x_min) / (le.x_max - le.x_min)
        rx_ratio = (re.x_abs - re.x_min) / (re.x_max - re.x_min)
        self._gaze_x = (lx_ratio + rx_ratio) / 2

        # Vertical (Y)
        le.y_min = min(p[1] for p in le.landmark_points)
        le.y_max = max(p[1] for p in le.landmark_points)
        re.y_min = min(p[1] for p in re.landmark_points)
        re.y_max = max(p[1] for p in re.landmark_points)

        le.y_abs = le.origin[1] + le.pupil.y
        re.y_abs = re.origin[1] + re.pupil.y

        ly_ratio = (le.y_abs - le.y_min) / (le.y_max - le.y_min)
        ry_ratio = (re.y_abs - re.y_min) / (re.y_max - re.y_min)
        self._gaze_y = (ly_ratio + ry_ratio) / 2

        if self.debug:
            print(f"[DEBUG] gaze_x={self._gaze_x:.2f}, gaze_y={self._gaze_y:.2f}")

    def horizontal_ratio(self):
        return self._gaze_x

    def vertical_ratio(self):
        return self._gaze_y
    
    def is_blinking(self):
        if self.pupils_located:
            ratio = (self.eye_left.blinking + self.eye_right.blinking) / 2
            return ratio > 5.0
        return False