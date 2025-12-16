"""
Functions for communicating with Hugging Face API.
Manages image-to-image transformation requests.

UPDATE: Using new router.huggingface.co endpoint.
Using non-gated models that work with free API.
"""

from huggingface_hub import InferenceClient
from PIL import Image
import io
import requests
import base64
from config.settings import HF_API_TOKEN


def transform_image(image_bytes, prompt="", strength=0.6, negative_prompt=""):
    """
    Transforms image using Hugging Face Inference API.

    Strategy:
    1. First try InstructPix2Pix (not gated, ideal for img2img)
    2. Then try other open models
    3. Last resort: direct API call

    Args:
        image_bytes: Image byte data
        prompt: Transformation guidance
        strength: Transformation strength (0.0-1.0)
        negative_prompt: Unwanted features

    Returns:
        tuple: (success status, result image or error message)
    """

    print("\n" + "=" * 70)
    print("=== HUGGING FACE IMAGE-TO-IMAGE ===")
    print(f"Prompt: {prompt[:60] if prompt else 'Not specified'}...")
    print(f"Strength: {strength}")
    print(f"Image size: {len(image_bytes)} bytes")
    print("=" * 70 + "\n")

    if not HF_API_TOKEN:
        return False, "API token not found. Check your .env file."

    print(f"✅ Token: {HF_API_TOKEN[:10]}...{HF_API_TOKEN[-5:]}")

    # === NON-GATED MODELS ===
    # These models don't require license approval and work with free API
    models_to_try = [
        {
            "name": "timbrooks/instruct-pix2pix",
            "description": "InstructPix2Pix - Natural language image editing",
            "type": "instruct"
        },
        {
            "name": "lllyasviel/sd-controlnet-canny",
            "description": "ControlNet Canny - Edge-based transformation",
            "type": "controlnet"
        },
        {
            "name": "stabilityai/stable-diffusion-xl-refiner-1.0",
            "description": "SDXL Refiner - Image enhancement",
            "type": "refiner"
        }
    ]

    # Prompt preparation
    if not prompt:
        prompt = "improve image quality, add details, enhance colors"

    # Convert prompt to instruction format for InstructPix2Pix
    instruct_prompt = prompt
    if not any(word in prompt.lower() for word in ["turn", "make", "change", "convert", "transform"]):
        instruct_prompt = f"transform this image: {prompt}"

    print(f"📝 Original Prompt: {prompt[:50]}...")
    print(f"📝 Instruct Prompt: {instruct_prompt[:50]}...")

    # === METHOD 1: Try with InferenceClient ===
    print("\n🔄 Method 1: InferenceClient API")
    print("-" * 50)

    try:
        client = InferenceClient(token=HF_API_TOKEN)
        print("✅ InferenceClient created")

        for model_info in models_to_try:
            model_name = model_info["name"]
            print(f"\n{'─' * 60}")
            print(f"🤖 Model: {model_name}")
            print(f"📋 {model_info['description']}")
            print(f"{'─' * 60}")

            try:
                print("🌐 Making API call...")

                # Different approach based on model type
                if model_info["type"] == "instruct":
                    # Special prompt for InstructPix2Pix
                    result = client.image_to_image(
                        image=image_bytes,
                        prompt=instruct_prompt,
                        model=model_name,
                        strength=strength,
                        guidance_scale=7.5
                    )
                else:
                    # Standard call for other models
                    result = client.image_to_image(
                        image=image_bytes,
                        prompt=prompt,
                        negative_prompt=negative_prompt if negative_prompt else None,
                        model=model_name,
                        strength=strength,
                        guidance_scale=7.5
                    )

                # Check result
                if isinstance(result, Image.Image):
                    print(f"✅ SUCCESS! Size: {result.size}")
                    print("\n" + "✨" * 25)
                    print("IMAGE SUCCESSFULLY TRANSFORMED!")
                    print("✨" * 25 + "\n")
                    return True, result

                elif hasattr(result, 'read'):
                    result = Image.open(result)
                    print(f"✅ SUCCESS! Size: {result.size}")
                    return True, result

            except Exception as e:
                error_msg = str(e)
                print(f"❌ Error: {error_msg[:100]}...")

                # Error analysis
                if "not supported" in error_msg.lower():
                    print("   ⚠️ This model doesn't support image-to-image")
                elif "503" in error_msg or "loading" in error_msg.lower():
                    print("   ⏳ Model is loading, wait 30 seconds and try again")
                elif "gated" in error_msg.lower() or "access" in error_msg.lower():
                    print("   🔒 This model requires access permission")
                elif "401" in error_msg:
                    print("   🔑 Token issue - but trying other models")
                elif "404" in error_msg or "not found" in error_msg.lower():
                    print("   🔭 Model not found or no access")

                continue

    except Exception as e:
        print(f"❌ InferenceClient error: {str(e)[:100]}")

    # === METHOD 2: Direct HTTP API call (NEW ENDPOINT) ===
    print("\n🔄 Method 2: Direct HTTP API (router.huggingface.co)")
    print("-" * 50)

    # Base64 encode
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    direct_models = [
        "timbrooks/instruct-pix2pix",
        "stabilityai/stable-diffusion-xl-refiner-1.0"
    ]

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    for model_name in direct_models:
        print(f"\n🤖 Direct API: {model_name}")

        # NEW ENDPOINT - using router.huggingface.co
        api_url = f"https://router.huggingface.co/hf-inference/models/{model_name}"

        try:
            # Prepare payload
            payload = {
                "inputs": {
                    "image": image_b64,
                    "prompt": instruct_prompt
                },
                "parameters": {
                    "strength": strength,
                    "guidance_scale": 7.5
                }
            }

            print(f"🌐 Sending HTTP POST: {api_url[:50]}...")
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)

            print(f"📥 Response: HTTP {response.status_code}")

            if response.status_code == 200:
                # Success - image returned
                result_image = Image.open(io.BytesIO(response.content))
                print(f"✅ SUCCESS! Size: {result_image.size}")
                print("\n" + "✨" * 25)
                print("IMAGE SUCCESSFULLY TRANSFORMED!")
                print("✨" * 25 + "\n")
                return True, result_image

            elif response.status_code == 503:
                # Model is loading
                try:
                    error_data = response.json()
                    wait_time = error_data.get("estimated_time", 30)
                    print(f"⏳ Model is loading... Estimated time: {wait_time:.0f} seconds")
                except:
                    print("⏳ Model is loading...")
                continue

            elif response.status_code == 401:
                print("🔑 Authorization error")
                continue

            elif response.status_code == 404:
                print("🔭 Model not found")
                continue

            elif response.status_code == 422:
                # Unprocessable Entity - payload format might be wrong
                print("⚠️ Payload format incompatible, trying alternative...")

                # Alternative payload format
                alt_payload = {
                    "inputs": image_b64,
                    "parameters": {
                        "prompt": instruct_prompt,
                        "strength": strength,
                        "guidance_scale": 7.5
                    }
                }

                response2 = requests.post(api_url, headers=headers, json=alt_payload, timeout=120)

                if response2.status_code == 200:
                    result_image = Image.open(io.BytesIO(response2.content))
                    print(f"✅ SUCCESS! Size: {result_image.size}")
                    return True, result_image
                else:
                    print(f"❌ Alternative also failed: HTTP {response2.status_code}")
                continue

            else:
                try:
                    error_data = response.json()
                    print(f"❌ Error: {error_data.get('error', 'Unknown error')[:100]}")
                except:
                    print(f"❌ HTTP Error: {response.status_code}")
                continue

        except requests.exceptions.Timeout:
            print("⏱️ Timeout - Model took too long")
            continue

        except Exception as e:
            print(f"❌ Request error: {str(e)[:100]}")
            continue

    # === ALL ATTEMPTS FAILED ===
    print("\n" + "=" * 70)
    print("❌ ALL MODELS FAILED")
    print("=" * 70)

    error_message = """
No suitable model found in Hugging Face free API.

Possible solutions:
1. Wait a few minutes and try again (models might be loading)
2. Try a different platform (DeepAI, Stability AI, Replicate)
3. Upgrade to Hugging Face Pro account

Note: Image-to-image support is limited in Hugging Face free tier.
"""

    return False, error_message.strip()


