"""
Functions for communicating with Stability AI REST API.
Manages image-to-image transformation requests through Stability AI platform.

Stability AI: Professional-grade AI image generation platform
Endpoint: api.stability.ai REST API
Model: Stable Diffusion XL and variants
"""

import requests
from PIL import Image
import io
import os
import base64
from dotenv import load_dotenv

load_dotenv()  # load variables from .env file

# Get Stability AI API Key from .env file
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

# Stability AI API endpoint
API_HOST = "https://api.stability.ai"

# SDXL allowed dimensions (width x height)
SDXL_ALLOWED_DIMENSIONS = [
    (1024, 1024),  # Square
    (1152, 896),  # Landscape
    (1216, 832),
    (1344, 768),
    (1536, 640),
    (640, 1536),  # Portrait
    (768, 1344),
    (832, 1216),
    (896, 1152),
]


def resize_for_sdxl(image):
    """
    Resizes image to one of the dimensions accepted by SDXL model.
    Preserves aspect ratio as much as possible.
    """
    original_width, original_height = image.size
    original_aspect = original_width / original_height

    # Find the closest compatible dimension
    best_match = None
    best_aspect_diff = float('inf')

    for width, height in SDXL_ALLOWED_DIMENSIONS:
        target_aspect = width / height
        aspect_diff = abs(target_aspect - original_aspect)

        if aspect_diff < best_aspect_diff:
            best_aspect_diff = aspect_diff
            best_match = (width, height)

    # Resize
    resized = image.resize(best_match, Image.Resampling.LANCZOS)
    print(f"   📐 Resize: {original_width}x{original_height} → {best_match[0]}x{best_match[1]}")

    return resized


