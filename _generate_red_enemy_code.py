"""Generate pygame sprite code from second_row_enemy_animation.png pixel data."""
from PIL import Image

img = Image.open('samples/second_row_enemy_animation.png')
w, h = img.size
pixels = img.load()

# Frame boundaries from analysis
frame_ranges = [(0, 13), (14, 28), (29, 43), (44, 57)]

# For each frame, extract pixels and scale to 10x10 using nearest-neighbor
def nearest_neighbor_scale(frame_pixels, src_w, src_h, dst_w=10, dst_h=10):
    """Scale frame using nearest-neighbor interpolation."""
    scaled = [[None] * dst_w for _ in range(dst_h)]
    
    for dy in range(dst_h):
        for dx in range(dst_w):
            # Map destination to source
            sx = int((dx / (dst_w - 1)) * (src_w - 1))
            sy = int((dy / (dst_h - 1)) * (src_h - 1))
            scaled[dy][dx] = frame_pixels[sy][sx]
    
    return scaled

print('"""Red enemy sprite frames extracted from second_row_enemy_animation.png.')
print('')
print('Each frame is 10x10 pixels matching the original arcade sprite size.')
print('The animation cycles through all 4 frames for smooth wing flapping."""')
print('')
print('import pygame')
print('')
print('')
print('def create_red_enemy_sprite():')
print('    """Create red enemy sprite with 4 animation frames from PNG data.')
print('    ')
print('    Each frame shows the enemy with different wing positions,')
print('    creating a smooth flapping animation when cycled through all 4 frames.')
print('    ')
print('    Colors extracted from samples/second_row_enemy_animation.png')
print('    and scaled to 10x10 to match the original arcade sprite."""')
print('')
print('    frames = []')
print('')

for frame_idx, (x_start, x_end) in enumerate(frame_ranges):
    frame_width = x_end - x_start + 1
    
    # Extract raw frame pixels
    raw = []
    for y in range(h):
        row = []
        for x in range(x_start, x_end + 1):
            r, g, b, a = pixels[x, y]
            row.append((r, g, b, a))
        raw.append(row)
    
    # Scale to 10x10
    scaled = nearest_neighbor_scale(raw, frame_width, h)
    
    # Print pygame code
    print(f'    # Frame {frame_idx}')
    print(f'    frame{frame_idx} = pygame.Surface((10, 10), pygame.SRCALPHA)')
    
    for y in range(10):
        for x in range(10):
            r, g, b, a = scaled[y][x]
            print(f'    frame{frame_idx}.set_at(({x}, {y}), ({r}, {g}, {b}, {a}))')
    
    print(f'    frames.append(frame{frame_idx})')
    print('')

print('    return frames')
