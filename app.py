"""
AI Image Variations Generator - Professional UI
Image transformation interface with multi-platform AI integration.
"""

import streamlit as st
from PIL import Image
import io
import time  # for processing time
from datetime import datetime  # for timestamp
import random  # for seed generation

from config.settings import (
    MIN_STRENGTH, MAX_STRENGTH, DEFAULT_STRENGTH,
    MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS
)
from config.style_presets import ALL_STYLES
from utils.image_loader import validate_image, load_and_preprocess, resize_image, image_to_bytes
from utils.image_processor import create_side_by_side, get_image_info
from utils.comparison_ui import (
    display_before_after, create_download_button,
    display_image_info, show_transformation_settings,
    display_slider_comparison, display_image_grid
)


def load_css():
    """Loads custom CSS file."""
    try:
        with open("assets/style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def init_session_state():
    """Initialize session state."""
    if "transformed_images" not in st.session_state:
        st.session_state.transformed_images = []  # Changed to list
    if "original_image" not in st.session_state:
        st.session_state.original_image = None
    if "transformation_done" not in st.session_state:
        st.session_state.transformation_done = False
    if "platform_settings" not in st.session_state:
        st.session_state.platform_settings = {}
    if "last_metadata" not in st.session_state:
        st.session_state.last_metadata = {}  # For storing metadata


def render_header():
    """Page header."""
    st.title("AI Image Variations Generator")
    st.caption("Multi-Platform AI Support • Professional Image Variations")


def render_sidebar():
    """Left sidebar - collapsible sections."""

    st.sidebar.markdown("### ⚙️ Settings")

    # === PLATFORM SELECTION (Expandable) ===
    with st.sidebar.expander("🚀 Platform Selection", expanded=True):

        platform_options = {
            "💻 Local GPU": "RTX 3060 • FREE • Unlimited • Fastest",
            "🎨 Leonardo.ai": "Phoenix Model",
            "🤖 DeepAI": "Image Editor ",
            "🤗 Hugging Face": "SDXL Refiner",
            "🔮 Replicate": "Cloud GPU",
            "⚡ Stability AI": "SDXL 1.0"
        }

        platform = st.selectbox(
            "AI Platform:",
            options=list(platform_options.keys()),
            format_func=lambda x: f"{x}\n{platform_options[x]}",
            help="Select AI platform"
        )

        st.caption(f"ℹ️ {platform_options[platform]}")

    st.sidebar.markdown("---")

    # === TRANSFORMATION SETTINGS (Expandable) ===
    with st.sidebar.expander("✨ Transformation Settings", expanded=True):

        st.markdown("**Mode Selection:**")
        mode = st.radio(
            "mode_selection",
            ["🎨 Preset Style", "✏️ Custom Prompt"],
            help="Style or prompt",
            label_visibility="collapsed"
        )

        strength = st.slider(
            "Transformation Strength:",
            MIN_STRENGTH, MAX_STRENGTH, DEFAULT_STRENGTH, 0.05,
            help="Low=original, High=different"
        )

        # Strength info
        if strength < 0.5:
            st.info("💡 Minimal change")
        elif strength < 0.7:
            st.success("💡 Balanced (recommended)")
        else:
            st.warning("💡 Creative result")

        # NEW: Variation count slider
        st.markdown("---")
        num_variations = st.slider(
            "How many variations?",
            min_value=1,
            max_value=4,
            value=1,
            step=1,
            help="Generate multiple variations from the same image with different seeds"
        )

        if num_variations > 1:
            st.caption(f"💡 {num_variations} different variations will be generated")

    st.sidebar.markdown("---")

    # === STYLE/PROMPT SETTINGS ===
    style_config = None
    custom_prompt = ""
    negative_prompt = ""

    if "Preset Style" in mode:
        with st.sidebar.expander("🎨 Style Selection", expanded=True):
            category = st.selectbox("Category:", list(ALL_STYLES.keys()))
            style_name = st.selectbox("Style:", list(ALL_STYLES[category].keys()))
            style_config = ALL_STYLES[category][style_name]

            with st.expander("📋 Style Details"):
                st.caption(f"**Prompt:** {style_config['prompt'][:80]}...")
                st.caption(f"**Recommended Strength:** {style_config['strength']}")
    else:
        with st.sidebar.expander("✏️ Custom Prompt", expanded=True):
            custom_prompt = st.text_area(
                "Prompt:",
                placeholder="oil painting, vibrant colors...",
                height=100
            )
            negative_prompt = st.text_input(
                "Negative:",
                placeholder="blurry, low quality..."
            )

    st.sidebar.markdown("---")

    # === PLATFORM-SPECIFIC SETTINGS (Collapsed) ===
    with st.sidebar.expander("🔧 Platform Settings", expanded=False):

        if "Local" in platform:
            st.caption("**Local GPU Settings**")
            steps = st.slider("Inference Steps:", 20, 50, 30, 5)
            guidance = st.slider("Guidance Scale:", 5.0, 15.0, 7.5, 0.5)
            scheduler = st.selectbox("Scheduler:", ["DPMSolverMultistep", "EulerDiscrete", "DDIM"])

            st.session_state.platform_settings = {
                "steps": steps,
                "guidance_scale": guidance,
                "scheduler": scheduler
            }

        elif "Leonardo" in platform:
            st.caption("**Leonardo.ai Settings**")
            model = st.selectbox("Model:", [
                "Leonardo Phoenix (Best Quality)",
                "Leonardo Diffusion XL"
            ])
            steps = st.slider("Inference Steps:", 20, 50, 30, 5)
            guidance = st.slider("Guidance Scale:", 5.0, 10.0, 7.0, 0.5)

            st.session_state.platform_settings = {
                "model": "phoenix" if "Phoenix" in model else "diffusion_xl",
                "steps": steps,
                "guidance_scale": guidance
            }

        elif "DeepAI" in platform:
            st.caption("**DeepAI Settings**")
            st.info("ℹ️ DeepAI uses automatic settings. Strength is controlled via prompt.")

            st.session_state.platform_settings = {}

        elif "Hugging Face" in platform:
            st.caption("**Hugging Face Settings**")
            model = st.selectbox("Model:", [
                "stabilityai/stable-diffusion-xl-refiner-1.0",
                "stabilityai/stable-diffusion-2-1"
            ])

            st.session_state.platform_settings = {"model": model}

        elif "Stability AI" in platform:
            st.caption("**Stability AI Settings**")
            engine = st.selectbox("Engine:", ["stable-diffusion-xl-1024-v1-0"])
            steps = st.slider("Steps:", 30, 50, 50, 5)
            cfg = st.slider("CFG Scale:", 7.0, 15.0, 12.0, 0.5)

            st.session_state.platform_settings = {
                "engine": engine,
                "steps": steps,
                "cfg_scale": cfg
            }

        elif "Replicate" in platform:
            st.caption("**Replicate Settings**")
            version = st.text_input("Model Version:", "stability-ai/sdxl:...", disabled=True)

            st.session_state.platform_settings = {"version": version}

    return platform, mode, strength, style_config, custom_prompt, negative_prompt, num_variations


def render_main_content(platform):
    """Main content - single column, full width."""

    # Image upload
    st.markdown("### 📤 Upload Image")
    uploaded_file = st.file_uploader(
        "Drag and drop or select",
        type=ALLOWED_EXTENSIONS,
        label_visibility="collapsed"
    )

    if uploaded_file:
        is_valid, message = validate_image(uploaded_file)

        if not is_valid:
            st.error(f"❌ {message}")
            return None

        image = load_and_preprocess(uploaded_file)
        image = resize_image(image)
        st.session_state.original_image = image

        # Preview - centered
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="Uploaded Image", width="stretch")

        return image

    return None


