from flask import Flask, request, render_template, send_file, redirect, url_for
import json
from presets import load_presets, save_presets, BASE_PRESET
from zipfile import ZipFile
import tempfile
from PIL import Image, ImageEnhance, ImageFilter, ImageChops, ImageDraw
import numpy as np
import io
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Image Editing Functions ---
def apply_warmth(img, warmth_factor=1.08, warm_r=None, warm_g=None):
    r, g, b = img.split()
    if warm_r is not None and warm_g is not None:
        r = r.point(lambda i: min(255, max(0, i * warm_r)))
        g = g.point(lambda i: min(255, max(0, i * warm_g)))
    else:
        r = r.point(lambda i: min(255, max(0, i * warmth_factor)))
        g = g.point(lambda i: min(255, max(0, i * (1 - (warmth_factor - 1) / 3))))
    return Image.merge('RGB', (r, g, b))

def add_soft_glow(image, strength=0.6, blur_radius=10):
    blurred = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return Image.blend(image, blurred, strength)

def edit_image(image, params):
    # Warmth
    image = apply_warmth(
        image,
        warmth_factor=params.get('warmth_factor', 1.08),
        warm_r=params.get('warm_r'),
        warm_g=params.get('warm_g')
    )
    # Glow
    if params.get('glow_strength', 0) > 0:
        glow = image.filter(ImageFilter.GaussianBlur(radius=params.get('glow_blur', 8)))
        image = Image.blend(image, glow, alpha=params.get('glow_strength', 0.15))
    # Brightness
    image = ImageEnhance.Brightness(image).enhance(params.get('brightness', 1.05))
    # Contrast
    image = ImageEnhance.Contrast(image).enhance(params.get('contrast', 1.12))
    # Vibrance/Saturation
    vibrance = params.get('vibrance', 1.10)
    image = ImageEnhance.Color(image).enhance(vibrance)
    # Color (legacy, for compatibility)
    image = ImageEnhance.Color(image).enhance(params.get('color', 1.0))
    # Grain
    if params.get('grain_strength', 0) > 0:
        image = add_film_grain(image, params.get('grain_strength', 0))
    # Sun Traces
    if params.get('sun_traces', 0) > 0:
        image = add_sun_traces(image, params.get('sun_traces', 0))
    # Sharpness
    sharpness = params.get('sharpness', 1.3)
    if sharpness > 0:
        image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=int(sharpness*100), threshold=3))
    return image

def add_film_grain(image, grain_strength=15):
    width, height = image.size
    noise = Image.effect_noise((width, height), grain_strength)
    noise = noise.convert("L")
    noise_colored = Image.merge("RGB", (noise, noise, noise))
    return ImageChops.add(image, noise_colored, scale=2.0)

def add_light_leak(image):
    leak = Image.new("RGB", image.size, (0, 0, 0))
    draw = ImageDraw.Draw(leak)
    for i in range(300):
        color = (255, 80, 60, max(0, 200 - i))
        draw.ellipse([-100 - i, -100 - i, 300 + i, 300 + i], fill=color)
    leak = leak.filter(ImageFilter.GaussianBlur(radius=80))
    final = Image.blend(image, leak, alpha=0.15)
    return final

def add_sun_traces(image):
    overlay = Image.new("RGB", image.size, (255, 200, 150))
    draw = ImageDraw.Draw(overlay)
    for i in range(400):
        color = (255, 210, 160)
        draw.ellipse([-200 - i, -200 - i, 400 + i, 400 + i], fill=color)
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=100))
    final = Image.blend(image, overlay, alpha=0.12)
    return final

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    presets = load_presets()
    selected_preset = request.form.get('preset', 'base')
    preset_values = presets.get(selected_preset, BASE_PRESET)
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        files = request.files.getlist('file')
        if not files or all(f.filename == '' for f in files):
            return redirect(request.url)

        # Get slider values or preset

        warmth_factor = float(request.form.get('warmth_factor', preset_values.get('warmth_factor', 1.08)))
        warm_r = float(request.form.get('warm_r', preset_values['warm_r']))
        warm_g = float(request.form.get('warm_g', preset_values['warm_g']))
        glow_strength = float(request.form.get('glow_strength', preset_values['glow_strength']))
        glow_blur = int(request.form.get('glow_blur', preset_values['glow_blur']))
        brightness = float(request.form.get('brightness', preset_values['brightness']))
        contrast = float(request.form.get('contrast', preset_values['contrast']))
        vibrance = float(request.form.get('vibrance', preset_values.get('vibrance', 1.10)))
        color = float(request.form.get('color', preset_values['color']))
        grain_strength = int(request.form.get('grain_strength', preset_values['grain_strength']))
        sharpness = float(request.form.get('sharpness', preset_values.get('sharpness', 1.3)))
        sun_traces = int(request.form.get('sun_traces', preset_values.get('sun_traces', 0)))
        add_grain = request.form.get('grain_effect')
        add_sun_traces_effect = request.form.get('sun_traces_effect')

        # Save preset if requested
        if request.form.get('save_preset'):
            new_preset_name = request.form.get('preset_name', '').strip()
            if new_preset_name:
                presets[new_preset_name] = {
                    "warmth_factor": warmth_factor,
                    "warm_r": warm_r,
                    "warm_g": warm_g,
                    "glow_strength": glow_strength,
                    "glow_blur": glow_blur,
                    "brightness": brightness,
                    "contrast": contrast,
                    "vibrance": vibrance,
                    "color": color,
                    "grain_strength": grain_strength,
                    "sharpness": sharpness,
                    "sun_traces": sun_traces,
                    "grain_effect": bool(add_grain),
                    "sun_traces_effect": bool(add_sun_traces_effect)
                }
                save_presets(presets)

        progress_steps = []
        total = len([f for f in files if f.filename])
        current = 0
        zip_folder = os.path.join(os.getcwd(), 'uploads')
        if not os.path.exists(zip_folder):
            os.makedirs(zip_folder)
        zip_path = os.path.join(zip_folder, 'edited_photos.zip')
        with ZipFile(zip_path, 'w') as zipf:
            for file in files:
                if file and file.filename:
                    current += 1
                    step_msg = f"Processing {file.filename} ({current}/{total})..."
                    progress_steps.append(step_msg)
                    img_stream = io.BytesIO(file.read())
                    image = Image.open(img_stream).convert('RGB')
                    # Use custom parameters
                    params = {
                        'warmth_factor': warmth_factor,
                        'warm_r': warm_r,
                        'warm_g': warm_g,
                        'glow_strength': glow_strength,
                        'glow_blur': glow_blur,
                        'brightness': brightness,
                        'contrast': contrast,
                        'vibrance': vibrance,
                        'color': color,
                        'grain_strength': grain_strength,
                        'sun_traces': sun_traces,
                        'sharpness': sharpness
                    }
                    final_image = edit_image(image, params)
                    out_path = os.path.join(zip_folder, f'edited_{file.filename}')
                    final_image.save(out_path, format='JPEG')
                    zipf.write(out_path, arcname=f'edited_{file.filename}')
        # After processing, show progress summary before download
        return render_template('index.html', progress_steps=progress_steps, show_progress=True, presets=presets, selected_preset=selected_preset, preset_values=preset_values)
    return render_template('index.html', show_progress=False, presets=presets, selected_preset=selected_preset, preset_values=preset_values)

if __name__ == '__main__':
    app.run(debug=False)
