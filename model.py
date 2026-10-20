import os, json, re, base64
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
PROMPT = (BASE_DIR / "prompt.txt").read_text()


def encode_image(image_path: str) -> str:
    path = Path(image_path).resolve()
    mime = "image/jpeg"
    suffix = path.suffix.lower()
    if suffix == ".png":
        mime = "image/png"
    elif suffix == ".webp":
        mime = "image/webp"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def ask_cloud_openrouter(image_path: str) -> str:
    from openai import OpenAI
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("GEMINI_API_KEY")
    model_name = os.environ.get("OPENROUTER_MODEL", "google/gemma-4-31b-it")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    data_url = encode_image(image_path)
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        temperature=0,
    )
    return response.choices[0].message.content


def ask_gemini_native(image_path: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"))
    img = Image.open(str(Path(image_path).resolve()))
    return model.generate_content([PROMPT, img]).text


def ask_gemini(image_path: str) -> str:
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if gemini_key and not gemini_key.startswith("sk-or-"):
        return ask_gemini_native(image_path)
    if os.environ.get("OPENROUTER_API_KEY") or gemini_key.startswith("sk-or-"):
        return ask_cloud_openrouter(image_path)
    return ask_gemini_native(image_path)


def ask_ollama(image_path: str) -> str:
    import ollama
    resolved_path = str(Path(image_path).resolve())
    response = ollama.chat(
        model=os.environ.get("OLLAMA_MODEL", "gemma4:latest"),
        messages=[{"role": "user", "content": PROMPT, "images": [resolved_path]}],
        options={"temperature": 0, "num_ctx": 8192},
    )
    return response["message"]["content"]


def parse_json(text: str) -> dict:
    """Extract and parse the model's JSON, handling thinking tokens or markdown fences."""
    # Try finding markdown json fence first
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try extracting outermost JSON object {...}
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = text[first_brace : last_brace + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def get_backend_info(backend: Optional[str] = None) -> dict:
    backend = (backend or os.getenv("BACKEND", "gemini")).lower()
    if backend in ["ollama", "local"]:
        return {
            "type": "Local",
            "provider": "Ollama (Offline)",
            "model": os.environ.get("OLLAMA_MODEL", "gemma4:latest"),
            "offline": True,
        }
    else:
        gemini_key = os.environ.get("GEMINI_API_KEY", "")
        if gemini_key and not gemini_key.startswith("sk-or-"):
            return {
                "type": "Cloud",
                "provider": "Google AI Studio",
                "model": os.environ.get("GEMINI_MODEL", "gemini-3.8-flash"),
                "offline": False,
            }
        return {
            "type": "Cloud",
            "provider": "OpenRouter",
            "model": os.environ.get("OPENROUTER_MODEL", "google/gemma-4-31b-it"),
            "offline": False,
        }


def analyze(image_path: str, backend: Optional[str] = None) -> dict:
    backend = (backend or os.getenv("BACKEND", "gemini")).lower()
    raw = ask_ollama(image_path) if backend in ["ollama", "local"] else ask_gemini(image_path)
    try:
        return parse_json(raw)
    except json.JSONDecodeError:
        return {"error": "Model did not return valid JSON", "raw": raw}

