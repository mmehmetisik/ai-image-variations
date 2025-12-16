"""
Image processing and manipulation functions.
Resizing, comparison and multiple variation operations.
"""

from PIL import Image, ImageEnhance, ImageFilter  # image processing tools
import io  # for byte stream operations
import random  # for random seed generation


def create_side_by_side(original, transformed, spacing=20):
    """Combines two images side by side (for comparison)."""

    original = original.convert("RGB")  # convert to RGB for format compatibility
    transformed = transformed.convert("RGB")

    total_width = original.width + transformed.width + spacing  # total width
    max_height = max(original.height, transformed.height)  # the tallest one

    combined = Image.new("RGB", (total_width, max_height), (255, 255, 255))  # canvas with white background
    combined.paste(original, (0, 0))  # paste original on the left
    combined.paste(transformed, (original.width + spacing, 0))  # paste transformed on the right

    return combined


def generate_random_seed():
    """Generates random seed (for different variations)."""

    return random.randint(1, 2147483647)  # random number in 32-bit integer range


def create_image_grid(images, columns=2, spacing=10):
    """Combines multiple images in a grid layout."""

    if not images:  # if list is empty
        return None

    rows = (len(images) + columns - 1) // columns  # number of rows needed (rounded up)

    img_width = images[0].width  # use first image dimensions as reference
    img_height = images[0].height

    grid_width = columns * img_width + (columns - 1) * spacing  # grid total width
    grid_height = rows * img_height + (rows - 1) * spacing  # grid total height

    grid = Image.new("RGB", (grid_width, grid_height), (255, 255, 255))  # white canvas

    for idx, img in enumerate(images):  # place each image in order
        row = idx // columns  # which row
        col = idx % columns  # which column
        x = col * (img_width + spacing)  # x coordinate
        y = row * (img_height + spacing)  # y coordinate
        grid.paste(img, (x, y))  # paste image

    return grid


def apply_enhancement(image, brightness=1.0, contrast=1.0, sharpness=1.0):
    """Applies basic enhancements to image."""

    if brightness != 1.0:  # brightness adjustment
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness)

    if contrast != 1.0:  # contrast adjustment
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)

    if sharpness != 1.0:  # sharpness adjustment
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(sharpness)

    return image


def get_image_info(image):
    """Returns information about the image (for metadata)."""

    return {
        "width": image.width,  # width in pixels
        "height": image.height,  # height in pixels
        "mode": image.mode,  # color mode (RGB, RGBA etc)
        "format": image.format,  # file format
        "size_kb": len(image.tobytes()) / 1024  # approximate size in KB
    }