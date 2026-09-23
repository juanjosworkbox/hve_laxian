from PIL import Image
import pygame

# Load original sprite
img = Image.open('samples/player.png')
w, h = img.size
pixels = img.load()

# Create pygame surface from pixels
surface = pygame.Surface((w, h), pygame.SRCALPHA)
for y in range(h):
    for x in range(w):
        r, g, b, a = pixels[x, y]
        surface.set_at((x, y), (r, g, b, a))

# Save as PNG
pygame.image.save(surface, '_player_exact.png')
print(f"Saved exact pixel recreation: {w}x{h}")

# Now create a scaled version for better visibility
scaled = pygame.transform.scale(surface, (w*5, h*5))
pygame.image.save(scaled, '_player_scaled.png')
print(f"Saved scaled version: {w*5}x{h*5}")

# Also save a grid representation for reference
print("\nPixel grid (R=red, T=teal, G=gray, B=black):")
for y in range(h):
    row = ''
    for x in range(w):
        r, g, b, a = pixels[x, y]
        if r > 200 and g < 20 and b < 20:
            row += 'R'
        elif r < 20 and g > 150 and b > 150:
            row += 'T'
        elif r > 150 and g > 150 and b > 150:
            row += 'G'
        else:
            row += 'B'
    print(f"  y={y:2d}: {row}")
