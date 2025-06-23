# Gaze Interface

This project extends [GazeTracking](https://github.com/antoinelame/GazeTracking) to support a research project.

The goal is to implement a radial mapping between screen resolution and gaze vectors for an analysis on non-verbal communication intent signals using screen-based cues and dwell timers. 

There’s a working demo and a setup.sh script in the README.md to get started quickly. Feedback and contributions are welcomed from those with experience in accessibility tech. 

## Features

- Radial gaze-based module selection
- Dwell timer with customizable thresholds
- Per-user configuration and gaze calibration
- Session logging of gaze-based interactions
- Hierarchical deck navigation (main deck, subdecks)
- JSON-based event logging with timestamp, dwell metrics, and card labels

## Structure

- `utils/gaze_base_extended/`: Gaze tracking, blink detection, and selector logic
- `ui/`: Overlay drawing and UI interface helpers
- `utils/deck_manager.py`: Deck navigation and card logic
- `utils/session_builder.py`: Per-user session logging, calibration, and data handling
- `data/`: Stores user configs, logs, and session records
- `main.py`: Main application loop and runtime logic

## Per user per session Payload Example
```
{
  "user_id": "99",
  "20250621_202634": {
    "config": {
      "center_left": [626, 254],
      "center_right": [755, 250]
    },
    "summary": {
      "user_id": "99",
      "start_time": "2025-06-21 20:26:34",
      "end_time": "2025-06-21 20:27:00",
      "total_frames": 172,
      "total_blinks": 13,
      "card_flips": 7,
      "cards_selected": ["No", "Help Menu", "Emergency"],
      "deck_activations": 1,
      "deck_deactivations": 0,
      "emergency_mode_entries": 1,
      "emergency_mode_exits": 1,
      "total_dwell_events": 3,
    },
    "events": [
      {
        "timestamp": "2025-06-21 20:26:42",
        "type": "card_selected",
        "label": "No",
        "horizontal_ratio": 0.53,
        "vertical_ratio": 0.36,
      },
      {
        "timestamp": "2025-06-21 20:26:45",
        "type": "card_selected",
        "label": "Help Menu",
        "horizontal_ratio": 0.54,
        "vertical_ratio": 0.39,
      },
      {
        "timestamp": "2025-06-21 20:26:49",
        "type": "card_selected",
        "label": "Emergency",
        "horizontal_ratio": 0.60,
        "vertical_ratio": 0.41,
      }
    ]
  }
}
```

## Getting Started
This interface uses a webcam feed and blink/gaze input to control a hierarchical, dwell-based selection menu. To run the application:

- Execute the setup.sh script to create a virtual environment and install all Python dependencies.
- Launch the interface with python main.py. Enter a user_id then the webcam will initialize automatically.
- Blink three times in rapid succession to activate the gaze-controlled main deck.
- Use gaze direction and dwell time to trigger actions or navigate to submenus (e.g., Basic Needs → Bathroom, Hungry, etc.).
- Use the Deactivate button to exit the main deck

```bash 
bash setup.sh
python main.py