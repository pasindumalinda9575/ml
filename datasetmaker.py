import os
import shutil
import random

def prepare_dataset(src_root="Chopper/training_tiles", dest_root="ready_for_ai", split_ratio=0.9):
    train_dir = os.path.join(dest_root, "train")
    val_dir = os.path.join(dest_root, "val")
    
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    all_tiles = []

    # 1. Collect all paths and create unique names
    for artwork_folder in os.listdir(src_root):
        folder_path = os.path.join(src_root, artwork_folder)
        if not os.path.isdir(folder_path): continue
        
        for tile_name in os.listdir(folder_path):
            if tile_name.endswith(".png"):
                old_path = os.path.join(folder_path, tile_name)
                # Create a unique name like "Apples_tile_0.png"
                new_name = f"{artwork_folder}_{tile_name}"
                all_tiles.append((old_path, new_name))

    # 2. Shuffle and Split
    random.shuffle(all_tiles)
    split_idx = int(len(all_tiles) * split_ratio)
    train_files = all_tiles[:split_idx]
    val_files = all_tiles[split_idx:]

    # 3. Copy files
    print(f"Moving {len(train_files)} tiles to Train...")
    for old_p, new_n in train_files:
        shutil.copy2(old_p, os.path.join(train_dir, new_n))
        
    print(f"Moving {len(val_files)} tiles to Val...")
    for old_p, new_n in val_files:
        shutil.copy2(old_p, os.path.join(val_dir, new_n))

    print("Done! Your dataset is organized and split.")

if __name__ == "__main__":
    prepare_dataset()