def transform_image(image_bytes, prompt="", strength=0.6, negative_prompt=""):
    """
    Transforms image using Stability AI REST API.

    Stability AI Platform:
    - Professional image generation API
    - Stable Diffusion XL models
    - High-quality image-to-image transformation

    Args:
        image_bytes: Image byte data
        prompt: Transformation instruction
        strength: Image strength (0.0-1.0) - lower = more similar to original
        negative_prompt: Unwanted features

    Returns:
        tuple: (success status, result image or error message)
    """

    print("\n" + "⚡" * 35)
    print("=== STABILITY AI REST API ===")
    print(f"Prompt: {prompt[:60] if prompt else 'Not specified'}...")
    print(f"Image Strength: {strength}")
    print(f"Image size: {len(image_bytes)} bytes")
    print("⚡" * 35 + "\n")

    # API Key check
    if not STABILITY_API_KEY:
        return False, "Stability AI API key not found. Add STABILITY_API_KEY to .env file."

    print(f"✅ API Key: {STABILITY_API_KEY[:10]}...{STABILITY_API_KEY[-5:]}")

    try:
        # 1. Convert image to PIL Image and resize to SDXL dimensions
        print(f"🖼️  1. Converting image to SDXL format...")
        image = Image.open(io.BytesIO(image_bytes))
        image = resize_for_sdxl(image)  # Resize to SDXL compatible dimensions

        # Convert resized image to bytes
        byte_stream = io.BytesIO()
        image.save(byte_stream, format="PNG")
        byte_stream.seek(0)
        image_bytes = byte_stream.getvalue()

        # 2. Engine selection (preferring SDXL)
        engine_id = "stable-diffusion-xl-1024-v1-0"
        print(f"🔧 2. Engine: {engine_id}")

        # 3. API endpoint
        url = f"{API_HOST}/v1/generation/{engine_id}/image-to-image"
        print(f"🌐 3. Endpoint: {url}")

        # 4. Headers preparation
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {STABILITY_API_KEY}"
        }

        # 5. Text prompts preparation
        text_prompts = []

        # Positive prompt
        if prompt:
            text_prompts.append({
                "text": prompt,
                "weight": 1.0
            })
        else:
            text_prompts.append({
                "text": "high quality, detailed, improved",
                "weight": 1.0
            })

        # Negative prompt
        if negative_prompt:
            text_prompts.append({
                "text": negative_prompt,
                "weight": -1.0
            })

        print(f"📝 4. Text prompts prepared:")
        print(f"   Positive: {text_prompts[0]['text'][:50]}...")
        if len(text_prompts) > 1:
            print(f"   Negative: {text_prompts[1]['text'][:50]}...")

        # 6. Form data preparation
        # Stability AI expects multipart/form-data
        files = {
            "init_image": ("image.png", image_bytes, "image/png")
        }

        # Image strength: 0 = fully original, 1 = completely new
        # Our strength: 0.3-0.9 range (how faithful to original)
        # We need to invert for Stability AI
        image_strength = 1.0 - strength  # Inverting

        data = {
            "text_prompts[0][text]": text_prompts[0]["text"],
            "text_prompts[0][weight]": text_prompts[0]["weight"],
            "image_strength": image_strength,  # 0.0-1.0
            "cfg_scale": 12.0,  # Prompt adherence (7.5 → 12.0 quality increase)
            "samples": 1,  # How many images to generate
            "steps": 50,  # Inference steps (30 → 50 high quality)
        }

        # Add negative prompt if exists
        if len(text_prompts) > 1:
            data["text_prompts[1][text]"] = text_prompts[1]["text"]
            data["text_prompts[1][weight]"] = text_prompts[1]["weight"]

        print(f"⚙️  5. Parameters:")
        print(f"   Image strength: {image_strength:.2f}")
        print(f"   CFG scale: {data['cfg_scale']}")
        print(f"   Steps: {data['steps']}")

        # 6. API call
        print("🚀 6. Making API call...")
        print("   ⏳ Generating image (may take 10-30 seconds)...")

        response = requests.post(
            url,
            headers=headers,
            files=files,
            data=data
        )

        # 7. Response check
        print(f"📥 7. Response received: HTTP {response.status_code}")

        if response.status_code != 200:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            error_message = error_data.get('message', response.text[:200])

            # Specific error cases
            if response.status_code == 401:
                return False, "Stability AI API key is invalid. Check your key."
            elif response.status_code == 402:
                return False, "No credit in your Stability AI account. Check your billing settings."
            elif response.status_code == 403:
                return False, "You don't have permission for this operation. Check your subscription plan."
            elif response.status_code == 404:
                return False, f"Engine not found: {engine_id}"
            elif response.status_code == 429:
                return False, "Rate limit exceeded. Wait a few seconds and try again."
            else:
                return False, f"Stability AI API error: {error_message}"

        # 8. Process result
        print("🔄 8. Processing result...")
        response_data = response.json()

        # Artifacts check
        if "artifacts" not in response_data or len(response_data["artifacts"]) == 0:
            return False, "No image returned from API."

        # Get first artifact
        artifact = response_data["artifacts"][0]

        # Finish reason check
        if artifact.get("finishReason") == "CONTENT_FILTERED":
            return False, "Caught by content filter. Please change your prompt."

        # Decode base64 image
        image_base64 = artifact.get("base64")
        if not image_base64:
            return False, "Could not get base64 image from API."

        print(f"   Base64 data: {len(image_base64)} characters")

        # Convert base64 to PIL Image
        image_data = base64.b64decode(image_base64)
        result_image = Image.open(io.BytesIO(image_data))

        print(f"   📐 Result: {result_image.size}, {result_image.mode}")
        print("\n✨✨✨ SUCCESS! Image transformed with Stability AI! ✨✨✨\n")

        return True, result_image

    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        print(f"   ❌ Request Error: {error_msg[:150]}")
        return False, f"Stability AI connection error: {error_msg[:150]}"

    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Error: {type(e).__name__}")
        print(f"   📋 Message: {error_msg[:200]}")
        return False, f"Stability AI API error: {error_msg[:150]}"


def transform_with_style(image_bytes, style_config):
    """Transforms using a preset style template."""

    # Get parameters from style config
    prompt = style_config["prompt"]
    strength = style_config.get("strength", 0.6)
    negative_prompt = style_config.get("negative_prompt", "")

    return transform_image(
        image_bytes=image_bytes,
        prompt=prompt,
        strength=strength,
        negative_prompt=negative_prompt
    )