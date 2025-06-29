"""
Passport Photo Layout Generator

This script takes a source image, crops it to the standard Indian passport photo
aspect ratio (3.5:4.5), and arranges it in a 3x2 grid on a 4x6 inch
photo paper layout. The final output is a 300 DPI PDF file ready for printing.

Usage:
    python generate_passport_layout_v2.py <input_photo_path> <output_pdf_path>

Example:
    python generate_passport_layout_v2.py my_photo.jpg passport_sheet.pdf
"""

import argparse
import sys
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw

# --- Constants ---
# Standard Indian passport photo size (3.5cm x 4.5cm) at 300 DPI
PASSPORT_PHOTO_PX: Tuple[int, int] = (413, 531)
ASPECT_RATIO: float = PASSPORT_PHOTO_PX[0] / PASSPORT_PHOTO_PX[1]

# 4x6 inch photo paper at 300 DPI
LAYOUT_PX: Tuple[int, int] = (1200, 1800)
PDF_RESOLUTION: float = 300.0

# Layout configuration
GRID_ROWS: int = 3
GRID_COLS: int = 2
PHOTO_BORDER_PX: int = 20  # White border around each photo
GUIDELINE_COLOR: str = "grey"
GUIDELINE_WIDTH: int = 2
DOTTED_LINE_GAP: int = 10

def draw_dotted_line(draw: ImageDraw.Draw, start_xy: Tuple[int, int], end_xy: Tuple[int, int], fill: str, width: int, gap: int):
    """Draws a dotted line on the image."""
    dist_x = end_xy[0] - start_xy[0]
    dist_y = end_xy[1] - start_xy[1]
    length = (dist_x**2 + dist_y**2)**0.5
    num_dots = int(length / (width + gap))
    for i in range(num_dots):
        start_pos = (start_xy[0] + (dist_x * i / num_dots), start_xy[1] + (dist_y * i / num_dots))
        end_pos = (start_xy[0] + (dist_x * (i + 0.5) / num_dots), start_xy[1] + (dist_y * (i + 0.5) / num_dots))
        draw.line([start_pos, end_pos], fill=fill, width=width)

def draw_dotted_rectangle(draw: ImageDraw.Draw, xy: list, outline: str, width: int, gap: int):
    """Draws a dotted rectangle."""
    x0, y0, x1, y1 = xy
    draw_dotted_line(draw, (x0, y0), (x1, y0), outline, width, gap)
    draw_dotted_line(draw, (x1, y0), (x1, y1), outline, width, gap)
    draw_dotted_line(draw, (x1, y1), (x0, y1), outline, width, gap)
    draw_dotted_line(draw, (x0, y1), (x0, y0), outline, width, gap)


def crop_image_to_aspect_ratio(img: Image.Image, aspect_target: float) -> Image.Image:
    """
    Crops the image to a target aspect ratio, cutting from the center.

    Args:
        img: The source PIL Image object.
        aspect_target: The target aspect ratio (width / height).

    Returns:
        The cropped PIL Image object.
    """
    img_aspect = img.width / img.height

    if img_aspect > aspect_target:
        # Image is wider than target, crop width
        new_width = int(img.height * aspect_target)
        left = (img.width - new_width) // 2
        return img.crop((left, 0, left + new_width, img.height))
    else:
        # Image is taller than target, crop height
        new_height = int(img.width / aspect_target)
        top = (img.height - new_height) // 2
        return img.crop((0, top, img.width, top + new_height))


def create_photo_layout(
    photo_path: Path, output_path: Path
) -> None:
    """
    Generates and saves a passport photo layout PDF.

    Args:
        photo_path: Path to the source passport photo.
        output_path: Path to save the output PDF file.
    """
    try:
        source_img = Image.open(photo_path)
    except FileNotFoundError:
        print(f"❌ Error: Input file not found at '{photo_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: Could not open image file. Reason: {e}")
        sys.exit(1)

    print("📷 Cropping image to 3.5:4.5 aspect ratio...")
    cropped_img = crop_image_to_aspect_ratio(source_img, ASPECT_RATIO)

    # Resize to final passport photo pixel dimensions
    resized_img = cropped_img.resize(PASSPORT_PHOTO_PX, Image.Resampling.LANCZOS)

    # Create a new image with a white border
    final_photo_size = (
        PASSPORT_PHOTO_PX[0] + 2 * PHOTO_BORDER_PX,
        PASSPORT_PHOTO_PX[1] + 2 * PHOTO_BORDER_PX,
    )
    framed_photo = Image.new("RGB", final_photo_size, "white")
    framed_photo.paste(resized_img, (PHOTO_BORDER_PX, PHOTO_BORDER_PX))

    # Create the 4x6 layout canvas
    layout = Image.new("RGB", LAYOUT_PX, "white")
    draw = ImageDraw.Draw(layout)
    print(f"📄 Creating {GRID_ROWS}x{GRID_COLS} layout on a 4x6 inch canvas...")

    # Calculate the total size of the photo block
    block_width = GRID_COLS * final_photo_size[0]
    block_height = GRID_ROWS * final_photo_size[1]

    # Calculate starting coordinates to center the block
    start_x = (LAYOUT_PX[0] - block_width) // 2
    start_y = (LAYOUT_PX[1] - block_height) // 2

    # Paste photos onto the layout and draw cutting guidelines
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x = start_x + col * final_photo_size[0]
            y = start_y + row * final_photo_size[1]
            layout.paste(framed_photo, (x, y))
            # Draw cutting guidelines around the framed photo
            draw_dotted_rectangle(
                draw,
                [x, y, x + final_photo_size[0], y + final_photo_size[1]],
                outline=GUIDELINE_COLOR,
                width=GUIDELINE_WIDTH,
                gap=DOTTED_LINE_GAP
            )

    try:
        layout.save(
            output_path, "PDF", resolution=PDF_RESOLUTION, save_all=True
        )
        print(f"✅ Success! Output saved to: {output_path}")
    except Exception as e:
        print(f"❌ Error: Could not save PDF file. Reason: {e}")
        sys.exit(1)


def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(
        description="Generates a printable 4x6 passport photo layout.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Example:
  python %(prog)s passport_photo.jpg passport_layout.pdf
"""
    )
    parser.add_argument(
        "input_photo",
        type=Path,
        help="Path to the source passport photo (e.g., my_photo.jpg).",
    )
    parser.add_argument(
        "output_pdf",
        type=Path,
        help="Path to save the output PDF file (e.g., passport_sheet.pdf).",
    )
    args = parser.parse_args()

    create_photo_layout(args.input_photo, args.output_pdf)


if __name__ == "__main__":
    main()
