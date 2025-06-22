from PIL import Image, ImageDraw

photo_path = "passport_photo.jpg"
output_pdf = "passport_layout.pdf"

# Indian passport photo size at 300 DPI (3.5 × 4.5 cm)
passport_px = (413, 531)
border = 20  # white border around photo
final_photo_size = (passport_px[0] + 2 * border, passport_px[1] + 2 * border)

# 4x6 inch photo paper = 1200 × 1800 px
layout_size = (1200, 1800)
layout = Image.new("RGB", layout_size, "white")
draw = ImageDraw.Draw(layout)

# Load and crop to 3.5:4.5 portrait aspect ratio
img = Image.open(photo_path)
aspect_target = passport_px[0] / passport_px[1]
img_aspect = img.width / img.height

if img_aspect > aspect_target:
    # crop width
    new_width = int(img.height * aspect_target)
    left = (img.width - new_width) // 2
    img = img.crop((left, 0, left + new_width, img.height))
else:
    # crop height
    new_height = int(img.width / aspect_target)
    top = (img.height - new_height) // 2
    img = img.crop((0, top, img.width, top + new_height))

# Resize and add border
resized = img.resize(passport_px)
framed = Image.new("RGB", final_photo_size, "white")
framed.paste(resized, (border, border))

# Arrange 2 rows × 3 columns
rows, cols = 2, 3
x_spacing = (layout_size[0] - (cols * final_photo_size[0])) // (cols + 1)
y_spacing = (layout_size[1] - (rows * final_photo_size[1])) // (rows + 1)

for row in range(rows):
    for col in range(cols):
        x = x_spacing + col * (final_photo_size[0] + x_spacing)
        y = y_spacing + row * (final_photo_size[1] + y_spacing)
        layout.paste(framed, (x, y))
        draw.rectangle([x, y, x + final_photo_size[0], y + final_photo_size[1]], outline=(200, 200, 200), width=2)

layout.save(output_pdf, "PDF", resolution=300.0)
print("✅ Output saved: passport_layout.pdf with 2x3 side-by-side layout.")


# This script generates a passport layout with a specified photo size and saves it as a PDF.
# Ensure you have the Pillow library installed to run this script.
# You can install it using: pip install Pillow
# Adjust the photo_path and output_pdf variables as needed.
# The layout consists of 3 rows and 2 columns of passport photos with specified spacing.
# The final PDF will be saved in the current working directory.