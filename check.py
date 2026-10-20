from pathlib import Path
from model import analyze
import json

image_path = "test_images/circuit1.jpeg" if Path("test_images/circuit1.jpeg").exists() else "test_images/circuit1.jpg"

for backend in ["gemini", "ollama"]:
    print(f"\n=== {backend} ===")
    try:
        res = analyze(image_path, backend)
        print(json.dumps(res, indent=2))
    except Exception as e:
        print(f"Error running {backend}: {e}")
