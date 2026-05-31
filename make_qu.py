import os
from PIL import Image, ImageDraw, ImageFont

def generate_qu_template():
    # Set to 640x640
    size = 640
    img = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(img)

    # Locate the native standard Windows Arial Bold font path
    windir = os.environ.get('WINDIR', 'C:\\Windows')
    font_path = os.path.join(windir, 'Fonts', 'arialbd.ttf')
    
    try:
        # Scaled up font size to match the 640x640 canvas
        font = ImageFont.truetype(font_path, 245)
    except IOError:
        print("  [Warning] Arial Bold not found at standard path, falling back to default.")
        font = ImageFont.load_default()

    text = "Qu"
    
    # Calculate text bounding box to center it horizontally
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    # Center text horizontally, shift up slightly to leave room for the 4 dots
    tx = (size - text_w) // 2 - bbox[0]
    ty = (size - text_h) // 2 - bbox[1] - 50 
    
    draw.text((tx, ty), text, fill="black", font=font)

    # Calculate exact alignment for the 4 dots underneath
    cx = size // 2
    cy = ty + text_h + 95  # Scaled drop below baseline
    
    dot_radius = 11      # Scaled up dot size
    dot_spacing = 38     # Scaled up spacing to match new width
    
    # Position 4 dots symmetrically around the center axis
    dot_positions = [
        cx - 1.5 * dot_spacing, 
        cx - 0.5 * dot_spacing, 
        cx + 0.5 * dot_spacing, 
        cx + 1.5 * dot_spacing
    ]
    
    for x in dot_positions:
        draw.ellipse([x - dot_radius, cy - dot_radius, x + dot_radius, cy + dot_radius], fill="black")

    # Save to your requested target directory
    target_dir = "./synthetic_bases"
    os.makedirs(target_dir, exist_ok=True)
    save_path = os.path.join(target_dir, "QU.png")
    
    img.save(save_path)
    print(f"✓ Generated clean 640x640 'Qu' template with 4 dots at: {save_path}")

if __name__ == "__main__":
    generate_qu_template()