def render_transform(image, platform, mode, strength, style_config, custom_prompt, negative_prompt, num_variations):
    """Transform button and processing."""

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("✨ Transform Image", type="primary", use_container_width=True):

            # Progress container
            progress_container = st.container()

            with progress_container:
                progress_bar = st.progress(0, text="🔄 Starting...")

                image_bytes = image_to_bytes(image)

                # Record processing time
                start_time = time.time()

                try:
                    # Platform import
                    progress_bar.progress(10, text=f"🔗 Connecting to {platform}...")

                    if "Hugging Face" in platform:
                        from utils import hf_api_handler as handler
                        platform_name = "Hugging Face"
                    elif "Leonardo" in platform:
                        from utils import leonardo_api_handler as handler
                        platform_name = "Leonardo.ai"
                    elif "DeepAI" in platform:
                        from utils import deepai_api_handler as handler
                        platform_name = "DeepAI"
                    elif "Replicate" in platform:
                        from utils import replicate_api_handler as handler
                        platform_name = "Replicate"
                    elif "Stability AI" in platform:
                        from utils import stability_ai_handler as handler
                        platform_name = "Stability AI"
                    elif "Local" in platform:
                        from utils import local_inference_handler as handler
                        platform_name = "Local GPU"
                    else:
                        st.error("❌ Invalid platform")
                        return

                    progress_bar.progress(20, text=f"🎨 Loading model...")

                    # Determine prompt and negative prompt
                    if "Preset Style" in mode and style_config:
                        used_prompt = style_config["prompt"]
                        used_negative_prompt = style_config.get("negative_prompt", "")
                    else:
                        used_prompt = custom_prompt
                        used_negative_prompt = negative_prompt

                    # Multiple variation generation
                    generated_images = []

                    for i in range(num_variations):
                        # Update progress
                        progress_percent = 20 + int((i / num_variations) * 70)
                        progress_text = f"⚡ Generating variation {i + 1}/{num_variations}..."
                        progress_bar.progress(progress_percent, text=progress_text)

                        # Random seed for each variation (some platforms don't support but no harm)
                        seed = random.randint(1, 2147483647)

                        # Transform operation
                        success, result = handler.transform_image(
                            image_bytes=image_bytes,
                            prompt=used_prompt,
                            strength=strength,
                            negative_prompt=used_negative_prompt
                        )

                        if success:
                            generated_images.append(result)
                        else:
                            # Cancel other variations on error
                            progress_bar.empty()
                            st.error(f"❌ Variation {i + 1} failed: {result}")
                            return

                    # Processing time
                    duration = time.time() - start_time

                    progress_bar.progress(100, text="✅ Completed!")

                    # Save to session state
                    st.session_state.transformed_images = generated_images
                    st.session_state.transformation_done = True

                    # Save metadata
                    st.session_state.last_metadata = {
                        "platform": platform_name,
                        "prompt": used_prompt,
                        "negative_prompt": used_negative_prompt,
                        "strength": strength,
                        "duration": duration,
                        "timestamp": datetime.now().strftime("%d %B %Y, %H:%M"),
                        "num_variations": num_variations
                    }

                    st.success(f"✅ Success! {num_variations} variation(s) generated. ({platform_name})")

                except Exception as e:
                    progress_bar.empty()
                    st.error(f"❌ Error: {str(e)}")


