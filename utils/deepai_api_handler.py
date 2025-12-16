"""
Functions for communicating with DeepAI API.
Manages image-to-image transformation requests through DeepAI platform.

"""

import requests
from PIL import Image
import io
import os
from dotenv import load_dotenv

load_dotenv()  # load variables from .env file

# Get DeepAI API Key from .env file
DEEPAI_API_KEY = os.getenv("DEEPAI_API_KEY")

# DeepAI API endpoint
API_BASE_URL = "https://api.deepai.org/api"


def transform_image(image_bytes, prompt="", strength=0.6, negative_prompt=""):
    """
    Transforms image using DeepAI API.

    DeepAI Platform:
    - Budget-friendly unlimited API
    - Image Editor endpoint
    - Fast processing
    - $5/month unlimited

    Args:
        image_bytes: Image byte data
        prompt: Transformation instruction (text prompt)
        strength: Transformation strength (not directly supported in DeepAI, will be used in prompt)
        negative_prompt: Unwanted features (not available in DeepAI, will be ignored)

    Returns:
        tuple: (success status, result image or error message)
    """

    print("\n" + "🤖" * 35)
    print("=== DEEPAI API ===")
    print(f"Prompt: {prompt[:60] if prompt else 'Not specified'}...")
    print(f"Strength: {strength} (will be controlled via prompt)")
    print(f"Image size: {len(image_bytes)} bytes")
    print("🤖" * 35 + "\n")

    # API Key check
    if not DEEPAI_API_KEY:
        return False, "DeepAI API key not found. Add DEEPAI_API_KEY to .env file."

    print(f"✅ API Key: {DEEPAI_API_KEY[:10]}...{DEEPAI_API_KEY[-5:]}")

    try:
        # 1. Endpoint selection - Image Editor
        endpoint = f"{API_BASE_URL}/image-editor"
        print(f"🌐 1. Endpoint: {endpoint}")

        # 2. Prompt preparation
        # DeepAI has no strength parameter, we'll control via prompt
        if not prompt:
            prompt = "enhance, improve quality, detailed"

        # Adjust prompt based on strength
        if strength < 0.5:
            # Low strength = minimal change
            final_prompt = f"slightly modify: {prompt}, keep original style"
        elif strength < 0.7:
            # Medium strength = balanced
            final_prompt = f"transform into: {prompt}"
        else:
            # High strength = dramatic change
            final_prompt = f"completely transform into: {prompt}, creative interpretation"

        print(f"📝 2. Final Prompt: {final_prompt[:80]}...")

        # 3. API Headers
        headers = {
            "api-key": DEEPAI_API_KEY
        }

        # 4. Form data preparation
        # DeepAI expects multipart/form-data
        files = {
            "image": ("image.png", image_bytes, "image/png")
        }

        data = {
            "text": final_prompt
        }

        print("🚀 3. Making API call...")
        print("   ⏳ Processing may take 5-20 seconds...")

        # 5. API call
        response = requests.post(
            endpoint,
            headers=headers,
            files=files,
            data=data,
            timeout=60  # 60 second timeout
        )

        # 6. Response check
        print(f"📥 4. Response received: HTTP {response.status_code}")

        if response.status_code != 200:
            error_msg = response.text[:200]

            # Specific error cases
            if response.status_code == 401:
                return False, "DeepAI API key is invalid. Check your key."
            elif response.status_code == 402:
                return False, "No credit in your DeepAI account. Check your subscription."
            elif response.status_code == 429:
                return False, "Rate limit exceeded. Wait a few seconds and try again."
            elif response.status_code == 500:
                return False, "DeepAI server error. Please try again in a few minutes."
            else:
                return False, f"DeepAI API error ({response.status_code}): {error_msg}"

        # 7. Process result
        print("🔄 5. Processing result...")

        response_data = response.json()

        # DeepAI returns output_url
        output_url = response_data.get("output_url")

        if not output_url:
            return False, "Could not get image URL from DeepAI."

        print(f"   📥 Image URL received: {output_url[:50]}...")

        # 8. Download image
        print("   📥 Downloading image...")
        image_response = requests.get(output_url, timeout=30)

        if image_response.status_code != 200:
            return False, "Could not download image."

        # Convert to PIL Image
        result_image = Image.open(io.BytesIO(image_response.content))

        print(f"   📐 Result: {result_image.size}, {result_image.mode}")
        print("\n✨✨✨ SUCCESS! Image transformed with DeepAI! ✨✨✨\n")

        return True, result_image

    except requests.exceptions.Timeout:
        return False, "DeepAI timeout: Processing did not complete within 60 seconds."

    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        print(f"   ❌ Request Error: {error_msg[:150]}")
        return False, f"DeepAI connection error: {error_msg[:150]}"

    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Error: {type(e).__name__}")
        print(f"   📋 Message: {error_msg[:200]}")
        return False, f"DeepAI API error: {error_msg[:150]}"


def transform_with_style(image_bytes, style_config):
    """Transforms using a preset style template."""

    prompt = style_config["prompt"]
    strength = style_config.get("strength", 0.6)
    negative_prompt = style_config.get("negative_prompt", "")

    return transform_image(
        image_bytes=image_bytes,
        prompt=prompt,
        strength=strength,
        negative_prompt=negative_prompt  # not used in DeepAI but kept for compatibility
    )


# For testing
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("DEEPAI API - CONNECTION TEST")
    print("=" * 50 + "\n")

    if DEEPAI_API_KEY:
        print(f"✅ API Key found: {DEEPAI_API_KEY[:10]}...{DEEPAI_API_KEY[-5:]}")
        print("✅ DeepAI handler ready!\n")
        print("ℹ️  Note: DeepAI does not support strength parameter,")
        print("   it is controlled via prompt.\n")
    else:
        print("❌ DEEPAI_API_KEY not found!")
        print("   Add it to .env file:\n")
        print("   DEEPAI_API_KEY=your_api_key_here\n")