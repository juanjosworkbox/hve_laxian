from PIL import Image

img = Image.open('samples/player.png')
w, h = img.size
pixels = img.load()

# Classify pixels
grid = []
for y in range(h):
    row = ''
    for x in range(w):
        r, g, b, a = pixels[x, y]
        if r > 200 and g < 20 and b < 20:
            row += 'R'  # Red
        elif r < 20 and g > 150 and b > 150:
            row += 'T'  # Teal
        elif r > 150 and g > 150 and b > 150:
            row += 'G'  # Gray
        else:
            row += 'B'  # Black
    grid.append(row)

print(f"Player sprite: {w}x{h}")
print("Grid (R=red, T=teal, G=gray, B=black):")
for row in grid:
    print(row)

# Count unique color clusters
from collections import Counter
colors = Counter()
for y in range(h):
    for x in range(w):
        r, g, b, a = pixels[x, y]
        # Round to nearest 5 for clustering
        colors[(r//5*5, g//5*5, b//5*5, a)] += 1

print("\nColor clusters (R, G, B, A): count:")
for color, count in sorted(colors.items(), key=lambda x: -x[1]):
    print(f"  {color}: {count}")
