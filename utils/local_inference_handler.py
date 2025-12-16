"""
Local GPU Inference Handler
PyTorch + Diffusers image-to-image inference optimized for RTX 3060 6GB.

GPU Requirements:
- NVIDIA GPU (CUDA support)
- Minimum 6GB VRAM (RTX 3060, RTX 2060, etc)
- 16GB+ RAM recommended

Model: Stable Diffusion XL Refiner 1.0
"""

import torch
from diffusers import StableDiffusionXLImg2ImgPipeline
from PIL import Image
import io
import os

# Global variable - load pipeline once, use continuously
_pipeline = None
_device = None


def get_device():
    """Checks CUDA availability."""
    global _device

    if _device is not None:
        return _device

    if torch.cuda.is_available():
        _device = "cuda"
        print(f"✅ CUDA GPU found: {torch.cuda.get_device_name(0)}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024 ** 3:.1f} GB")
    else:
        _device = "cpu"
        print("⚠️  CUDA GPU not found, will use CPU (SLOW!)")

    return _device


def load_pipeline():
    """
    Loads Stable Diffusion XL Refiner pipeline.
    Model is downloaded on first run (~6GB), loaded from cache on subsequent runs.
    """
    global _pipeline

    if _pipeline is not None:
        print("✅ Pipeline loaded from cache.")
        return _pipeline

    print("\n" + "🔥" * 40)
    print("=== LOCAL GPU INFERENCE - MODEL LOADING ===")
    print("Model: Stable Diffusion XL Refiner 1.0")
    print("🔥" * 40 + "\n")

    device = get_device()

    # Model ID
    model_id = "stabilityai/stable-diffusion-xl-refiner-1.0"

    print(f"📥 1. Downloading/loading model: {model_id}")
    print("   ⏳ First run: ~5-10 minutes (6GB download)")
    print("   ⚡ Subsequent runs: ~10-20 seconds (cache)")

    try:
        # Load pipeline
        _pipeline = StableDiffusionXLImg2ImgPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            use_safetensors=True,
            variant="fp16" if device == "cuda" else None
        )

        # Move to GPU
        _pipeline = _pipeline.to(device)

        # 6GB VRAM optimizations
        if device == "cuda":
            print(f"⚙️  2. Applying GPU optimizations...")

            # Attention slicing (memory saving)
            _pipeline.enable_attention_slicing(slice_size="auto")
            print("   ✅ Attention slicing enabled")

            # VAE slicing (memory saving)
            _pipeline.enable_vae_slicing()
            print("   ✅ VAE slicing enabled")

            # Model offloading (if VRAM is insufficient)
            # _pipeline.enable_model_cpu_offload()  # Enable if needed

            print(f"   ✅ FP16 precision enabled")

        print("\n✨✨✨ Pipeline loaded successfully! ✨✨✨\n")
        return _pipeline

    except Exception as e:
        print(f"\n❌ Model loading error: {str(e)}")
        print("\nPossible solutions:")
        print("1. Check your internet connection")
        print("2. Check your disk space (~10GB required)")
        print("3. Verify CUDA is properly installed")
        raise


def transform_image(image_bytes, prompt="", strength=0.6, negative_prompt=""):
    """
    Transforms image using Local GPU.

    Args:
        image_bytes: Image byte data
        prompt: Transformation instruction
        strength: Transformation strength (0.0-1.0)
            - 0.0 = original image
            - 1.0 = completely new image
        negative_prompt: Unwanted features

    Returns:
        tuple: (success status, result image or error message)
    """

    print("\n" + "🔥" * 40)
    print("=== LOCAL GPU INFERENCE ===")
    print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    print(f"Prompt: {prompt[:60] if prompt else 'Not specified'}...")
    print(f"Strength: {strength}")
    print("🔥" * 40 + "\n")

    try:
        # 1. Load pipeline
        print("📦 1. Loading pipeline...")
        pipeline = load_pipeline()

        # 2. Convert image to PIL Image
        print(f"🖼️  2. Processing image...")
        init_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        print(f"   📐 Original size: {init_image.size}")

        # 3. Size check for SDXL (1024x1024 ideal)
        # Shrink large images (VRAM saving)
        max_size = 1024
        if max(init_image.size) > max_size:
            ratio = max_size / max(init_image.size)
            new_size = (int(init_image.width * ratio), int(init_image.height * ratio))
            init_image = init_image.resize(new_size, Image.Resampling.LANCZOS)
            print(f"   📐 Resize: {new_size}")

        # 4. Prompt preparation
        if not prompt:
            prompt = "high quality, detailed, improved, professional"

        print(f"📝 3. Parameters:")
        print(f"   Prompt: {prompt[:80]}...")
        print(f"   Negative: {negative_prompt[:80] if negative_prompt else 'None'}...")
        print(f"   Strength: {strength}")
        print(f"   Inference steps: 30")
        print(f"   Guidance scale: 7.5")

        # 5. Inference
        print("🚀 4. Starting GPU inference...")
        print("   ⏳ This process may take 10-30 seconds...")

        with torch.inference_mode():  # Memory optimization
            result = pipeline(
                prompt=prompt,
                image=init_image,
                strength=strength,  # 0.0-1.0
                negative_prompt=negative_prompt if negative_prompt else None,
                num_inference_steps=30,  # Quality (between 30-50)
                guidance_scale=7.5,  # Prompt adherence
                num_images_per_prompt=1
            )

        # 6. Result
        output_image = result.images[0]

        print(f"   📐 Result: {output_image.size}")
        print("\n✨✨✨ SUCCESS! Image transformed with Local GPU! ✨✨✨\n")

        # Clear VRAM
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return True, output_image

    except RuntimeError as e:
        error_msg = str(e)

        if "out of memory" in error_msg.lower():
            return False, "Insufficient GPU memory. Try a smaller image or lower the strength value."
        else:
            print(f"   ❌ RuntimeError: {error_msg[:200]}")
            return False, f"GPU error: {error_msg[:150]}"

    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Error: {type(e).__name__}")
        print(f"   📋 Message: {error_msg[:200]}")
        return False, f"Local inference error: {error_msg[:150]}"


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


def unload_pipeline():
    """Removes pipeline from memory (VRAM cleanup)."""
    global _pipeline

    if _pipeline is not None:
        del _pipeline
        _pipeline = None

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        print("🗑️  Pipeline removed from memory.")


# Show GPU info
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("LOCAL GPU INFERENCE - SYSTEM INFO")
    print("=" * 50 + "\n")

    device = get_device()

    if device == "cuda":
        print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024 ** 3:.1f} GB")
        print(f"🔢 CUDA Version: {torch.version.cuda}")
        print(f"🐍 PyTorch Version: {torch.__version__}")
        print("\n✅ System ready for local inference!\n")
    else:
        print("⚠️  CUDA GPU not found!")
        print("Local inference will run on CPU (very slow).\n")