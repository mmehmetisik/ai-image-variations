"""
Project configuration settings - Single Source of Truth
All constant values and API settings are defined here.
"""

import os  # for operating system interaction
from dotenv import load_dotenv  # for reading .env file

load_dotenv()  # loads variables from .env file

# === Hugging Face API Settings ===
HF_API_TOKEN = os.getenv("HF_API_TOKEN")  # get API key from .env
# NEW
HF_IMG2IMG_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-refiner-1.0"

# === Image Settings ===
MAX_FILE_SIZE_MB = 5  # maximum uploadable file size
ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg"]  # accepted file formats
DEFAULT_OUTPUT_SIZE = (512, 512)  # output image size (width, height)

# === Transformation Strength Settings ===
MIN_STRENGTH = 0.3  # minimum transformation strength (very similar to original)
MAX_STRENGTH = 0.9  # maximum transformation strength (very different result)
DEFAULT_STRENGTH = 0.6  # default transformation strength (balanced)

# === Application Settings ===
APP_TITLE = "AI Image Variations Generator"  # page title
APP_ICON = "🎨"  # icon to display in browser tab