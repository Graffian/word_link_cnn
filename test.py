import os
import cv2
import numpy as np
import tensorflow as tf

# Suppress TensorFlow terminal spam
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# ==========================================
# CONFIGURATION
# ==========================================
MODEL_PATH = "perfect_ocr_model.h5"
TEST_DIR = "test"
CNN_TARGET_SIZE = (64, 64)
CNN_CONFIDENCE_THRESHOLD = 0.45 

CLASS_NAMES = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
    'N', 'O', 'P', 'Q' ,'QU', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
]

def run_clean_folder_test():
    if not os.path.exists(TEST_DIR):
        print(f"[ERROR] Could not find the '{TEST_DIR}/' folder!")
        return

    print("Loading TensorFlow Vision Engine...")
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
    except Exception as e:
        print(f"[ERROR] Failed to load {MODEL_PATH}.")
        return

    # Grab all images and sort them alphanumerically
    image_files = sorted([f for f in os.listdir(TEST_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    
    if not image_files:
        print(f"[ERROR] No images found in '{TEST_DIR}/'!")
        return

    print(f"Found {len(image_files)} clean cropped images. Processing...\n")

    batch = []
    for img_name in image_files:
        img_path = os.path.join(TEST_DIR, img_name)
        
        # 1. Load in pure grayscale
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        
        # 2. NO SHAVING! Just resize directly to what the brain expects (64x64)
        resized = cv2.resize(img, CNN_TARGET_SIZE, interpolation=cv2.INTER_AREA)
        
        # 3. Add the color channel dimension so shape is (64, 64, 1)
        batch.append(np.expand_dims(resized, axis=-1))

    # Convert to standard Tensor format
    batch_tensor = np.array(batch, dtype=np.float32)

    # Predict all 16 instantly
    predictions = model.predict(batch_tensor, verbose=0)
    
    letters = []
    print("--- INDIVIDUAL TILE RESULTS ---")
    for i, (pred, file_name) in enumerate(zip(predictions, image_files)):
        class_idx = np.argmax(pred)
        confidence = pred[class_idx]
        
        predicted_char = CLASS_NAMES[class_idx]
        if confidence < CNN_CONFIDENCE_THRESHOLD:
            predicted_char = "?"
            
        letters.append(predicted_char)
        print(f"  {file_name:<15} -> {predicted_char.upper():>2}  ({confidence*100:>5.1f}%)")

    # Print the final 4x4 Grid
    if len(letters) == 16:
        print("\n--- FINAL 4x4 BOARD OUTPUT ---")
        rows = [" ".join(f"{letters[r*4+c].upper():>2}" for c in range(4)) for r in range(4)]
        print(f"  OCR[CNN]:   {rows[0]}")
        for row in rows[1:]:
            print(f"              {row}")

if __name__ == "__main__":
    run_clean_folder_test()