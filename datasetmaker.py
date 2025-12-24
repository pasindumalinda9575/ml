import os
import shutil
import random

def prepare_dataset(src_root="chopper/training_tiles", dest_root="ready_for_ai", split_ratio=0.9, repeats=20):
    # Kohya expects: ready_for_ai / img / 20_halftone / images+txt
    train_img_dir = os.path.join(dest_root, "img", f"{repeats}_halftone")
    val_dir = os.path.join(dest_root, "val_holdout") # Kept aside for manual testing
    
    os.makedirs(train_img_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    all_pairs = []

    # 1. Collect pairs (PNG + TXT)
    for artwork_folder in os.listdir(src_root):
        folder_path = os.path.join(src_root, artwork_folder)
        if not os.path.isdir(folder_path): continue
        
        for file in os.listdir(folder_path):
            if file.endswith(".png"):
                base_name = os.path.splitext(file)[0]
                img_path = os.path.join(folder_path, file)
                txt_path = os.path.join(folder_path, f"{base_name}.txt")
                
                # Only add if both exist
                if os.path.exists(txt_path):
                    new_name = f"{artwork_folder}_{base_name}"
                    all_pairs.append((img_path, txt_path, new_name))

    # 2. Shuffle and Split
    random.seed(42) # Keeps the split the same every time you run it
    random.shuffle(all_pairs)
    split_idx = int(len(all_pairs) * split_ratio)
    train_set = all_pairs[:split_idx]
    val_set = all_pairs[split_idx:]

    # 3. Copy files (PNG + TXT together)
    print(f"Moving {len(train_set)} pairs to Kohya Training folder...")
    for img_p, txt_p, new_n in train_set:
        shutil.copy2(img_p, os.path.join(train_img_dir, f"{new_n}.png"))
        shutil.copy2(txt_p, os.path.join(train_img_dir, f"{new_n}.txt"))
        
    print(f"Moving {len(val_set)} pairs to Holdout folder...")
    for img_p, txt_p, new_n in val_set:
        shutil.copy2(img_p, os.path.join(val_dir, f"{new_n}.png"))
        shutil.copy2(txt_p, os.path.join(val_dir, f"{new_n}.txt"))

    print("\n--- DONE ---")
    print(f"KOHYA SETTING: Point your 'Image Folder' to: {os.path.abspath(os.path.join(dest_root, 'img'))}")

if __name__ == "__main__":
    prepare_dataset()
