# utils/file_io.py
import json

def load_resume(path="data/resume.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)