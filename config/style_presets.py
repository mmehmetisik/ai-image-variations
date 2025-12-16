"""
Pre-made style templates and transformation settings.
Strategy: Short directive positive prompt + Long specific negative prompt
This approach ensures the model preserves the original composition.
"""

# === Artistic Styles ===
ARTISTIC_STYLES = {
    "Oil Painting": {
        "prompt": "Apply classical oil painting style with visible brush strokes and canvas texture",
        "strength": 0.40,
        "negative_prompt": "photograph, photorealistic, photo, digital art, flat colors, no texture, smooth surface, different composition, changed layout, altered subject, moved elements, repositioned objects, deformed, distorted, blurry, low quality, bad anatomy, disfigured, ugly, artificial, plastic look, oversaturated"
    },
    "Watercolor": {
        "prompt": "Apply watercolor painting style with soft flowing colors and paper texture",
        "strength": 0.35,
        "negative_prompt": "photograph, photo, sharp edges, hard lines, digital, flat, no texture, different composition, changed layout, altered pose, moved subject, repositioned elements, deformed, distorted, blurry, low quality, artificial, oversaturated, dark, muddy colors"
    },
    "Sketch": {
        "prompt": "Apply pencil sketch style with hand-drawn lines and crosshatching",
        "strength": 0.45,
        "negative_prompt": "color, colored, painted, photograph, photo, digital, smooth, no lines, no texture, different composition, changed layout, altered subject, moved elements, deformed anatomy, distorted features, blurry, low quality, messy, unclear lines, smudged"
    },
    "Digital Art": {
        "prompt": "Apply modern digital art style with vibrant colors and smooth rendering",
        "strength": 0.38,
        "negative_prompt": "photograph, photo, traditional painting, old style, rough texture, grainy, different composition, changed layout, altered pose, moved subject, repositioned elements, deformed, distorted, blurry, low quality, bad anatomy, pixelated, compression artifacts"
    }
}

# === Photo Styles ===
PHOTO_STYLES = {
    "Vintage": {
        "prompt": "Apply vintage photo effect with retro color grading and subtle film grain",
        "strength": 0.25,
        "negative_prompt": "modern, digital, sharp, clean, oversaturated, vibrant, different composition, changed layout, altered subject, moved elements, repositioned objects, added objects, removed objects, deformed, distorted, blurry beyond vintage effect, low quality, artificial HDR"
    },
    "Black and White": {
        "prompt": "Convert to black and white photography with rich tonal range",
        "strength": 0.22,
        "negative_prompt": "color, colored, colorful, tinted, sepia beyond black and white, different composition, changed layout, altered subject, moved elements, repositioned objects, added elements, removed elements, deformed, distorted, low contrast, muddy, blurry, low quality"
    },
    "HDR": {
        "prompt": "Apply HDR photography effect with enhanced dynamic range and vivid details",
        "strength": 0.20,
        "negative_prompt": "flat, dull, underexposed, overexposed, overprocessed, unrealistic, cartoon, painted, different composition, changed layout, altered subject, moved elements, repositioned objects, halos, artifacts, deformed, distorted, blurry, low quality, fake looking"
    },
    "Film Grain": {
        "prompt": "Apply 35mm film photography effect with natural grain texture and cinematic color",
        "strength": 0.25,
        "negative_prompt": "digital, clean, sharp, no grain, plastic look, oversaturated, different composition, changed layout, altered subject, moved elements, repositioned objects, deformed, distorted, excessive grain, noise, blurry beyond film aesthetic, low quality, artificial"
    }
}

# === Fantasy Styles ===
FANTASY_STYLES = {
    "Anime": {
        "prompt": "Apply anime art style with cel-shading and clean outlines",
        "strength": 0.35,
        "negative_prompt": "realistic photograph, photorealistic, photo, real life, 3D render, western cartoon, different composition, changed layout, altered pose, moved subject, repositioned elements, different character, changed face, deformed anatomy, distorted features, wrong proportions, extra limbs, missing limbs, blurry, low quality, bad anatomy, ugly, disfigured, malformed, mutation"
    },
    "Cartoon": {
        "prompt": "Apply cartoon illustration style with bold outlines and simplified shapes",
        "strength": 0.40,
        "negative_prompt": "realistic, photograph, photo, detailed, complex, textured, anime, different composition, changed layout, altered pose, moved subject, repositioned elements, different character, deformed anatomy, distorted features, wrong proportions, blurry, low quality, bad anatomy, ugly, messy lines, unclear"
    },
    "Comic Book": {
        "prompt": "Apply comic book art style with bold ink lines and vibrant colors",
        "strength": 0.38,
        "negative_prompt": "photograph, photo, realistic, soft, watercolor, no outlines, different composition, changed layout, altered pose, moved subject, repositioned elements, different scene, deformed anatomy, distorted features, wrong proportions, blurry, low quality, bad anatomy, messy, unclear lines, muddy colors"
    }
}

# === Combine all styles (for easy access in app.py) ===
ALL_STYLES = {
    "🎨 Artistic": ARTISTIC_STYLES,
    "📷 Photo": PHOTO_STYLES,
    "✨ Fantasy": FANTASY_STYLES
}