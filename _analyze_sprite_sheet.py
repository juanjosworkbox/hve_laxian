"""Analyze second_row_enemy_animation.png pixel data."""
from PIL import Image

img = Image.open('samples/second_row_enemy_animation.png')
w, h = img.size
print(f'Image size: {w} x {h}')
print(f'Mode: {img.mode}')

# Collect unique colors
unique_colors = {}
for y in range(h):
    for x in range(w):
        pixel = img.getpixel((x, y))
        if pixel[3] > 0:  # Not transparent
            key = pixel[:3]
            unique_colors[key] = unique_colors.get(key, 0) + 1

print(f'\nUnique colors ({len(unique_colors)}):')
for color, count in sorted(unique_colors.items(), key=lambda x: -x[1]):
    print(f'  RGB{color}: {count} pixels')

# Print pixel grid with color codes
print('\n--- Pixel Grid ---')
for y in range(h):
    row = []
    for x in range(w):
        pixel = img.getpixel((x, y))
        if pixel[3] == 0:
            row.append('.')
        else:
            r, g, b = pixel[:3]
            if r > 150 and g < 100 and b < 100:
                row.append('R')  # Red body
            elif r > 150 and g > 150 and b < 100:
                row.append('Y')  # Yellow
            elif b > 150 and r < 100:
                row.append('B')  # Blue
            elif r < 50 and g < 50 and b < 50:
                row.append('D')  # Dark/Black
            else:
                row.append(f'{r:02x}')
    print(f'Row {y}: {" ".join(row)}')

# Detect frame boundaries - find columns that are all transparent
print('\n--- Frame Detection ---')
frame_cols = []
for x in range(w):
    has_content = False
    for y in range(h):
        if img.getpixel((x, y))[3] > 0:
            has_content = True
            break
    if has_content:
        frame_cols.append(x)

# Find contiguous regions
frames = []
current = []
for x in frame_cols:
    if current and x == current[-1] + 1:
        current.append(x)
    else:
        if current:
            frames.append(current)
        current = [x]
if current:
    frames.append(current)

print(f'Detected {len(frames)} frames:')
for i, frame in enumerate(frames):
    print(f'  Frame {i}: columns {frame[0]}-{frame[-1]} (width {len(frame)})')
