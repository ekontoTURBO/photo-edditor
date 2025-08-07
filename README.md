# Dreamy Photo Editor - Local Setup Guide

This guide will help you set up and run the Dreamy Photo Editor app on your Windows PC using Anaconda (Conda) and Python.

---

## 1. Install Anaconda (Conda)

Download and install Anaconda (includes Conda):
- [Anaconda Individual Edition Download](https://www.anaconda.com/products/distribution)
- [Miniconda Download (lighter version)](https://docs.conda.io/en/latest/miniconda.html)

During installation, **check the box to add Anaconda/Miniconda to your PATH** for easier terminal access.

---

## 2. Open Anaconda Prompt

- Search for **Anaconda Prompt** in your Start Menu and open it.

---


## 3. Navigate to Your Project Folder

In Anaconda Prompt, run:

```
cd C:\Users\<your-username>\Desktop\VSCode\photo-edditor
```

---

## 4. Create a New Conda Environment

```
conda create -n photoeditor python=3.11
```

- This creates a new environment called `photoeditor` with Python 3.11.

---

## 5. Activate the Environment

```
conda activate photoeditor
```

---

## 6. Install Required Packages

```
pip install flask pillow
```

---

## 7. Download or Clone the Project

- Place the project files (including `app.py`, `templates/index.html`, and the `uploads` folder) in the folder you navigated to above.

---

## 8. Run the Flask App

```
python app.py
```

- You should see output like:
  `* Running on http://127.0.0.1:5000`

---

## 9. Use the App

- Open your browser and go to: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- Upload a photo, select effects, and click "Edit Photo" to download your edited image.

---

## Troubleshooting

- If you see `conda : The term 'conda' is not recognized...`, use the Anaconda Prompt or add Anaconda/Miniconda to your PATH.
- If you get import errors, make sure you installed Flask and Pillow in the correct environment.
- For more help: [Anaconda Documentation](https://docs.anaconda.com/)

---

## Useful Links
- [Anaconda Download](https://www.anaconda.com/products/distribution)
- [Miniconda Download](https://docs.conda.io/en/latest/miniconda.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pillow Documentation](https://pillow.readthedocs.io/)

---

Enjoy editing your photos locally!
