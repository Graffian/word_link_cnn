import random, os
from PIL import Image

for letter in ['R', 'W', 'B', 'V']:
    folder = f"dataset/{letter}"
    files = os.listdir(folder)
    sample = random.choice(files)
    Image.open(f"{folder}/{sample}").save(f"check_{letter}.png")