from flask import Flask, request, render_template, send_file, redirect, url_for
import json
from presets import load_presets, save_presets, BASE_PRESET
from zipfile import ZipFile
import tempfile
from PIL import Image, ImageEnhance, ImageFilter, ImageChops, ImageDraw
import io
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Image Editing Functions ---
def apply_warm_tone(image, r_factor=1.1, g_factor=1.05):
    r, g, b = image.split()
    r = r.point(lambda i: i * r_factor)
    g = g.point(lambda i: i * g_factor)
    return Image.merge('RGB', (r, g, b))

def add_soft_glow(image, strength=0.6, blur_radius=10):
    blurred = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return Image.blend(image, blurred, strength)

def enhance_image(image, brightness_factor=1.1, contrast_factor=1.05, color_factor=1.2):
    brightness = ImageEnhance.Brightness(image).enhance(brightness_factor)
    contrast = ImageEnhance.Contrast(brightness).enhance(contrast_factor)
    color = ImageEnhance.Color(contrast).enhance(color_factor)
    return color

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
        warm_r = float(request.form.get('warm_r', preset_values['warm_r']))
        warm_g = float(request.form.get('warm_g', preset_values['warm_g']))
        glow_strength = float(request.form.get('glow_strength', preset_values['glow_strength']))
        glow_blur = int(request.form.get('glow_blur', preset_values['glow_blur']))
        brightness = float(request.form.get('brightness', preset_values['brightness']))
        contrast = float(request.form.get('contrast', preset_values['contrast']))
        color = float(request.form.get('color', preset_values['color']))
        grain_strength = int(request.form.get('grain_strength', preset_values['grain_strength']))
        add_grain = request.form.get('grain_effect')
        add_sun_traces_effect = request.form.get('sun_traces_effect')

        # Save preset if requested
        if request.form.get('save_preset'):
            new_preset_name = request.form.get('preset_name', '').strip()
            if new_preset_name:
                presets[new_preset_name] = {
                    "warm_r": warm_r,
                    "warm_g": warm_g,
                    "glow_strength": glow_strength,
                    "glow_blur": glow_blur,
                    "brightness": brightness,
                    "contrast": contrast,
                    "color": color,
                    "grain_strength": grain_strength,
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
                    warm_image = apply_warm_tone(image, warm_r, warm_g)
                    glow_image = add_soft_glow(warm_image, glow_strength, glow_blur)
                    final_image = enhance_image(glow_image, brightness, contrast, color)
                    if add_grain:
                        final_image = add_film_grain(final_image, grain_strength)
                    if add_sun_traces_effect:
                        final_image = add_sun_traces(final_image)
                    out_path = os.path.join(zip_folder, f'edited_{file.filename}')
                    final_image.save(out_path, format='JPEG')
                    zipf.write(out_path, arcname=f'edited_{file.filename}')
        # After processing, show progress summary before download
        return render_template('index.html', progress_steps=progress_steps, show_progress=True, presets=presets, selected_preset=selected_preset, preset_values=preset_values)
    return render_template('index.html', show_progress=False, presets=presets, selected_preset=selected_preset, preset_values=preset_values)

if __name__ == '__main__':
    app.run(debug=False)
