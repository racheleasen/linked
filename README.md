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