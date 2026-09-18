"""
Animation and mascot visualizer engine for Buddy Agent UI
"""

import time
from rich.text import Text
from .config import COLOR_PEACH, COLOR_AMBER, COLOR_MINT, get_random_champ_compliment


class BuddyEmpathyComplimentsAnimation:
    """
    Renders Buddy Bear on the left side sending heartwarming, caring developer
    compliments directly to the user during agent execution.
    """
    def __init__(self):
        self.step_counter = 0
        self.start_time = time.time()
        self.current_compliment = get_random_champ_compliment()
        self.compliment_timer = time.time()

    def tick(self) -> None:
        self.step_counter += 1
        if time.time() - self.compliment_timer > 3.0:
            self.current_compliment = get_random_champ_compliment()
            self.compliment_timer = time.time()

    def render_line(self) -> Text:
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        frame = spinners[self.step_counter % len(spinners)]
        line = Text()
        line.append(f"{frame} ", style=f"bold {COLOR_PEACH}")
        line.append("🧸 ", style="bold")
        line.append("BUDDY // ", style=f"bold {COLOR_AMBER}")
        line.append(f"\"{self.current_compliment}\"", style=f"italic {COLOR_MINT}")
        return line
