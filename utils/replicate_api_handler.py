"""
Functions for communicating with Replicate API.
Manages image-to-image transformation requests through Replicate platform.

Replicate: Production-ready AI model hosting platform
Model: timbrooks/instruct-pix2pix (Image editing with instructions)
"""

import replicate
from PIL import Image
import io
import os
from dotenv import load_dotenv

load_dotenv()  # load variables from .env file

# Get Replicate API Token from .env file
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")


def transform_image(image_bytes, prompt="", strength=0.6, negative_prompt=""):
    """
    Transforms image using Replicate API.

    Replicate Platform:
    - Production-ready AI hosting
    - timbrooks/instruct-pix2pix model
    - Image editing with natural language instructions

    Args:
        image_bytes: Image byte data
        prompt: Transformation instruction (e.g., "turn into oil painting")
        strength: Transformation strength (0.0-1.0) - guidance scale for instruct-pix2pix
        negative_prompt: Unwanted features (not used, kept for compatibility)

    Returns:
        tuple: (success status, result image or error message)
    """

    print("\n" + "🎨" * 35)
    print("=== REPLICATE API - INSTRUCT-PIX2PIX ===")
    print(f"Prompt: {prompt[:60] if prompt else 'Not specified'}...")
    print(f"Guidance Scale: {strength}")
    print(f"Image size: {len(image_bytes)} bytes")
    print("🎨" * 35 + "\n")

    # Token check
    if not REPLICATE_API_TOKEN:
        return False, "Replicate API token not found. Add REPLICATE_API_TOKEN to .env file."

    print(f"✅ Token: {REPLICATE_API_TOKEN[:10]}...{REPLICATE_API_TOKEN[-5:]}")

    try:
        # 1. Replicate client automatically gets token from environment
        print("📝 1. Preparing Replicate client...")

        # 2. Convert image to base64 string (Replicate accepts this)
        print("🖼️  2. Preparing image...")
        import base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        image_data_uri = f"data:image/png;base64,{image_base64}"
        print(f"   ✅ Base64 encoded: {len(image_base64)} characters")

        # 3. Model parameters
        print("⚙️  3. Setting model parameters...")

        # Parameters expected by instruct-pix2pix
        input_params = {
            "image": image_data_uri,  # base64 encoded image
            "prompt": prompt if prompt else "improve the image quality",
            "num_inference_steps": 20,  # for better quality results
            "image_guidance_scale": 1.5,  # how faithful to original
            "guidance_scale": 7.5  # how much to follow prompt (similar to strength)
        }

        print(f"   Model: timbrooks/instruct-pix2pix")
        print(f"   Prompt: {input_params['prompt'][:50]}...")
        print(f"   Inference steps: {input_params['num_inference_steps']}")
        print(f"   Image guidance: {input_params['image_guidance_scale']}")
        print(f"   Text guidance: {input_params['guidance_scale']}")

        # 4. API call
        print("🌐 4. Making Replicate API call...")
        print("   ⏳ Running model (may take 10-30 seconds)...")

        output = replicate.run(
            "timbrooks/instruct-pix2pix:30c1d0b916a6f8efce20493f5d61ee27491ab2a60437c13c588468b9810ec23f",
            input=input_params
        )

        print("   ✅ API call successful!")

        # 5. Process result
        print("🔄 5. Processing result...")

        # Replicate output is usually URL or PIL Image
        if isinstance(output, str):
            # If URL, download it
            print(f"   📥 Downloading image from URL: {output[:50]}...")
            import requests
            response = requests.get(output)
            result_image = Image.open(io.BytesIO(response.content))
        elif isinstance(output, Image.Image):
            # Direct PIL Image
            result_image = output
        elif isinstance(output, list) and len(output) > 0:
            # If list, get first element
            if isinstance(output[0], str):
                print(f"   📥 Downloading image from URL...")
                import requests
                response = requests.get(output[0])
                result_image = Image.open(io.BytesIO(response.content))
            else:
                result_image = output[0]
        else:
            return False, f"Unexpected output format: {type(output)}"

        print(f"   📐 Result: {result_image.size}, {result_image.mode}")
        print("\n✨✨✨ SUCCESS! Image transformed with Replicate! ✨✨✨\n")

        return True, result_image

    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Error: {type(e).__name__}")
        print(f"   📋 Message: {error_msg[:200]}")

        # Specific error cases
        if "401" in error_msg or "authentication" in error_msg.lower():
            return False, "Replicate API token is invalid. Check your token."
        elif "402" in error_msg or "payment" in error_msg.lower() or "credit" in error_msg.lower():
            return False, "No credit in your Replicate account. Check your billing settings."
        elif "429" in error_msg or "rate limit" in error_msg.lower():
            return False, "Too many requests. Wait a few minutes and try again."
        elif "500" in error_msg or "503" in error_msg:
            return False, "Replicate servers are busy. Please try again in a few minutes."
        else:
            return False, f"Replicate API error: {error_msg[:150]}"


def transform_with_style(image_bytes, style_config):
    """Transforms using a preset style template."""

    # Get prompt from style config and adapt for Replicate
    prompt = style_config["prompt"]

    # Use strength as guidance_scale
    # instruct-pix2pix works a bit differently from strength
    strength = style_config.get("strength", 0.6)

    return transform_image(
        image_bytes=image_bytes,
        prompt=prompt,
        strength=strength,
        negative_prompt=style_config.get("negative_prompt", "")
    )