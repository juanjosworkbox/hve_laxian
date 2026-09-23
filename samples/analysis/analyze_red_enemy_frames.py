"""Analyze second_row_enemy_animation.png frame by frame."""
from PIL import Image

img = Image.open('samples/second_row_enemy_animation.png')
w, h = img.size
print(f'Image: {w}x{h}')
print(f'Frame width: 10px')
frames = w // 10
print(f'Number of frames: {frames}')

pixels = img.load()

for i in range(frames):
    print(f'\n=== Frame {i} (cols {i*10}-{i*10+9}) ===')
    for y in range(h):
        row = []
        for x in range(i*10, i*10+10):
            px = pixels[x, y]
            r, g, b, a = px
            if a == 0:
                row.append('..')
            elif r > 150 and g < 50 and b < 50:
                row.append('R ')  # Red
            elif r < 50 and g > 150 and b < 50:
                row.append('G ')  # Green
            elif r < 50 and g < 50 and b > 150:
                row.append('B ')  # Blue
            elif r > 150 and g > 150 and b < 50:
                row.append('Y ')  # Yellow
            else:
                row.append(f'({r:02x})')
        print(f'  Row {y:2d}: ' + ' '.join(row))
