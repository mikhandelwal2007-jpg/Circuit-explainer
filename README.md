# ⚡ Circuit & Diagram Explainer

An AI-powered electronics and electromagnetics tutor that reverse-engineers schematics, identifies components, flags design flaws/ambiguities, and generates engineering practice questions. Powered by **Gemma 4** with both Cloud and 100% Offline Local inference modes.

---

## 🌟 Features

- **Multi-Source Diagram Input**:
  - 📋 **Paste from Clipboard**: Take a screenshot and paste directly (`Cmd+Shift+4` or `Win+Shift+S`).
  - 📁 **File Upload**: Drag and drop PNG, JPG, or WEBP schematics.
  - ⚡ **Preset Samples**: Instant 1-click testing with a classic 741 Op-Amp transistor schematic.
- **Circuit Reverse-Engineering**:
  - Automatically identifies circuit topology (e.g., Op-Amp internal schematics, active filters, differential pairs).
  - Recognizes individual electrical symbols (BJTs, Miller compensation capacitors, feedback networks, offset null pins).
  - Traces inter-stage routing and biasing networks.
- **Diagnostic Risk & Health Audit**:
  - Flags missing voltage supply rails, blurriness, and ambiguous connections with confidence ratings (High / Medium / Low).
- **Undergraduate Engineering Tutoring**:
  - Generates 3 level-progressing practice questions with step-by-step worked solutions.
- **Hybrid Inference Switch**:
  - **Cloud**: Google AI Studio / Gemini API / OpenRouter (`gemma-4-31b-it` / `gemini-3.8-flash`).
  - **Local (100% Offline)**: Ollama (`gemma4:latest`).
- **Export Reports**: Download full analysis in JSON or Markdown format.

---

## 🚀 Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/mikhandelwal2007-jpg/Circuit-explainer.git
cd Circuit-explainer
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory:
```dotenv
# Cloud API Key (Google AI Studio or OpenRouter)
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.8-flash

# Local Ollama Model
OLLAMA_MODEL=gemma4:latest
BACKEND=gemini
```

### 4. Run the Streamlit App
```bash
streamlit run app.py
```

---

## 🏗️ Project Structure

```
Circuit-explainer/
├── app.py              # Streamlit interactive UI with scanner animation
├── model.py            # Unified backend router (Google AI Studio, OpenRouter, Ollama)
├── prompt.txt          # Electronics tutor prompt
├── check.py            # CLI verification script for both backends
├── requirements.txt    # Production dependencies
├── .gitignore          # Ignores .env, venv/, and build artifacts
├── LICENSE             # MIT License
└── test_images/        # Sample circuits (741 Op-Amp schematic, etc.)
```

---

## 📜 License
MIT License. See [LICENSE](LICENSE) for details.