def transform_with_style(image_bytes, style_config):
    """Transforms using a preset style template."""

    print("\n" + "🎨" * 35)
    print(f"STYLE APPLICATION")
    print(f"Prompt: {style_config.get('prompt', 'N/A')[:50]}...")
    print(f"Strength: {style_config.get('strength', 0.6)}")
    print("🎨" * 35)

    return transform_image(
        image_bytes=image_bytes,
        prompt=style_config["prompt"],
        strength=style_config["strength"],
        negative_prompt=style_config.get("negative_prompt", "")
    )


# === TEST FUNCTION ===
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("HUGGING FACE API - CONNECTION TEST")
    print("=" * 50 + "\n")

    if HF_API_TOKEN:
        print(f"✅ Token found: {HF_API_TOKEN[:15]}...")

        # Simple API test
        try:
            client = InferenceClient(token=HF_API_TOKEN)
            print("✅ InferenceClient created")
            print("\n💡 Handler ready to use!")
            print("   Supported models:")
            print("   - timbrooks/instruct-pix2pix (InstructPix2Pix)")
            print("   - stabilityai/stable-diffusion-xl-refiner-1.0 (SDXL)")
        except Exception as e:
            print(f"❌ Client error: {e}")
    else:
        print("❌ HF_API_TOKEN not found!")
        print("   Add it to .env file:")
        print("   HF_API_TOKEN=hf_xxxxx")