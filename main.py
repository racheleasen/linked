import cv2
import time
import uuid
from ui import overlay
from utils.gaze_base_extended.pupil_tracker import ExtendedGazeTracker
from utils.gaze_base_extended.gaze_selector import GazeSelector
from utils.gaze_base_extended.blink_manager import BlinkManager
from utils.deck_manager import DeckManager, deck
from utils.session_builder import UserBuilder

# User session configuration
user_id = input("Enter your user ID: ").strip()
user = UserBuilder(user_id)
user.create_user(metadata={"created_at": time.strftime("%Y-%m-%d %H:%M:%S")})

if not user.validate_user():
    print("[ERROR] User ID not recognized.")
    exit()

user_config = user.calibrate()
session_id = time.strftime("%Y%m%d_%H%M%S")
user.init_session_stats(session_id)

# Intialize modules
gaze = ExtendedGazeTracker()
selector = GazeSelector(trigger_time=1.25, center=(0.5, 0.5), inner_radius=0.00, outer_radius=0.25)
blink_manager = BlinkManager()
deck_manager = DeckManager(deck, selector=selector)
webcam = cv2.VideoCapture(0)
emergency_mode = False

# Main Loop
while True:
    ret, frame = webcam.read()
    if not ret:
        print("Failed to capture frame.")
        break

    frame = cv2.flip(frame, 1)
    gaze.refresh(frame)
    selector.dwell_enabled = not gaze.is_blinking()
    user.session_summary["total_frames"] += 1

    # Process gaze selection
    frame, event = selector.process(
        frame,
        gaze,
        deck_manager=deck_manager if deck_manager.is_active() else None,
        emergency_mode=emergency_mode
    )

    # Dwell progress arc
    if selector.current_selection and selector.dwell_progress > 0.0:
        height, width = frame.shape[:2]
        box_w, box_h = width // 4, height // 4
        x_frac, y_frac = selector.button_actions[selector.current_selection]["corner"]
        x = int(x_frac * (width - box_w))
        y = int(y_frac * (height - box_h))
        center = (x + box_w // 2, y + box_h // 2)
        dwell_ratio = selector.dwell_progress / selector.trigger_time
        overlay.draw_dwell_arc(frame, center, 30, dwell_ratio)

    # Handle Dwell triggered events
    if event:
        if emergency_mode:
            if event["action"] == "upper_left":
                emergency_mode = False
                user.session_summary["emergency_mode_exits"] += 1
                deck_manager.deactivate()
        else:
            if event["action"] == "upper_left":
                if deck_manager.is_active():
                    deck_manager.deactivate()
                    user.session_summary["deck_deactivations"] += 1
                else:
                    deck_manager.activate()
                    user.session_summary["deck_activations"] += 1
            elif event["action"] == "upper_right":
                if deck_manager.is_active():
                    selected_card = deck_manager.select()
                    user.session_summary["card_flips"] += 1

                    user.log_event_detail({
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "card_selected",
                        "label": selected_card["label"],
                        "horizontal_ratio": gaze.horizontal_ratio(),
                        "vertical_ratio": gaze.vertical_ratio(),
                        "dwell_time": selector.dwell_progress
                    })

                    if selected_card["label"].strip().lower() == "emergency":
                        emergency_mode = True
                        user.session_summary["emergency_mode_entries"] += 1

    # Blink Navigation
    if gaze.is_blinking():
        now = time.time()
        blink_type = blink_manager.register_blink(now)
        user.session_summary["total_blinks"] += 1

        if blink_type == "triple":
            deck_manager.activate()
            user.session_summary["deck_activations"] += 1
        elif deck_manager.is_active() and blink_type == "single":
            deck_manager.on_blink(now)
            user.session_summary["card_flips"] += 1

    # Deck UI
    frame = deck_manager.draw(frame)

    # Emergency Overlay... should probably be UI overlay
    if emergency_mode:
        text = "EMERGENCY"
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 3.0
        thickness = 5
        color = (0, 0, 255)

        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_width, text_height = text_size
        text_x = (frame.shape[1] - text_width) // 2
        text_y = (frame.shape[0] + text_height) // 2
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)

    cv2.imshow("Gaze Selector", frame)
    if cv2.waitKey(1) == 27:
        break

# Cleanup
user.save_session_data(config=user_config)
webcam.release()
cv2.destroyAllWindows()
