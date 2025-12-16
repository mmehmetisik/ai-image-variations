# 🖼️ AI Image Variations Generator

A powerful multi-platform AI image transformation tool with a professional Streamlit UI. Transform your images using various AI platforms including Local GPU, Leonardo.ai, DeepAI, Hugging Face, Replicate, and Stability AI.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![AI](https://img.shields.io/badge/AI-Multi--Platform-purple.svg)

## 📸 Demo

<img width="2546" height="1273" alt="Ekran görüntüsü 2025-12-17 003810" src="https://github.com/user-attachments/assets/831309de-88ed-4fbc-bdd5-051e3810886f" />


## ✨ Features

- **Multi-Platform Support**: Switch between 6 different AI platforms seamlessly
- **Local GPU Inference**: Free, unlimited processing with RTX 3060 or similar NVIDIA GPUs
- **Preset Styles**: 20+ ready-to-use artistic styles (Oil Painting, Watercolor, Anime, Cyberpunk, etc.)
- **Custom Prompts**: Full control with custom prompts and negative prompts
- **Multiple Variations**: Generate 1-4 variations from a single image
- **Side-by-Side Comparison**: Visual comparison tools with slider
- **Professional UI**: Clean, modern Streamlit interface with dark theme support
- **Easy Download**: Download transformed images and comparisons with one click

## 🚀 Supported Platforms

| Platform | Model | Cost | Speed | Quality |
|----------|-------|------|-------|---------|
| 💻 Local GPU | SDXL Refiner 1.0 | FREE | ⚡ Fastest | ⭐⭐⭐⭐⭐ |
| 🎨 Leonardo.ai | Phoenix | Credits | Fast | ⭐⭐⭐⭐⭐ |
| 🤖 DeepAI | Image Editor | $5/month | Fast | ⭐⭐⭐⭐ |
| 🤗 Hugging Face | SDXL Refiner | Free/Paid | Medium | ⭐⭐⭐⭐ |
| 🔮 Replicate | InstructPix2Pix | Pay-per-use | Medium | ⭐⭐⭐⭐ |
| ⚡ Stability AI | SDXL 1.0 | Credits | Fast | ⭐⭐⭐⭐⭐ |

## 📁 Project Structure
```
ai-image-variations/
├── 📁 assets/
│   ├── 📁 sample_images/      # Sample images for testing
│   └── 🎨 style.css           # Custom CSS styling
├── 📁 config/
│   ├── 🐍 settings.py         # Application settings
│   └── 🐍 style_presets.py    # Predefined style configurations
├── 📁 input_images/           # User input images (not tracked by git)
├── 📁 output_images/          # Generated outputs (not tracked by git)
├── 📁 utils/
│   ├── 🐍 comparison_ui.py    # UI comparison components
│   ├── 🐍 deepai_api_handler.py
│   ├── 🐍 hf_api_handler.py
│   ├── 🐍 image_loader.py     # Image loading utilities
│   ├── 🐍 image_processor.py  # Image processing functions
│   ├── 🐍 leonardo_api_handler.py
│   ├── 🐍 local_inference_handler.py
│   ├── 🐍 replicate_api_handler.py
│   └── 🐍 stability_ai_handler.py
├── 🐍 app.py                  # Main Streamlit application
├── 📄 requirements.txt        # Python dependencies
├── 🔐 .env                    # API keys (create from .env.example)
└── 🚫 .gitignore
```

> **Note**: `input_images/` and `output_images/` folders are excluded from git for privacy. Create them manually if needed for local file storage.

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- NVIDIA GPU with CUDA support (for Local GPU inference)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/mmehmetisik/ai-image-variations.git
cd ai-image-variations
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure API Keys

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
```env
HF_API_TOKEN=your_huggingface_token
DEEPAI_API_KEY=your_deepai_key
STABILITY_API_KEY=your_stability_key
LEONARDO_API_KEY=your_leonardo_key
REPLICATE_API_TOKEN=your_replicate_token
```

### Step 5: Run the Application
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage

1. **Select Platform**: Choose your preferred AI platform from the sidebar
2. **Upload Image**: Drag and drop or browse to select an image (PNG, JPG, JPEG)
3. **Choose Mode**: 
   - **Preset Style**: Select from 20+ predefined artistic styles
   - **Custom Prompt**: Enter your own transformation instructions
4. **Adjust Strength**: Control how much the image changes (0.3 = subtle, 0.9 = dramatic)
5. **Set Variations**: Choose how many variations to generate (1-4)
6. **Transform**: Click the "Transform Image" button
7. **Compare & Download**: View results, compare side-by-side, and download

## 🎨 Available Style Categories

- **Artistic**: Oil Painting, Watercolor, Impressionist, Pop Art
- **Modern**: Cyberpunk, Synthwave, Vaporwave, Glitch Art
- **Traditional**: Japanese Ukiyo-e, Chinese Ink Wash, Renaissance
- **Photography**: HDR, Vintage Film, Noir, Cinematic
- **Fantasy**: Ethereal, Dark Fantasy, Steampunk, Sci-Fi

## 🔑 Getting API Keys

| Platform | How to Get |
|----------|------------|
| Hugging Face | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| DeepAI | [deepai.org/dashboard](https://deepai.org/dashboard) |
| Stability AI | [platform.stability.ai](https://platform.stability.ai/) |
| Leonardo.ai | [leonardo.ai](https://leonardo.ai/) |
| Replicate | [replicate.com/account](https://replicate.com/account) |

## 🖥️ Local GPU Requirements

For free, unlimited local inference:

- **GPU**: NVIDIA with 6GB+ VRAM (RTX 3060, RTX 2060, etc.)
- **CUDA**: Version 11.8 or higher
- **RAM**: 16GB+ recommended
- **Storage**: ~10GB for model cache (first run downloads the model)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Mehmet Işık**

- 🐙 GitHub: [@mmehmetisik](https://github.com/mmehmetisik)
- 💼 LinkedIn: [Mehmet Işık](https://www.linkedin.com/in/mehmetisik4601/)
- 📊 Kaggle: [mehmetisik](https://www.kaggle.com/mehmetisik)

---

⭐ If you found this project useful, please consider giving it a star!
