"""Analyze second row enemy animation PNG frames."""
from PIL import Image

img = Image.open('samples/second_row_enemy_animation.png')
w, h = img.size
print(f'Image size: {w} x {h}')
print(f'Mode: {img.mode}')

# Analyze each row
for y in range(h):
    row = []
    for x in range(w):
        pixel = img.getpixel((x, y))
        r, g, b, a = pixel
        if a == 0:
            row.append('.')
        elif r > 200 and g < 50 and b < 50:
            row.append('R')  # Red
        elif r < 50 and g < 50 and b < 50:
            row.append('B')  # Black
        elif r > 150 and g > 150 and b < 50:
            row.append('Y')  # Yellow
        else:
            row.append(f'({r},{g},{b})')
    print(f'Row {y}: {" ".join(row)}')

# Try to detect frame boundaries by looking for gaps
print('\n--- Frame Analysis ---')
# Check for vertical gaps (all black columns)
for x in range(w):
    col_has_content = False
    for y in range(h):
        pixel = img.getpixel((x, y))
        if pixel[3] > 0:  # Not transparent
            col_has_content = True
            break
    if not col_has_content:
        print(f'Column {x} appears to be a gap')
