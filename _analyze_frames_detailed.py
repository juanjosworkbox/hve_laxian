"""Detailed analysis of second_row_enemy_animation.png to find frame boundaries."""
from PIL import Image

img = Image.open('samples/second_row_enemy_animation.png')
w, h = img.size
print(f'Image size: {w} x {h}')

# Print full pixel grid with detailed color info
print('\n--- Detailed Pixel Grid (R=Red, Y=Yellow, B=Blue, D=Dark, .=Transparent) ---')
for y in range(h):
    row = []
    for x in range(w):
        pixel = img.getpixel((x, y))
        r, g, b, a = pixel
        if a == 0:
            row.append('.')
        elif r > 180 and g < 100 and b < 100:
            row.append('R')  # Red body
        elif r > 180 and g > 180 and b < 100:
            row.append('Y')  # Yellow wing tips
        elif b > 150 and r < 100:
            row.append('B')  # Blue wing bases
        elif r < 50 and g < 50 and b < 50:
            row.append('D')  # Dark
        else:
            row.append(f'{r:02x}{g:02x}{b:02x}')
    print(f'Row {y:2d}: {" ".join(row)}')

# Analyze column by column for content gaps
print('\n--- Column Content Analysis ---')
col_content = []
for x in range(w):
    has_content = False
    for y in range(h):
        if img.getpixel((x, y))[3] > 0:
            has_content = True
            break
    col_content.append(has_content)

# Find transitions between content and gaps
print('Content columns (1=has content, 0=gap):')
content_str = ''.join(['1' if c else '0' for c in col_content])
print(content_str)

# Find contiguous content regions (potential frames)
print('\n--- Contiguous Content Regions ---')
in_region = False
region_start = 0
regions = []
for x in range(w):
    if col_content[x] and not in_region:
        in_region = True
        region_start = x
    elif not col_content[x] and in_region:
        in_region = False
        regions.append((region_start, x - 1))

if in_region:
    regions.append((region_start, w - 1))

print(f'Found {len(regions)} contiguous content regions:')
for i, (start, end) in enumerate(regions):
    print(f'  Region {i}: columns {start}-{end} (width {end - start + 1})')

# Since there are no gaps, let's look for vertical dividers
# Check each column for dominant color patterns
print('\n--- Per-Column Color Analysis ---')
for x in range(0, w, 2):
    colors_in_col = set()
    for y in range(h):
        pixel = img.getpixel((x, y))
        if pixel[3] > 0:
            colors_in_col.add(pixel[:3])
    if colors_in_col:
        print(f'  Col {x:2d}: {colors_in_col}')
