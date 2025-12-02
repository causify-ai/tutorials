#!/usr/bin/env python3
from PIL import Image
import os

img = Image.new('RGB', (100, 100), color='red')
path = os.path.join('examples', 'images')
os.makedirs(path, exist_ok=True)
img.save(os.path.join(path, 'red.png'))
