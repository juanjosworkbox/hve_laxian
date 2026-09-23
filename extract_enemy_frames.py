"""Extract pixel data from second_row_enemy_animation.png and generate pygame surfaces."""
import os

# Use Pillow for initial pixel analysis (no video mode needed)
from PIL import Image

# Initialize pygame without video driver
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
pygame.init()

# Load the PNG using Pillow first for pixel analysis
pil_img = Image.open('samples/second_row_enemy_animation.png')
w, h = pil_img.size
print(f'Image size: {w} x {h}')
print(f'Mode: {pil_img.mode}')

# Convert to pygame after init
img = pygame.image.load('samples/second_row_enemy_animation.png').convert_alpha()

# Analyze pixel data to find frame boundaries
# Look for columns with significant red content
red_threshold = 150
frame_candidates = []

for x in range(w):
    has_red = False
    for y in range(h):
        pixel = img.get_at((x, y))
        r, g, b, a = pixel
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

# Now extract each frame as a pygame surface
print('\n--- Generating Sprite Surfaces ---')

# Create output directory
output_dir = 'generated_sprites'
os.makedirs(output_dir, exist_ok=True)

for i, frame_cols in enumerate(frames):
    x_start = frame_cols[0]
    x_end = frame_cols[-1]
    frame_width = x_end - x_start + 1
    
    # Find actual content bounds (y)
    y_min = h
    y_max = 0
    for y in range(h):
        for x in range(x_start, x_end + 1):
            pixel = img.get_at((x, y))
            if pixel[3] > 0:  # Not transparent
                y_min = min(y_min, y)
                y_max = max(y_max, y)
    
    # Add some padding
    y_min = max(0, y_min - 1)
    y_max = min(h - 1, y_max + 1)
    
    frame_height = y_max - y_min + 1
    
    # Create surface
    surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
    
    # Blit from source
    for dy in range(frame_height):
        for dx in range(frame_width):
            src_x = x_start + dx
            src_y = y_min + dy
            pixel = img.get_at((src_x, src_y))
            surface.set_at((dx, dy), pixel)
    
    # Scale to 10x10 if needed
    if frame_width != 10 or frame_height != 10:
        surface = pygame.transform.scale(surface, (10, 10))
    
    # Save as PNG
    output_path = os.path.join(output_dir, f'red_enemy_frame{i}.png')
    pygame.image.save(surface, output_path)
    print(f'  Saved frame {i} to {output_path} (size: {surface.get_size()})')
    
    # Print pixel data for manual recreation
    print(f'  Pixel data (frame {i}):')
    preview = surface
    for y in range(10):
        row = []
        for x in range(10):
            pixel = preview.get_at((x, y))
            r, g, b, a = pixel
            if a == 0:
                row.append('.')
            elif r > 150 and g < 100 and b < 100:
                row.append('R')  # Red
            elif r > 150 and g > 150 and b < 100:
                row.append('Y')  # Yellow
            elif b > 150 and r < 100:
                row.append('B')  # Blue
            else:
                row.append(f'{r:02x}')
        print(f'    {" ".join(row)}')

print('\n--- Generating Python Code ---')

# Generate Python code to recreate the sprites
code = '''"""Red enemy sprite frames extracted from second_row_enemy_animation.png."""
import pygame

def create_red_enemy_sprite():
    """Create red enemy sprite with 4 animation frames from PNG data.
    
    Each frame shows the enemy with slightly different wing positions,
    creating a flapping animation when cycled.
    """
    frames = []
    
'''

for i, frame_cols in enumerate(frames):
    x_start = frame_cols[0]
    x_end = frame_cols[-1]
    
    # Get pixel data for this frame
    frame_surface = pygame.Surface((x_end - x_start + 1, h), pygame.SRCALPHA)
    for y in range(h):
        for x in range(x_start, x_end + 1):
            pixel = img.get_at((x, y))
            if pixel[3] > 0:
                frame_surface.set_at((x - x_start, y), pixel)
    
    # Find y bounds
    y_min = h
    y_max = 0
    for y in range(h):
        for x in range(x_end - x_start + 1):
            pixel = frame_surface.get_at((x, y))
            if pixel[3] > 0:
                y_min = min(y_min, y)
                y_max = max(y_max, y)
    
    y_min = max(0, y_min - 1)
    y_max = min(h - 1, y_max + 1)
    frame_height = y_max - y_min + 1
    frame_width = x_end - x_start + 1
    
    code += f'    # Frame {i}: columns {x_start}-{x_end}\n'
    code += f'    frame{i}_surface = pygame.Surface(({frame_width}, {frame_height}), pygame.SRCALPHA)\n'
    
    # Add pixel data
    for y in range(y_min, y_max + 1):
        row = []
        for x in range(frame_width):
            src_x = x_start + x
            src_y = y
            pixel = img.get_at((src_x, src_y))
            if pixel[3] > 0:
                r, g, b, a = pixel
                row.append(f'({r}, {g}, {b}, {a})')
            else:
                row.append('(0, 0, 0, 0)')
        code += f'    # Row {y - y_min}: {row}\n'
    
    code += f'    frames.append(frame{i}_surface)\n\n'

code += '''    # Scale all frames to 10x10
    scaled_frames = []
    for frame in frames:
        if frame.get_size() != (10, 10):
            scaled_frames.append(pygame.transform.scale(frame, (10, 10)))
        else:
            scaled_frames.append(frame)
    
    return scaled_frames


if __name__ == "__main__":
    pygame.init()
    frames = create_red_enemy_sprite()
    print(f"Created {len(frames)} frames")
    for i, frame in enumerate(frames):
        print(f"Frame {i}: {frame.get_size()}")
'''

# Save the generated code
code_path = os.path.join(output_dir, 'red_enemy_sprite_code.py')
with open(code_path, 'w') as f:
    f.write(code)
print(f'Generated code saved to {code_path}')

pygame.quit()
