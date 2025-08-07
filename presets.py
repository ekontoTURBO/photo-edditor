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
    "warm_r": 1.1,
    "warm_g": 1.05,
    "glow_strength": 0.6,
    "glow_blur": 10,
    "brightness": 1.1,
    "contrast": 1.05,
    "color": 1.2,
    "grain_strength": 15,
    "grain_effect": True,
    "sun_traces_effect": True
}

# On first run, save base preset if not present
presets = load_presets()
if "base" not in presets:
    presets["base"] = BASE_PRESET
    save_presets(presets)
