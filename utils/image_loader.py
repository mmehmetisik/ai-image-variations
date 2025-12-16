"""
Image loading and preprocessing functions.
Validates user uploaded images and prepares them for API.
"""

from PIL import Image  # image processing library
import io  # for byte stream operations
from config.settings import MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS, DEFAULT_OUTPUT_SIZE  # central settings


def validate_image(uploaded_file):
    """Checks if the uploaded file is valid."""

    if uploaded_file is None:  # if no file uploaded
        return False, "Please upload an image."

    file_extension = uploaded_file.name.split(".")[-1].lower()  # get file extension
    if file_extension not in ALLOWED_EXTENSIONS:  # if not in allowed formats
        return False, f"Unsupported format. Allowed: {ALLOWED_EXTENSIONS}"

    file_size_mb = uploaded_file.size / (1024 * 1024)  # convert bytes to MB
    if file_size_mb > MAX_FILE_SIZE_MB:  # if exceeds size limit
        return False, f"File too large. Maximum: {MAX_FILE_SIZE_MB}MB"

    return True, "Image is valid."  # passed all checks


def load_and_preprocess(uploaded_file):
    """Loads image, converts to RGB and resizes."""

    image = Image.open(uploaded_file)  # open image

    if image.mode == "RGBA":  # if has transparent background
        background = Image.new("RGB", image.size, (255, 255, 255))  # create white background
        background.paste(image, mask=image.split()[3])  # paste using alpha channel
        image = background
    elif image.mode != "RGB":  # if not RGB
        image = image.convert("RGB")  # convert to RGB

    return image


def resize_image(image, max_size=DEFAULT_OUTPUT_SIZE):
    """Resizes image while maintaining aspect ratio."""

    image.thumbnail(max_size, Image.Resampling.LANCZOS)  # highest quality resize algorithm
    return image


def image_to_bytes(image):
    """Converts PIL Image object to byte array (required for API)."""

    byte_stream = io.BytesIO()  # create byte stream in memory
    image.save(byte_stream, format="PNG")  # save as PNG
    byte_stream.seek(0)  # go to stream start
    return byte_stream.getvalue()  # return byte data