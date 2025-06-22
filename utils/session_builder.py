import cv2
import os
import json
import time
import numpy as np
from utils.gaze_base_extended.pupil_tracker import ExtendedGazeTracker

class UserBuilder:
    def __init__(self, user_id):
        self.user_id = str(user_id)
        self.account_path = "data/users/account.json"
        self.config_path = f"data/configs/{self.user_id}.json"
        self._ensure_dirs()
        self.session_id = None
        self.session_summary = {}
        self.session_events = []
        self.gaze_radii = []
        self.gaze_thetas = []

    def _ensure_dirs(self):
        os.makedirs("data/users", exist_ok=True)
        os.makedirs("data/configs", exist_ok=True)
        os.makedirs("data/user_data", exist_ok=True)

    def _convert(self, o):
        if isinstance(o, (np.integer, np.floating)):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(f"{o.__class__.__name__} not JSON serializable")

    def _user_data_path(self):
        return f"data/user_data/{self.user_id}.json"

    def _load_user_data(self):
        if os.path.exists(self._user_data_path()):
            with open(self._user_data_path(), "r") as f:
                return json.load(f)
        return {"user_id": self.user_id}

    def _save_user_data(self, data):
        with open(self._user_data_path(), "w") as f:
            json.dump(data, f, indent=2, default=self._convert)

    def create_user(self, metadata=None):
        users = self._load_account_registry()
        if self.user_id in users:
            print(f"[INFO] User '{self.user_id}' already exists.")
            return
        users[self.user_id] = metadata or {"created": time.strftime("%Y-%m-%d %H:%M:%S")}
        self._save_account_registry(users)
        print(f"[SUCCESS] User '{self.user_id}' created.")

    def validate_user(self):
        users = self._load_account_registry()
        return self.user_id in users

    def _load_account_registry(self):
        if os.path.exists(self.account_path):
            with open(self.account_path, "r") as f:
                return json.load(f)
        return {}

    def _save_account_registry(self, users):
        with open(self.account_path, "w") as f:
            json.dump(users, f, indent=2)

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return json.load(f)
        return {}

    def save_config(self, config):
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2, default=self._convert)

    def calibrate(self):
        print("[INFO] Please look straight at the screen for calibration...")
        gaze = ExtendedGazeTracker()
        webcam = cv2.VideoCapture(0)
        for _ in range(20):
            ret, frame = webcam.read()
            if not ret:
                continue
            gaze.refresh(frame)
        config = {
            "center_left": gaze.pupil_left_coords(),
            "center_right": gaze.pupil_right_coords()
        }
        self.save_config(config)
        webcam.release()
        print("[INFO] Calibration saved!")
        return config

    # --- Session-based logging ---
    def init_session_stats(self, session_id):
        self.session_id = session_id
        self.session_summary = {
            "user_id": self.user_id,
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_frames": 0,
            "total_blinks": 0,
            "triple_blinks": 0,
            "card_flips": 0,
            "cards_selected": [],
            "deck_activations": 0,
            "deck_deactivations": 0,
            "emergency_mode_entries": 0,
            "emergency_mode_exits": 0,
            "avg_gaze_radius": None,
            "avg_gaze_theta": None,
            "total_dwell_events": 0,
            "total_dwell_time": 0.0
        }
        self.session_events = []
        self.gaze_radii = []
        self.gaze_thetas = []

    def log_event_detail(self, event):
        if not self.session_id:
            print("[WARN] Session ID not initialized — call init_session_stats() first.")
            return

        self.session_events.append(event)

        if "radius" in event:
            self.gaze_radii.append(event["radius"])
        if "theta" in event:
            self.gaze_thetas.append(event["theta"])
        if "dwell_time" in event:
            self.session_summary["total_dwell_time"] += event["dwell_time"]
            self.session_summary["total_dwell_events"] += 1
        if event.get("type") == "card_selected":
            self.session_summary["cards_selected"].append(event["label"])

    def save_session_data(self, config=None):
        self.session_summary["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.gaze_radii:
            self.session_summary["avg_gaze_radius"] = sum(self.gaze_radii) / len(self.gaze_radii)
        if self.gaze_thetas:
            self.session_summary["avg_gaze_theta"] = sum(self.gaze_thetas) / len(self.gaze_thetas)

        data = self._load_user_data()
        data[self.session_id] = {
            "config": config or self.load_config(),
            "summary": self.session_summary,
            "events": self.session_events
        }
        self._save_user_data(data)

