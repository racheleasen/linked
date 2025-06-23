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

## JSON Payload Example
```
{
  "user_id": "99",
  "20250623_175007": {
    "config": {
      "center_left": [
        596,
        331
      ],
      "center_right": [
        706,
        329
      ]
    },
    "summary": {
      "user_id": "99",
      "start_time": "2025-06-23 17:50:07",
      "total_frames": 313,
      "total_blinks": 56,
      "triple_blinks": 0,
      "card_flips": 28,
      "cards_selected": [
        "Basic Needs Menu","Hungry","Uncomfortable","Sentiment Menu","I appreciate you","Feeling overwhelmed"
      ],
      "deck_activations": 3,
      "deck_deactivations": 2,
      "emergency_mode_entries": 0,
      "emergency_mode_exits": 0,
      "avg_gaze_radius": 0.16780498041410544,
      "std_gaze_radius": 0.013052086294084634,
      "range_gaze_radius": 0.034500481218571355,
      "avg_gaze_theta": 265.35798353076757,
      "std_gaze_theta": 20.43045070451582,
      "angular_range_theta": 52.52514195784232,
      "total_dwell_events": 8,
      "total_dwell_time": 0.0,
      "end_time": "2025-06-23 17:50:50"
    },
    "events": [
      {
        "timestamp": "2025-06-23 17:50:17",
        "action": "upper_right",
        "gaze_point": {
          "x": 0.529623,
          "y": 0.357143
        },
        "radius": 0.1459,
        "theta": 281.7151,
        "avg_radius": 0.1532757251939758,
        "std_radius": 0.027596221506297404,
        "min_radius": 0.10509372923934293,
        "max_radius": 0.20544366619228438,
        "range_radius": 0.10034993695294145,
        "gaze_jitter_radius": 0.1800430007515764,
        "samples_radius": 10,
        "avg_theta": 282.59792229135286,
        "std_theta": 6.949876898639898,
        "min_theta": 276.040216583606,
        "max_theta": 300.3843069300189,
        "angular_range_theta": 24.344090346412884,
        "gaze_jitter_theta": 0.01930521360733305,
        "samples_theta": 10,
        "horizontal_ratio": 0.5296234772978959,
        "vertical_ratio": 0.3571428571428571,
        "dwell_time": 0.0,
        "type": "card_selected",
        "label": "Basic Needs Menu"
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