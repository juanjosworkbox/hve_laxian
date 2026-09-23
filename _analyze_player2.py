from PIL import Image
import pygame

img = Image.open('samples/player.png')
w, h = img.size
pixels = img.load()

# Get exact color clusters
from collections import defaultdict
color_map = defaultdict(int)
for y in range(h):
    for x in range(w):
        color_map[pixels[x, y]] += 1

print("Exact color clusters (R, G, B, A): count:")
for color, count in sorted(color_map.items(), key=lambda x: -x[1]):
    print(f"  {color}: {count}")

# Create pygame surface from pixels
pygame.init()
surface = pygame.Surface((w, h), pygame.SRCALPHA)
for y in range(h):
    for x in range(w):
        r, g, b, a = pixels[x, y]
        surface.set_at((x, y), (r, g, b, a))

# Save as test
pygame.image.save(surface, '_player_analysis.png')
print("\nSaved analysis surface to _player_analysis.png")

# Also save a scaled version for comparison
scaled = pygame.transform.scale(surface, (60, 80))
pygame.image.save(scaled, '_player_analysis_scaled.png')
print("Saved scaled version to _player_analysis_scaled.png")
