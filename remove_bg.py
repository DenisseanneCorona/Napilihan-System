from rembg import remove
from PIL import Image
import sys

input_path = "Frontend/images/logo.jpg"
output_path = "Frontend/images/logo.png"

try:
    with open(input_path, 'rb') as i:
        input_data = i.read()
        output_data = remove(input_data)
        with open(output_path, 'wb') as o:
            o.write(output_data)
    print(f"SUCCESS: Background removed. Saved to {output_path}")
except FileNotFoundError:
    print(f"ERROR: File not found: {input_path}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)
