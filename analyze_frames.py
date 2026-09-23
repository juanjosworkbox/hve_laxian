"""Detailed analysis of second row enemy animation PNG."""
from PIL import Image

img = Image.open('samples/second_row_enemy_animation.png')
w, h = img.size
print(f'Image size: {w} x {h}')

# Count distinct colored regions horizontally
print('\n--- Horizontal Analysis (Row 2 - middle of sprite) ---')
row2 = []
for x in range(w):
    pixel = img.getpixel((x, 2))
    r, g, b, a = pixel
    if a == 0:
        row2.append('.')
    elif r > 200 and g < 50 and b < 50:
        row2.append('R')  # Red
    elif r > 200 and g > 200 and b < 50:
        row2.append('Y')  # Yellow
    elif b > 150 and r < 50:
        row2.append('B')  # Blue
    else:
        row2.append(f'{r},{g},{b}')

# Find gaps (transparent or black columns)
print('Row 2 pattern:', ''.join(row2))

# Analyze frame boundaries by finding transparent columns
print('\n--- Frame Boundary Detection ---')
for x in range(w):
    col_has_color = False
    for y in range(h):
        pixel = img.getpixel((x, y))
        r, g, b, a = pixel
        if a > 0 and r > 50 and g < 100 and b < 100:  # Red-ish
            col_has_color = True
            break
        if a > 0 and r > 200 and g > 200 and b < 50:  # Yellow
            col_has_color = True
            break
    if col_has_color:
        print(f'Column {x}: has red/yellow content')
