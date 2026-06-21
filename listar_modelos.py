import json
from pathlib import Path
import google.generativeai as genai

cfg_path = Path(__file__).parent / "config.json"
api_key = json.loads(cfg_path.read_text(encoding="utf-8")).get("api_key", "")

if not api_key:
    print("No se encontró API key en config.json")
    exit(1)

genai.configure(api_key=api_key)

print("Modelos disponibles con tu API key:\n")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(f"  {m.name}")
