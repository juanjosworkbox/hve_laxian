"""Detailed pixel analysis of second row enemy animation PNG."""
from PIL import Image

img = Image.open('samples/second_row_enemy_animation.png')
w, h = img.size
print(f'Image size: {w} x {h}')
print()

# Print all non-transparent pixels for each row
for y in range(h):
    print(f'Row {y}:')
    for x in range(w):
        pixel = img.getpixel((x, y))
        r, g, b, a = pixel
        if a > 0:
            print(f'  ({x},{y}): RGB={pixel}')
    print()

# Try to identify distinct frames by finding contiguous colored regions
print('\n--- Frame Detection ---')
# For each row, find contiguous regions of non-transparent pixels
for y in [2, 3, 4]:  # Check middle rows
    print(f'Row {y} regions:')
    in_region = False
    region_start = 0
    for x in range(w):
        pixel = img.getpixel((x, y))
        if pixel[3] > 0 and not in_region:
            in_region = True
            region_start = x
        elif pixel[3] == 0 and in_region:
            in_region = False
            print(f'  Region: cols {region_start}-{x-1} (width {x-region_start})')
    if in_region:
        print(f'  Region: cols {region_start}-{w-1} (width {w-region_start})')
