"""Extract pixel data from second_row_enemy_animation.png using Pillow."""
from PIL import Image
import os

# Load the PNG
img = Image.open('samples/second_row_enemy_animation.png')
w, h = img.size
print(f'Image size: {w} x {h}')
print(f'Mode: {img.mode}')

# Analyze pixel data to find frame boundaries
# Look for columns with significant red content
red_threshold = 150
frame_candidates = []

for x in range(w):
    has_red = False
    for y in range(h):
        pixel = img.getpixel((x, y))
        r, g, b, a = pixel[:4]  # Handle RGBA
        if a > 0 and r > red_threshold and g < 100 and b < 100:
            has_red = True
            break
    if has_red:
        frame_candidates.append(x)

print(f'Columns with red content: {frame_candidates}')

# Find contiguous regions (frames)
frames = []
current_frame = []
for x in frame_candidates:
    if not current_frame or x == current_frame[-1] + 1:
        current_frame.append(x)
    else:
        if current_frame:
            frames.append(current_frame)
        current_frame = [x]
if current_frame:
    frames.append(current_frame)

print(f'\nDetected {len(frames)} frames:')
for i, frame in enumerate(frames):
    print(f'  Frame {i}: columns {frame[0]}-{frame[-1]} (width {len(frame)})')

# Now extract each frame's pixel data
print('\n--- Frame Pixel Data ---')

# Create output directory
output_dir = 'generated_sprites'
os.makedirs(output_dir, exist_ok=True)

# Generate Python code for each frame
code = '''"""Red enemy sprite frames extracted from second_row_enemy_animation.png."""
import pygame

def create_red_enemy_sprite():
    """Create red enemy sprite with 4 animation frames from PNG data.
    
    Each frame shows the enemy with slightly different wing positions,
    creating a flapping animation when cycled.
    
    Colors:
    - Red body: (224, 0, 0)
    - Yellow wing tips: (224, 213, 0)
    - Blue wing bases: (0, 86, 206)
    """
    frames = []
    
'''

for i, frame_cols in enumerate(frames):
    x_start = frame_cols[0]
    x_end = frame_cols[-1]
    frame_width = x_end - x_start + 1
    
    # Find actual content bounds (y)
    y_min = h
    y_max = 0
    for y in range(h):
        for x in range(x_start, x_end + 1):
            pixel = img.getpixel((x, y))
            r, g, b, a = pixel[:4]
            if a > 0:
                y_min = min(y_min, y)
                y_max = max(y_max, y)
    
    # Add some padding
    y_min = max(0, y_min - 1)
    y_max = min(h - 1, y_max + 1)
    
    frame_height = y_max - y_min + 1
    
    print(f'\nFrame {i}:')
    print(f'  Position: columns {x_start}-{x_end} (width {frame_width})')
    print(f'  Y bounds: {y_min}-{y_max} (height {frame_height})')
    
    # Print pixel grid
    print('  Pixel grid:')
    for y in range(y_min, y_max + 1):
        row = []
        for x in range(x_start, x_end + 1):
            pixel = img.getpixel((x, y))
            r, g, b, a = pixel[:4]
            if a == 0:
                row.append('.')
            elif r > 150 and g < 100 and b < 100:
                row.append('R')  # Red
            elif r > 150 and g > 150 and b < 100:
                row.append('Y')  # Yellow
            elif b > 150 and r < 100:
                row.append('B')  # Blue
            elif r > 200 and g > 200 and b < 50:
                row.append('Y')  # Yellow
            else:
                row.append(f'{r:02x}')
        print(f'    {" ".join(row)}')
    
    # Generate pygame code for this frame
    code += f'    # Frame {i}: {frame_width}x{frame_height}px\n'
    code += f'    frame{i} = pygame.Surface(({frame_width}, {frame_height}), pygame.SRCALPHA)\n'
    
    for y in range(y_min, y_max + 1):
        for x in range(x_start, x_end + 1):
            pixel = img.getpixel((x, y))
            r, g, b, a = pixel[:4]
            dx = x - x_start
            dy = y - y_min
            code += f'    frame{i}.set_at(({dx}, {dy}), ({r}, {g}, {b}, {a}))\n'
    
    code += f'    frames.append(frame{i})\n\n'

code += '''    # Scale all frames to 10x10
    scaled_frames = []
    for frame in frames:
        if frame.get_size() != (10, 10):
            scaled_frames.append(pygame.transform.scale(frame, (10, 10)))
        else:
            scaled_frames.append(frame)
    
    return scaled_frames


if __name__ == "__main__":
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    import pygame
    pygame.init()
    
    frames = create_red_enemy_sprite()
    print(f"\\nCreated {len(frames)} frames")
    for i, frame in enumerate(frames):
        print(f"Frame {i}: {frame.get_size()}")
'''

# Save the generated code
code_path = os.path.join(output_dir, 'red_enemy_sprite_code.py')
with open(code_path, 'w') as f:
    f.write(code)
print(f'\n\nGenerated code saved to {code_path}')

# Also save individual frame PNGs for visual inspection
for i, frame_cols in enumerate(frames):
    x_start = frame_cols[0]
    x_end = frame_cols[-1]
    frame_width = x_end - x_start + 1
    
    # Find y bounds
    y_min = h
    y_max = 0
    for y in range(h):
        for x in range(x_start, x_end + 1):
            pixel = img.getpixel((x, y))
            r, g, b, a = pixel[:4]
            if a > 0:
                y_min = min(y_min, y)
                y_max = max(y_max, y)
    
    y_min = max(0, y_min - 1)
    y_max = min(h - 1, y_max + 1)
    frame_height = y_max - y_min + 1
    
    # Crop frame
    frame_img = img.crop((x_start, y_min, x_end + 1, y_max + 1))
    output_path = os.path.join(output_dir, f'red_enemy_frame{i}.png')
    frame_img.save(output_path)
    print(f'Saved frame {i} to {output_path} ({frame_img.size})')
