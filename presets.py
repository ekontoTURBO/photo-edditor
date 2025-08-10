import json
import os

PRESETS_FILE = 'presets.json'

# Load presets from file
def load_presets():
    if os.path.exists(PRESETS_FILE):
        with open(PRESETS_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save presets to file
def save_presets(presets):
    with open(PRESETS_FILE, 'w') as f:
        json.dump(presets, f, indent=2)

# Get default/base preset

BASE_PRESET = {
    "warmth_factor": 1.08,
    "warm_r": 1.08,
    "warm_g": 0.97,
    "glow_strength": 0.15,
    "glow_blur": 8,
    "brightness": 1.05,
    "contrast": 1.12,
    "vibrance": 1.10,
    "color": 1.0,
    "grain_strength": 0,
    "sharpness": 1.3,
    "sun_traces": 0,
    "grain_effect": False,
    "sun_traces_effect": False
}

CHATGPT_TEMPLATE = {
    "warmth_factor": 1.08,
    "warm_r": 1.08,
    "warm_g": 0.97,
    "glow_strength": 0.15,
    "glow_blur": 8,
    "brightness": 1.05,
    "contrast": 1.12,
    "vibrance": 1.10,
    "color": 1.0,
    "grain_strength": 0,
    "sharpness": 1.3,
    "sun_traces": 0,
    "grain_effect": False,
    "sun_traces_effect": False
}

# On first run, save base preset if not present
presets = load_presets()
changed = False
if "base" not in presets:
    presets["base"] = BASE_PRESET
    changed = True
if "chatgpt_template" not in presets:
    presets["chatgpt_template"] = CHATGPT_TEMPLATE
    changed = True
if changed:
    save_presets(presets)
