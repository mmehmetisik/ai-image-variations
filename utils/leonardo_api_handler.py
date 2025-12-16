"""
Functions for communicating with Leonardo.ai API.
Manages image-to-image transformation requests through Leonardo.ai platform.

"""

import requests
from PIL import Image
import io
import os
import base64
import time
from dotenv import load_dotenv

load_dotenv()  # load variables from .env file

# Get Leonardo.ai API Key from .env file
LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")

# Leonardo.ai API endpoint
API_BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"


def transform_image(image_bytes, prompt="", strength=0.6, negative_prompt=""):
    """
    Transforms image using Leonardo.ai API.

    Leonardo.ai Platform:
    - Professional AI art generation
    - Leonardo Phoenix model (highest quality)
    - Image-to-image with init_strength

    Args:
        image_bytes: Image byte data
        prompt: Transformation instruction
        strength: Init strength (0.0-1.0)
            - 0.0 = completely original
            - 1.0 = completely new
        negative_prompt: Unwanted features

    Returns:
        tuple: (success status, result image or error message)
    """

    print("\n" + "🎨" * 35)
    print("=== LEONARDO.AI API ===")
    print(f"Prompt: {prompt[:60] if prompt else 'Not specified'}...")
    print(f"Init Strength: {strength}")
    print(f"Image size: {len(image_bytes)} bytes")
    print("🎨" * 35 + "\n")

    # API Key check
    if not LEONARDO_API_KEY:
        return False, "Leonardo.ai API key not found. Add LEONARDO_API_KEY to .env file."

    print(f"✅ API Key: {LEONARDO_API_KEY[:10]}...{LEONARDO_API_KEY[-5:]}")

    try:
        # 1. Upload init image
        print("📤 1. Uploading init image...")

        # Convert image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        upload_url = f"{API_BASE_URL}/init-image"
        upload_headers = {
            "accept": "application/json",
            "authorization": f"Bearer {LEONARDO_API_KEY}",
            "content-type": "application/json"
        }

        upload_payload = {
            "extension": "png",
            "name": "init_image.png",
            "imageDataUrl": f"data:image/png;base64,{image_base64}"
        }

        upload_response = requests.post(upload_url, json=upload_payload, headers=upload_headers)

        if upload_response.status_code != 200:
            error_msg = upload_response.json().get('error', upload_response.text)
            return False, f"Image upload error: {error_msg}"

        upload_data = upload_response.json()
        init_image_id = upload_data.get("uploadInitImage", {}).get("id")

        if not init_image_id:
            return False, "Could not get init image ID."

        print(f"   ✅ Init image uploaded: {init_image_id}")

        # 2. Start generation
        print("🎨 2. Starting generation...")

        generation_url = f"{API_BASE_URL}/generations"
        generation_headers = {
            "accept": "application/json",
            "authorization": f"Bearer {LEONARDO_API_KEY}",
            "content-type": "application/json"
        }

        # Prepare prompt
        if not prompt:
            prompt = "high quality, detailed, professional, improved"

        generation_payload = {
            "modelId": "6b645e3a-d64f-4341-a6d8-7a3690fbf042",  # Leonardo Phoenix
            "prompt": prompt,
            "negative_prompt": negative_prompt if negative_prompt else "low quality, blurry, distorted",
            "init_strength": strength,  # 0.0-1.0
            "init_image_id": init_image_id,
            "width": 1024,
            "height": 1024,
            "num_images": 1,
            "guidance_scale": 7.0,
            "num_inference_steps": 30
        }

        print(f"   Model: Leonardo Phoenix")
        print(f"   Prompt: {generation_payload['prompt'][:60]}...")
        print(f"   Init strength: {strength}")
        print(f"   Steps: 30")

        generation_response = requests.post(
            generation_url,
            json=generation_payload,
            headers=generation_headers
        )

        if generation_response.status_code != 200:
            error_msg = generation_response.json().get('error', generation_response.text)
            return False, f"Generation start error: {error_msg}"

        generation_data = generation_response.json()
        generation_id = generation_data.get("sdGenerationJob", {}).get("generationId")

        if not generation_id:
            return False, "Could not get generation ID."

        print(f"   ✅ Generation started: {generation_id}")

        # 3. Wait for generation to complete
        print("⏳ 3. Generation in progress...")
        print("   ⏱️ This process may take 20-60 seconds...")

        max_attempts = 60  # 60 second timeout
        attempt = 0

        while attempt < max_attempts:
            time.sleep(2)  # Check every 2 seconds
            attempt += 1

            status_url = f"{API_BASE_URL}/generations/{generation_id}"
            status_headers = {
                "accept": "application/json",
                "authorization": f"Bearer {LEONARDO_API_KEY}"
            }

            status_response = requests.get(status_url, headers=status_headers)

            if status_response.status_code != 200:
                continue

            status_data = status_response.json()
            generation_info = status_data.get("generations_by_pk", {})
            status = generation_info.get("status")

            print(f"   ⏳ Status: {status} ({attempt * 2}s)")

            if status == "COMPLETE":
                print("   ✅ Generation completed!")

                # Get the image
                generated_images = generation_info.get("generated_images", [])
                if not generated_images:
                    return False, "Image could not be generated."

                image_url = generated_images[0].get("url")
                if not image_url:
                    return False, "Could not get image URL."

                print(f"   📥 Downloading image: {image_url[:50]}...")

                # Download image
                image_response = requests.get(image_url)
                if image_response.status_code != 200:
                    return False, "Could not download image."

                result_image = Image.open(io.BytesIO(image_response.content))

                print(f"   📐 Result: {result_image.size}, {result_image.mode}")
                print("\n✨✨✨ SUCCESS! Image transformed with Leonardo.ai! ✨✨✨\n")

                return True, result_image

            elif status == "FAILED":
                return False, "Generation failed."

        return False, "Timeout: Generation did not complete within 60 seconds."

    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        print(f"   ❌ Request Error: {error_msg[:150]}")
        return False, f"Leonardo.ai connection error: {error_msg[:150]}"

    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Error: {type(e).__name__}")
        print(f"   📋 Message: {error_msg[:200]}")
        return False, f"Leonardo.ai API error: {error_msg[:150]}"


def transform_with_style(image_bytes, style_config):
    """Transforms using a preset style template."""

    prompt = style_config["prompt"]
    strength = style_config.get("strength", 0.6)
    negative_prompt = style_config.get("negative_prompt", "")

    return transform_image(
        image_bytes=image_bytes,
        prompt=prompt,
        strength=strength,
        negative_prompt=negative_prompt
    )


# For testing
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("LEONARDO.AI API - CONNECTION TEST")
    print("=" * 50 + "\n")

    if LEONARDO_API_KEY:
        print(f"✅ API Key found: {LEONARDO_API_KEY[:10]}...{LEONARDO_API_KEY[-5:]}")
        print("✅ Leonardo.ai handler ready!\n")
    else:
        print("❌ LEONARDO_API_KEY not found!")
        print("   Add it to .env file:\n")
        print("   LEONARDO_API_KEY=your_api_key_here\n")