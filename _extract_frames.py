"""Extract actual pixel data from second_row_enemy_animation.png for all 4 frames."""
from PIL import Image

img = Image.open('samples/second_row_enemy_animation.png')
w, h = img.size
pixels = img.load()

# The sprite sheet is 58x8 with 4 frames
# Let's try dividing into 4 equal regions of ~14-15 pixels each
# Frame boundaries based on analysis:
# Frame 0: cols 0-13 (14px)
# Frame 1: cols 14-28 (15px) 
# Frame 2: cols 29-43 (15px)
# Frame 3: cols 44-57 (14px)

frame_ranges = [(0, 13), (14, 28), (29, 43), (44, 57)]

print("=== Frame-by-frame pixel analysis ===\n")

for frame_idx, (x_start, x_end) in enumerate(frame_ranges):
    print(f"--- Frame {frame_idx} (cols {x_start}-{x_end}) ---")
    # Find content bounds
    y_min = h
    y_max = -1
    for y in range(h):
        for x in range(x_start, x_end + 1):
            if pixels[x, y][3] > 0:
                y_min = min(y_min, y)
                y_max = max(y_max, y)
    
    if y_max == -1:
        print("  No content found")
        continue
    
    print(f"  Content bounds: y={y_min}-{y_max}")
    
    # Print each row with color codes
    for y in range(y_min, y_max + 1):
        row = []
        for x in range(x_start, x_end + 1):
            r, g, b, a = pixels[x, y]
            if a == 0:
                row.append('.')
            elif r > 180 and g < 100 and b < 100:
                row.append('R')  # Red
            elif r > 180 and g > 180 and b < 100:
                row.append('Y')  # Yellow
            elif b > 150 and r < 100:
                row.append('B')  # Blue
            elif r < 50 and g < 50 and b < 50:
                row.append('D')  # Dark
            else:
                row.append(f'{r:02x}')
        print(f"  Row {y:2d}: {''.join(row)}")
    
    # Collect unique colors in this frame
    colors = set()
    for y in range(h):
        for x in range(x_start, x_end + 1):
            r, g, b, a = pixels[x, y]
            if a > 0:
                colors.add((r, g, b))
    print(f"  Unique colors: {colors}")
    print()

# Now let's look at what's DIFFERENT between frames
print("\n=== Frame comparison (key differences) ===")
for y in range(h):
    diffs = []
    for frame_idx, (x_start, x_end) in enumerate(frame_ranges):
        r, g, b, a = pixels[x_start + 7, y]  # Center column of each frame
        diffs.append(f'{r:02x}' if a > 0 else '.')
    if any(d != '.' for d in diffs):
        print(f"  Row {y}: {diffs}")
