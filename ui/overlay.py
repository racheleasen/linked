import cv2
import math
import time

def draw_buttons(frame, actions, selected_key, box_size):
    """Draws all button regions and their labels."""
    height, width = frame.shape[:2]
    box_w, box_h = box_size

    for key, data in actions.items():
        x_frac, y_frac = data["corner"]
        x = int(x_frac * (width - box_w))
        y = int(y_frac * (height - box_h))
        color = (0, 255, 0) if key == selected_key else (180, 180, 180)
        cv2.rectangle(frame, (x, y), (x + box_w, y + box_h), color, 2)
        cv2.putText(frame, data["label"], (x + 10, y + 40), cv2.FONT_HERSHEY_DUPLEX, 1, color, 2)

def draw_gaze_point(frame, hor, ver):
    """Draws the gaze point dot on screen."""
    height, width = frame.shape[:2]
    if hor is not None and ver is not None:
        gaze_x = int(hor * width)
        gaze_y = int(ver * height)
        cv2.circle(frame, (gaze_x, gaze_y), 6, (255, 0, 0), -1)

def draw_r_theta_debug(frame, r, theta):
    """Draws text displaying r and θ on screen."""
    height = frame.shape[0]
    if r is not None and theta is not None:
        cv2.putText(frame, f"r: {r:.2f}, θ: {theta:.0f}°", (20, height - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

def draw_dwell_arc(frame, center, radius, progress_ratio, color=(0, 255, 255), thickness=4):
    """Draws a circular arc representing dwell progress."""
    end_angle = int(progress_ratio * 360)
    for angle in range(0, end_angle, 5):
        rad = math.radians(angle - 90)
        x1 = int(center[0] + radius * math.cos(rad))
        y1 = int(center[1] + radius * math.sin(rad))
        x2 = int(center[0] + (radius - thickness) * math.cos(rad))
        y2 = int(center[1] + (radius - thickness) * math.sin(rad))
        cv2.ellipse(frame, center, (radius, radius), -90, 0, end_angle, color, thickness)

def draw_timestamp_and_latency(frame, latency):
    """Draws current timestamp and frame latency."""
    height = frame.shape[0]
    now_str = time.strftime("%H:%M:%S", time.localtime()) + f".{int((time.time() % 1) * 1000):03d}"
    cv2.putText(frame, f"Timestamp: {now_str}", (20, height - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)
    cv2.putText(frame, f"Gaze latency: {latency*1000:.1f} ms", (20, height - 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)

def draw_selector_overlay(frame, selector):
    height, width = frame.shape[:2]
    box_w, box_h = width // 4, height // 4

    for key, data in selector.button_actions.items():
        x_frac, y_frac = data["corner"]
        x = int(x_frac * (width - box_w))
        y = int(y_frac * (height - box_h))
        color = (0, 255, 0) if selector.current_selection == key else (180, 180, 180)

        # Create translucent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (x, y), (x + box_w, y + box_h), (180, 180, 180), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Draw border and label
        border_color = (0, 255, 0) if selector.current_selection == key else (100, 100, 100)
        cv2.rectangle(frame, (x, y), (x + box_w, y + box_h), border_color, 2)
        cv2.putText(frame, data["label"], (x + 10, y + 40),
                    cv2.FONT_HERSHEY_DUPLEX, 1, border_color, 2)

    return frame

