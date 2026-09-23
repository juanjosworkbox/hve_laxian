"""Analyze the 4 frames from the second_row_enemy_animation.png sprite sheet."""
from PIL import Image

img = Image.open('samples/second_row_enemy_animation.png')
w, h = img.size

# The image is 58x8 with 4 frames of ~14px each (with some overlap/gaps)
# Let's look at the repeating pattern more carefully
# Based on the pixel grid, I can see 4 distinct patterns

# Let's extract each frame by analyzing color patterns
# Frame 1: columns 0-13, Frame 2: columns ~15-29, Frame 3: columns ~30-44, Frame 4: columns ~45-57

# Let me find the exact boundaries by looking at where each "shape" starts
# The key is to find where the red body pixel pattern shifts

# Let's look at row 2 (has the yellow wing tips) and row 3 (has the red body)
# to find frame boundaries

print("=== Row 2 (yellow wing tips row) ===")
for x in range(w):
    pixel = img.getpixel((x, 2))
    r, g, b, a = pixel
    if a > 0:
        if r > 180 and g > 180 and b < 100:
            print(f'{x:2d}: Y (yellow)', end=' ')
        elif r > 180 and g < 100 and b < 100:
            print(f'{x:2d}: R (red)', end=' ')
        elif b > 150 and r < 100:
            print(f'{x:2d}: B (blue)', end=' ')
        elif r < 50 and g < 50 and b < 50:
            print(f'{x:2d}: D (dark)', end=' ')
        else:
            print(f'{x:2d}: {r:02x}', end=' ')
    else:
        print(f'{x:2d}: . (transparent)', end=' ')
    if (x + 1) % 10 == 0:
        print()

print("\n\n=== Row 3 (red body row) ===")
for x in range(w):
    pixel = img.getpixel((x, 3))
    r, g, b, a = pixel
    if a > 0:
        if r > 180 and g < 100 and b < 100:
            print(f'{x:2d}: R (red)', end=' ')
        elif r > 180 and g > 180 and b < 100:
            print(f'{x:2d}: Y (yellow)', end=' ')
        elif b > 150 and r < 100:
            print(f'{x:2d}: B (blue)', end=' ')
        elif r < 50 and g < 50 and b < 50:
            print(f'{x:2d}: D (dark)', end=' ')
        else:
            print(f'{x:2d}: {r:02x}', end=' ')
    else:
        print(f'{x:2d}: . (transparent)', end=' ')
    if (x + 1) % 10 == 0:
        print()

# Count red pixels per column to find frame centers
print("\n=== Red pixel count per column (row 3) ===")
for x in range(w):
    pixel = img.getpixel((x, 3))
    r, g, b, a = pixel
    if a > 0 and r > 180 and g < 100 and b < 100:
        print(f'{x:2d}: X', end=' ')
    else:
        print(f'{x:2d}: .', end=' ')
    if (x + 1) % 10 == 0:
        print()

# Let's try dividing by 4 (14.5px per frame)
# Actually let me look at where the red body column appears in each frame
print("\n\n=== Looking for red body centers ===")
red_centers = []
for frame_start in range(0, w, 1):
    # Count red pixels in a window
    pass

# Better approach: look at the pattern of row 2 which has the wing tip Y characters
# Frame 1: R at col 0-3, Y at col 4-6, R at col 7-9
# Frame 2: R at col 16-19, Y at col 20-22, R at col 23-25
# Frame 3: R at col 30-32, Y at col 33-35, R at col 36-38
# Frame 4: R at col 48-51, Y at col 52-54, R at col 55-57

# Let's find the repeating pattern
print("\n=== Pattern analysis from row 2 ===")
row2 = []
for x in range(w):
    pixel = img.getpixel((x, 2))
    r, g, b, a = pixel
    if a > 0:
        if r > 180 and g > 180 and b < 100:
            row2.append('Y')  # Yellow
        elif r > 180 and g < 100 and b < 100:
            row2.append('R')  # Red
        elif b > 150 and r < 100:
            row2.append('B')  # Blue
        elif r < 50 and g < 50 and b < 50:
            row2.append('D')  # Dark
        else:
            row2.append(f'{r:02x}')
    else:
        row2.append('.')

print(' '.join(row2))

# Find the 4 distinct patterns
# Looking at the data, each frame seems to be about 14-15 pixels wide
# Let's try splitting at regular intervals
frame_widths = [14, 14, 15, 15]  # Total: 58
frame_starts = [0, 14, 28, 43]

print("\n=== Extracted frame patterns (row 2) ===")
for i, start in enumerate(frame_starts):
    end = start + frame_widths[i]
    frame_data = row2[start:end]
    print(f'Frame {i} (cols {start}-{end-1}): {" ".join(frame_data)}')
