import os
import shutil
import random
import glob
from PIL import Image, ImageDraw, ImageOps, ImageEnhance

# ==========================================
# CONFIGURATION
# ==========================================
TARGET_SIZE   = (64, 64)
NUM_VARIANTS  = 500
OUTPUT_DIR    = "dataset"
SHAVE_PIXELS  = 65

# ── Set this to only regenerate specific letters ──
# Leave empty [] to regenerate ALL letters
REGENERATE_ONLY = []

# ── Letters that get extra variants + stronger augmentation due to visual ambiguity ──
HARD_LETTERS   = {'R', 'W', 'QU'}
HARD_VARIANTS  = 800   # more data for ambiguous letters

# ── QU needs less shave on the right to keep the U visible ──
QU_SHAVE_RIGHT  = 20

# ── R needs a deeper shave to kill corner triangle artifacts ──
R_SHAVE_PIXELS  = 85

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def augment_image(img, hard=False):
    """Rotation, shift, brightness and contrast variation."""
    # Rotation — wider range for hard letters
    angle = random.randint(-8, 8) if hard else random.randint(-3, 3)
    img = img.rotate(angle, fillcolor="white")

    # Shift
    dx = random.randint(-10, 10)
    dy = random.randint(-10, 10)
    img = ImageOps.expand(img, border=(abs(dx), abs(dy)), fill="white")
    left = abs(dx) - dx
    top  = abs(dy) - dy
    img  = img.crop((left, top, left + TARGET_SIZE[0], top + TARGET_SIZE[1]))

    # Brightness variation — simulates different tile backgrounds
    img = ImageEnhance.Brightness(img).enhance(random.uniform(0.7, 1.3))

    # Contrast variation
    img = ImageEnhance.Contrast(img).enhance(random.uniform(0.8, 1.4))

    return img

def draw_random_dots(img):
    """Draws 0 to 5 random dots at the bottom of the tile."""
    draw = ImageDraw.Draw(img)
    width, height = img.size
    num_dots = random.randint(0, 5)
    if num_dots > 0:
        dot_radius = 2
        y_position = height - 8
        total_width = (num_dots * dot_radius * 2) + ((num_dots - 1) * dot_radius)
        start_x = (width - total_width) // 2
        for i in range(num_dots):
            x_center = start_x + (i * dot_radius * 3) + dot_radius
            bbox = [x_center - dot_radius, y_position - dot_radius,
                    x_center + dot_radius, y_position + dot_radius]
            draw.ellipse(bbox, fill="black")
    return img

def shave_and_resize(img, letter):
    """Shaves borders and resizes with per-letter overrides."""
    w, h = img.size
    if letter == 'QU':
        left_shave  = SHAVE_PIXELS
        right_shave = QU_SHAVE_RIGHT
    elif letter == 'R':
        left_shave  = R_SHAVE_PIXELS
        right_shave = R_SHAVE_PIXELS
    else:
        left_shave  = SHAVE_PIXELS
        right_shave = SHAVE_PIXELS
    cropped = img.crop((left_shave, SHAVE_PIXELS, w - right_shave, h - 10))
    return cropped.resize(TARGET_SIZE)

def preview_base(letter, img):
    """Saves a preview so you can verify the base looks correct before training."""
    os.makedirs("preview", exist_ok=True)
    img.save(f"preview/{letter}_base_preview.png")

def should_process(letter):
    return not REGENERATE_ONLY or letter in REGENERATE_ONLY

def clear_and_remake(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

def load_all_bases(letter, base_dir):
    """Loads base_crops/LETTER.png + any base_crops/LETTER_2.png, LETTER_3.png etc."""
    pattern = os.path.join(base_dir, f"{letter}*.png")
    files   = sorted(glob.glob(pattern))
    bases   = []
    for f in files:
        try:
            img = Image.open(f).convert("RGB")
            img = shave_and_resize(img, letter)
            bases.append(img)
        except Exception as e:
            print(f"    Warning: could not load {f} — {e}")
    return bases

def generate_variants(bases, out_folder, letter, num_variants, synthetic=False):
    """Spreads num_variants evenly across all base crops."""
    hard       = letter in HARD_LETTERS
    per_base   = num_variants // len(bases)
    remainder  = num_variants % len(bases)
    count      = 0

    for b_idx, base_img in enumerate(bases):
        n = per_base + (1 if b_idx < remainder else 0)
        for i in range(n):
            img = base_img.copy()
            if synthetic:
                img = draw_random_dots(img)
            img = augment_image(img, hard=hard)
            img.save(f"{out_folder}/{letter}_{count}.png")
            count += 1

    return count

# ==========================================
# NORMAL LETTERS
# ==========================================
normal_letters = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M',
    'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'QU'
]

if REGENERATE_ONLY:
    print(f"Regenerating only: {REGENERATE_ONLY}\n")
else:
    print("Regenerating ALL letters\n")

print("Processing Normal Letters...")
for letter in normal_letters:
    if not should_process(letter):
        continue

    out_folder   = f"{OUTPUT_DIR}/{letter}"
    num_variants = HARD_VARIANTS if letter in HARD_LETTERS else NUM_VARIANTS

    clear_and_remake(out_folder)

    bases = load_all_bases(letter, "base_crops")
    if not bases:
        print(f"  ✗ {letter:<4} — no base crops found in base_crops/, skipping")
        continue

    # Preview first base so you can sanity check
    preview_base(letter, bases[0])

    count = generate_variants(bases, out_folder, letter, num_variants)
    src_note = f"{len(bases)} base crop(s)" if len(bases) > 1 else "1 base crop"
    print(f"  ✓ {letter:<4} — {count} variants from {src_note}")


# ==========================================
# SYNTHETIC LETTERS (J, Q, Z — dots added dynamically)
# ==========================================
synthetic_letters = ['J', 'Z']

print("\nProcessing Synthetic Letters...")
for letter in synthetic_letters:
    if not should_process(letter):
        continue

    out_folder   = f"{OUTPUT_DIR}/{letter}"
    num_variants = HARD_VARIANTS if letter in HARD_LETTERS else NUM_VARIANTS

    clear_and_remake(out_folder)

    bases = load_all_bases(letter, "synthetic_bases")
    if not bases:
        print(f"  ✗ {letter:<4} — no base crops found in synthetic_bases/, skipping")
        continue

    preview_base(letter, bases[0])

    count = generate_variants(bases, out_folder, letter, num_variants, synthetic=True)
    src_note = f"{len(bases)} base crop(s)" if len(bases) > 1 else "1 base crop"
    print(f"  ✓ {letter:<4} — {count} variants from {src_note}")

print("\nDone! Check preview/ folder before running train_model.py.")