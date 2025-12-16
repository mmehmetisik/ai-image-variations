"""
Comparison UI components for Streamlit.
Before/after views and image selection tools.
"""

import streamlit as st  # web UI framework
from PIL import Image  # for image processing
import io  # for byte stream operations
import base64  # for base64 encoding


def display_before_after(original, transformed):
    """Displays original and transformed images side by side."""

    col1, col2 = st.columns(2)  # create two-column layout

    with col1:  # left column
        st.markdown("**📷 Original**")  # title
        st.image(original, width="stretch")  # fit image

    with col2:  # right column
        st.markdown("**🎨 Transformed**")
        st.image(transformed, width="stretch")


def display_slider_comparison(original, transformed):
    """
    REAL Before/After slider - splits image with PIL + adds vertical line.
    Controlled with Streamlit slider, INSTANT update.
    """

    st.markdown("### 🔍 Interactive Comparison")
    st.markdown("*Move the slider - slide right to see transformed, slide left to see original*")

    # Resize images to same dimensions
    orig_width, orig_height = original.size
    trans_resized = transformed.resize((orig_width, orig_height), Image.Resampling.LANCZOS)

    # Slider (0-100 range)
    split_position = st.slider(
        "⬅️ Original | Transformed ➡️",
        min_value=0,
        max_value=100,
        value=50,
        step=1,
        label_visibility="collapsed"
    )

    # Convert split point to pixels
    split_pixel = int((split_position / 100) * orig_width)

    # Create new image
    combined = Image.new('RGB', (orig_width, orig_height))

    # Get left part from original (from 0 to split_pixel)
    left_part = original.crop((0, 0, split_pixel, orig_height))
    combined.paste(left_part, (0, 0))

    # Get right part from transformed (from split_pixel to end)
    right_part = trans_resized.crop((split_pixel, 0, orig_width, orig_height))
    combined.paste(right_part, (split_pixel, 0))

    # ADD WHITE VERTICAL LINE (5 pixels wide)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(combined)
    line_width = 5
    draw.rectangle(
        [(split_pixel - line_width // 2, 0), (split_pixel + line_width // 2, orig_height)],
        fill='white'
    )

    # Display image
    st.image(combined, width="stretch")

    # Info
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.caption(f"📷 Original: {100 - split_position}%")
    with col2:
        st.caption(f"📍 Split point: {split_position}%")
    with col3:
        st.caption(f"🎨 Transformed: {split_position}%")


def display_image_grid(images, captions=None):
    """Displays images in a grid layout."""

    if not images:  # if list is empty
        st.warning("No images to display.")
        return

    num_images = len(images)  # number of images
    columns = min(num_images, 4)  # maximum 4 columns
    cols = st.columns(columns)  # create columns

    for idx, img in enumerate(images):  # place each image with loop
        col_idx = idx % columns  # which column it goes to
        caption = captions[idx] if captions else f"Variation {idx + 1}"  # title
        with cols[col_idx]:
            st.image(img, caption=caption, width="stretch")


def create_download_button(image, filename="transformed_image.png"):
    """Creates an image download button."""

    buffer = io.BytesIO()  # create buffer in memory
    image.save(buffer, format="PNG")  # save image as PNG to buffer
    buffer.seek(0)  # go to buffer start

    st.download_button(
        label="📥 Download Image",  # button text
        data=buffer,  # data to download
        file_name=filename,  # file name
        mime="image/png"  # file type
    )


def display_image_info(image_info):
    """Displays image metadata information."""

    st.markdown("**📊 Image Information**")

    col1, col2, col3 = st.columns(3)  # three-column info boxes

    with col1:
        st.metric("Size", f"{image_info['width']}x{image_info['height']}")  # pixel size
    with col2:
        st.metric("Format", image_info['mode'])  # color mode
    with col3:
        st.metric("File", f"{image_info['size_kb']:.1f} KB")  # file size


def show_transformation_settings(prompt, strength, platform_name=None, duration=None, timestamp=None,
                                 negative_prompt=None):
    """
    Displays the transformation settings used.

    Args:
        prompt: The positive prompt used
        strength: Transformation strength
        platform_name: Which platform was used (e.g., "Hugging Face")
        duration: Processing time (in seconds)
        timestamp: Creation time (string)
        negative_prompt: The negative prompt used
    """

    with st.expander("⚙️ Settings Used", expanded=False):  # collapsible panel

        # Platform info
        if platform_name:
            st.write(f"**🚀 Platform:** {platform_name}")

        # Prompt info
        st.write(f"**📝 Prompt:** {prompt if prompt else 'Not specified'}")

        if negative_prompt:
            st.write(f"**🚫 Negative Prompt:** {negative_prompt[:100]}{'...' if len(negative_prompt) > 100 else ''}")

        st.write(f"**⚡ Strength:** {strength}")

        # Processing info
        if duration is not None:
            st.write(f"**⏱️ Processing Time:** {duration:.2f} seconds")

        if timestamp:
            st.write(f"**🕐 Created:** {timestamp}")


def select_best_variation(images):
    """Allows user to select their favorite variation."""

    if not images or len(images) < 2:  # need at least 2 images
        return None

    st.markdown("**⭐ Select your favorite variation:**")

    options = [f"Variation {i + 1}" for i in range(len(images))]  # option list
    selected = st.radio("Selection:", options, horizontal=True)  # horizontal radio buttons

    selected_idx = options.index(selected)  # selected index
    return images[selected_idx]  # return selected image