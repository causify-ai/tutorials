#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from PIL import Image


def analyze(image_path: Path) -> str:
    image = Image.open(image_path).convert('RGB')
    width, height = image.size
    colors = image.getcolors(width * height)
    dominant_color = max(colors, key=lambda item: item[0])[1] if colors else (0, 0, 0)
    return f"Image {image_path.name} resolution {width}x{height}, dominant color RGB{dominant_color}."


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    args = parser.parse_args()
    caption = analyze(Path(args.input))
    print(json.dumps({"status": "ok", "caption": caption}))

if __name__ == '__main__':
    main()
