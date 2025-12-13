from PIL import Image
import os

def remove_white_bg(img_path):
    try:
        img = Image.open(img_path).convert("RGBA")
        datas = img.getdata()
        
        new_data = []
        for item in datas:
            # Change all white (also shades of whites)
            # Find all pixels that are "close" to white
            if item[0] > 200 and item[1] > 200 and item[2] > 200:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        
        img.putdata(new_data)
        img.save(img_path, "PNG")
        print(f"Processed: {img_path}")
    except Exception as e:
        print(f"Error processing {img_path}: {e}")

logo_dir = "assets/logos"
if not os.path.exists(logo_dir):
    print("Logo directory not found!")
    exit()

for filename in os.listdir(logo_dir):
    if filename.endswith(".png"):
        remove_white_bg(os.path.join(logo_dir, filename))
