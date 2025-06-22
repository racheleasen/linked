import time
import cv2
from utils.gaze_base_extended.pupil_tracker import ExtendedGazeTracker

# Action functions
def yes(): print("Yes")
def no(): print("No")
def help(): print("Help triggered")
def emergency(): print("Emergency triggered")
def accident(): print("Accident triggered")
def bathroom(): print("Bathroom requested")
def hungry(): print("Hungry signal")
def medicine(): print("Medicine needed")
def uncomfortable(): print("Uncomfortable")
def thank_you(): print("Thank you")
def love_you(): print("I love you")
def appreciation(): print("I appreciate you")
def happy(): print("Feeling happy")
def overwhelmed(): print("Feeling overwhelmed")
def upset(): print("Feeling upset")
def frustrated(): print("Feeling frustrated")
def sorry(): print("I'm sorry")

# Deck definition with nested subdecks
deck = [
    {"label": "Yes", "func": yes},
    {"label": "No", "func": no},
    {"label": "Help Menu", "func": help, "subdeck": [
        {"label": "Emergency", "func": emergency}
    ]},
    {"label": "Basic Needs Menu", "subdeck": [
        {"label": "Bathroom", "func": bathroom},
        {"label": "Hungry", "func": hungry},
        {"label": "Medicine", "func": medicine},
        {"label": "Uncomfortable", "func": uncomfortable}
    ]},
    {"label": "Sentiment Menu", "subdeck": [
        {"label": "Thank you", "func": thank_you},
        {"label": "I love you", "func": love_you},
        {"label": "I appreciate you", "func": appreciation},
        {"label": "Feeling happy", "func": happy},
        {"label": "Feeling overwhelmed", "func": overwhelmed},
        {"label": "Feeling upset", "func": upset},
        {"label": "Feeling frustrated", "func": frustrated},
        {"label": "I'm sorry", "func": sorry}
    ]}
]

class DeckManager:
    def __init__(self, deck, cooldown=1, selector=None):
        self.root_deck = deck
        self.deck_stack = [deck]
        self.index_stack = [0]
        self.cooldown = cooldown
        self.selector = selector
        self.last_blink = 0
        self.active = False

    def activate(self):
        self.active = True
        if self.selector:
            self.selector.dwell_enabled = True

    def deactivate(self):
        self.active = False
        self.deck_stack = [self.root_deck]
        self.index_stack = [0]
        if self.selector:
            self.selector.dwell_enabled = False

    def is_active(self):
        return self.active

    def current_deck(self):
        return self.deck_stack[-1]

    def current_index(self):
        return self.index_stack[-1]

    def current_card(self):
        deck = self.current_deck()
        index = self.current_index() % len(deck)
        return deck[index]

    def next(self):
        self.index_stack[-1] += 1

    def on_blink(self, now=None):
        """Only advance deck index."""
        if not self.active:
            return None
        now = now or time.time()
        if now - self.last_blink > self.cooldown:
            self.last_blink = now
            self.next()
            return self.current_card()
        return None

    def select(self):
        card = self.current_card()
        if "subdeck" in card:
            self.deck_stack.append(card["subdeck"])
            self.index_stack.append(0)
        elif "func" in card:
            card["func"]()
        return card

    def back(self):
        """Return to previous deck level."""
        if len(self.deck_stack) > 1:
            self.deck_stack.pop()
            self.index_stack.pop()

    def draw(self, frame):
        if not self.active:
            return frame

        card = self.current_card()
        text = f"{card['label']}"
        font = cv2.FONT_HERSHEY_DUPLEX
        scale = 1.2
        thickness = 2
        color = (0, 255, 0)

        text_size, _ = cv2.getTextSize(text, font, scale, thickness)
        text_width, text_height = text_size
        text_x = (frame.shape[1] - text_width) // 2
        text_y = 60

        cv2.putText(frame, text, (text_x, text_y), font, scale, color, thickness, cv2.LINE_AA)

        return frame