def render_results():
    """Result tabs."""

    if st.session_state.transformation_done and st.session_state.transformed_images:
        st.markdown("### 🖼️ Result")

        # Show metadata
        metadata = st.session_state.last_metadata
        show_transformation_settings(
            prompt=metadata.get("prompt", ""),
            strength=metadata.get("strength", 0),
            platform_name=metadata.get("platform"),
            duration=metadata.get("duration"),
            timestamp=metadata.get("timestamp"),
            negative_prompt=metadata.get("negative_prompt")
        )

        num_images = len(st.session_state.transformed_images)

        # If single variation, show as before
        if num_images == 1:
            tab1, tab2, tab3 = st.tabs(["📊 Side by Side", "🔍 Comparison", "💾 Download"])

            with tab1:
                display_before_after(
                    st.session_state.original_image,
                    st.session_state.transformed_images[0]
                )

            with tab2:
                display_slider_comparison(
                    st.session_state.original_image,
                    st.session_state.transformed_images[0]
                )

            with tab3:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**🎨 Transformed**")
                    st.image(st.session_state.transformed_images[0], width="stretch")
                    create_download_button(st.session_state.transformed_images[0], "transformed.png")

                with col2:
                    st.markdown("**📊 Comparison**")
                    combined = create_side_by_side(
                        st.session_state.original_image,
                        st.session_state.transformed_images[0]
                    )
                    st.image(combined, width="stretch")
                    create_download_button(combined, "comparison.png")

        # If multiple variations, show grid
        else:
            tab1, tab2 = st.tabs(["🎨 All Variations", "💾 Download"])

            with tab1:
                st.markdown(f"**{num_images} different variations generated:**")

                # Grid layout (2 columns)
                cols_per_row = 2
                for i in range(0, num_images, cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j in range(cols_per_row):
                        idx = i + j
                        if idx < num_images:
                            with cols[j]:
                                st.image(
                                    st.session_state.transformed_images[idx],
                                    caption=f"Variation {idx + 1}",
                                    width="stretch"
                                )

            with tab2:
                st.markdown("**Download each variation separately:**")

                # Download button for each variation
                cols_per_row = 2
                for i in range(0, num_images, cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j in range(cols_per_row):
                        idx = i + j
                        if idx < num_images:
                            with cols[j]:
                                st.image(
                                    st.session_state.transformed_images[idx],
                                    width="stretch"
                                )
                                create_download_button(
                                    st.session_state.transformed_images[idx],
                                    f"variation_{idx + 1}.png"
                                )


def main():
    """Main application."""

    st.set_page_config(
        page_title="AI Image Variations Generator",
        page_icon="🖼️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    load_css()
    init_session_state()
    render_header()

    # Sidebar settings (num_variations added)
    platform, mode, strength, style_config, custom_prompt, negative_prompt, num_variations = render_sidebar()

    # Main content
    uploaded_image = render_main_content(platform)

    if uploaded_image:
        render_transform(
            uploaded_image, platform, mode, strength,
            style_config, custom_prompt, negative_prompt, num_variations
        )
        render_results()

    # Footer
    st.markdown("---")
    st.caption("AI Image Variations Generator • Multi-Platform Support")


if __name__ == "__main__":
    main()