from flask import Flask, request, render_template, send_file, redirect, url_for
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
def apply_warm_tone(image):
    r, g, b = image.split()
    r = r.point(lambda i: i * 1.1)
    g = g.point(lambda i: i * 1.05)
    return Image.merge('RGB', (r, g, b))

def add_soft_glow(image, strength=0.6, blur_radius=10):
    blurred = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return Image.blend(image, blurred, strength)

def enhance_image(image):
    brightness = ImageEnhance.Brightness(image).enhance(1.1)
    contrast = ImageEnhance.Contrast(brightness).enhance(1.05)
    color = ImageEnhance.Color(contrast).enhance(1.2)
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
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        files = request.files.getlist('file')
        if not files or all(f.filename == '' for f in files):
            return redirect(request.url)

        add_grain = request.form.get('grain_effect')
        add_sun_traces_effect = request.form.get('sun_traces_effect')

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
                    warm_image = apply_warm_tone(image)
                    glow_image = add_soft_glow(warm_image)
                    final_image = enhance_image(glow_image)
                    if add_grain:
                        final_image = add_film_grain(final_image)
                    if add_sun_traces_effect:
                        final_image = add_sun_traces(final_image)
                    out_path = os.path.join(zip_folder, f'edited_{file.filename}')
                    final_image.save(out_path, format='JPEG')
                    zipf.write(out_path, arcname=f'edited_{file.filename}')
        # After processing, show progress summary before download
        return render_template('index.html', progress_steps=progress_steps, show_progress=True)
    return render_template('index.html', show_progress=False)

if __name__ == '__main__':
    app.run(debug=True)
