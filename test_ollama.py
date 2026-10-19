from pathlib import Path
import ollama

BASE_DIR = Path(__file__).resolve().parent.parent

prompt_path = BASE_DIR / "prompt.txt"
image_path = BASE_DIR / "test_images" / "circuit1.jpeg"

prompt = prompt_path.read_text()

response = ollama.chat(
    model="gemma4:latest",
    messages=[{
        "role": "user",
        "content": prompt,
        "images": [str(image_path)],
    }],
    options={"temperature": 0 ,"num_ctx": 8192},
)

print(response["message"]["content"])