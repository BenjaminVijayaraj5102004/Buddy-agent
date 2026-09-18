"""
Configuration, Constants, Palettes, and Model Catalog for Buddy Agent UI
"""

import random

APP_NAME = "PROJECT BUDDY AGENT"
VERSION = "1.2.0"

# Project I.G.I. Tactical Night-Vision Palette
COLOR_PEACH   = "#00ff55"  # Tactical Night-Vision Green (Primary)
COLOR_AMBER   = "#facc15"  # Tactical Warning Amber
COLOR_MINT    = "#00ff55"  # Mission Readiness Phosphor Green
COLOR_BLUE    = "#38bdf8"  # Satellite Sky Blue
COLOR_PURPLE  = "#a3e635"  # Tactical Lime / Session
COLOR_ROSE    = "#ef4444"  # Abort / Alert Red
COLOR_TEXT    = "#f0fdf4"  # Phosphor White / Text
COLOR_MUTED   = "#14532d"  # Camo Dark Olive (Borders)

# I.G.I. Palette Constants
IGI_GREEN_BRIGHT = "#00ff55"
IGI_GREEN_MID    = "#22c55e"
IGI_GREEN_DIM    = "#14532d"
IGI_METALLIC     = "#94a3b8"
IGI_WHITE        = "#f0fdf4"
IGI_AMBER        = "#facc15"

# Empathetic, Caring Developer Compliments from Buddy Bear
CHAMP_COMPLIMENTS = [
    "Hey Champ! 🌟 Your code is getting ready. Just chill for a second — how was your day? Teddy's got this covered!",
    "Take it easy, Champ! ☕ You've been coding hard today. Sit back, relax, and let Teddy handle the heavy lifting for you!",
    "Hey friend! 💖 Remember to drink some water and stretch. Your solution is being crafted with care and perfection right now!",
    "Tough day or frustrating bugs earlier? Forget about it, Champ! 🏆 Teddy's on your side and we're building something great together!",
    "You're a brilliant engineer! 🐾 Never doubt yourself. Teddy is packaging the cleanest architecture for you right now! ✨",
    "Just chill, Champ! 🏖️ Coding can be tiring. Teddy's paws are flying across the keyboard to make your life easier! ⚡",
    "High paw, Champ! 🐾 You make complex backend and cloud engineering look effortless. Take a breather while I finish your code! ❤️",
    "Hey rockstar! 🌟 Sit back and relax. Even the hardest tasks are easy when we pair program together! Almost ready!",
]


def get_random_champ_compliment() -> str:
    """Selects an empathetic, caring compliment for the user while they wait."""
    return random.choice(CHAMP_COMPLIMENTS)


# Supported AI Model Catalog
MODELS_CATALOG = [
    {
        "id": "1",
        "key": "groq",
        "name": "Groq Cloud",
        "provider": "Groq Cloud",
        "cost": "Free / Low",
        "context": "128k",
        "recommended": True,
    },
    {
        "id": "2",
        "key": "ollama",
        "name": "Ollama Local ",
        "provider": "Local Host ",
        "cost": "Free (Local)",
        "context": "32k",
        "recommended": False,
    },
    {
        "id": "3",
        "key": "bedrock",
        "name": "AWS Bedrock",
        "provider": "AWS Bedrock ",
        "cost": "Standard",
        "context": "200k",
        "recommended": False,
    },
]
