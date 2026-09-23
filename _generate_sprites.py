"""Extract and scale PNG frames to 10x10, then generate Python code."""
from PIL import Image

img = Image.open('samples/second_row_enemy_animation.png')
w, h = img.size
pixels = img.load()

# Frame boundaries from analysis
frame_ranges = [(0, 13), (14, 28), (29, 43), (44, 57)]

# Extract each frame, scale to 10x10, and print pixel data
print('"""Red enemy sprite frames extracted from second_row_enemy_animation.png."""\n')
print('import pygame\n\n')
print('def create_red_enemy_sprite():\n')
print('    """Create red enemy sprite with 4 animation frames from PNG data.')
print('    ')
print('    Each frame shows the enemy with different wing positions,')
print('    creating a smooth flapping animation when cycled through all 4 frames.')
print('    ')
print('    Sizes are scaled to 10x10 to match the original arcade sprite."""\n')
print('    frames = []\n')

for frame_idx, (x_start, x_end) in enumerate(frame_ranges):
    frame_width = x_end - x_start + 1
    
    # Extract frame pixels
    frame_pixels = []
    for y in range(h):
        row = []
        for x in range(x_start, x_end + 1):
            r, g, b, a = pixels[x, y]
            row.append((r, g, b, a))
        frame_pixels.append(row)
    
    # Scale to 10x10 using bilinear interpolation
    scaled = []
    for ty in range(10):
        row = []
        for tx in range(10):
            # Map back to source coordinates
            sx = (tx / 9.0) * (frame_width - 1)
            sy = (ty / 9.0) * (h - 1)
            
            # Get surrounding pixels for bilinear interpolation
            x0 = int(sx)
            y0 = int(sy)
            x1 = min(x0 + 1, frame_width - 1)
            y1 = min(y0 + 1, h - 1)
            
            dx = sx - x0
            dy = sy - y0
            
            p00 = frame_pixels[y0][x0]
            p01 = frame_pixels[y0][x1]
            p10 = frame_pixels[y1][x0]
            p11 = frame_pixels[y1][x1]
            
            # Interpolate each channel
            def lerp(c0, c1, t):
                return int(c0 + (c1 - c0) * t)
            
            r = lerp(p00[0], p01[0], dx)
            g = lerp(p00[1], p01[1], dx)
            b = lerp(p00[2], p01[2], dx)
            a = lerp(p00[3], p01[3], dx)
            
            r = lerp(r, lerp(p10[0], p11[0], dx), dy)
            g = lerp(g, lerp(p10[1], p11[1], dx), dy)
            b = lerp(b, lerp(p10[2], p11[2], dx), dy)
            a = lerp(a, lerp(p10[3], p11[3], dx), dy)
            
            row.append((r, g, b, max(a, 1)))  # Ensure not fully transparent
        scaled.append(row)
    
    # Print the scaled frame pixel data
    print(f'    # Frame {frame_idx}')
    print(f'    frame{frame_idx} = pygame.Surface((10, 10), pygame.SRCALPHA)')
    for y in range(10):
        for x in range(10):
            r, g, b, a = scaled[y][x]
            print(f'    frame{frame_idx}.set_at(({x}, {y}), ({r}, {g}, {b}, {a}))')
    print(f'    frames.append(frame{frame_idx})\n')

print('    return frames')
