"""
Script to create a splash screen image for PyInstaller.
Run this once to generate the splash.png file.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create image with same dimensions as splash screen
width, height = 400, 200
background_color = (43, 43, 43)  # #2b2b2b
text_color = (255, 255, 255)  # white
accent_color = (74, 158, 255)  # #4a9eff

# Create image
img = Image.new('RGB', (width, height), background_color)
draw = ImageDraw.Draw(img)

# Try to use a system font, fallback to default
try:
    # Try to load a nice font
    title_font = ImageFont.truetype("arial.ttf", 36)
    subtitle_font = ImageFont.truetype("arial.ttf", 14)
except:
    # Fallback to default font
    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()

# Draw title "Video Editor"
title_text = "Video Editor"
# Get text bounding box for centering
title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
title_width = title_bbox[2] - title_bbox[0]
title_x = (width - title_width) // 2
title_y = 60

draw.text((title_x, title_y), title_text, fill=text_color, font=title_font)

# Draw "Loading..." text
loading_text = "Loading..."
loading_bbox = draw.textbbox((0, 0), loading_text, font=subtitle_font)
loading_width = loading_bbox[2] - loading_bbox[0]
loading_x = (width - loading_width) // 2
loading_y = 130

draw.text((loading_x, loading_y), loading_text, fill=text_color, font=subtitle_font)

# Draw a simple accent line/bar
bar_width = 200
bar_height = 4
bar_x = (width - bar_width) // 2
bar_y = 115
draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill=accent_color)

# Save the image
output_path = os.path.join(os.path.dirname(__file__), 'splash.png')
img.save(output_path)
print(f"Splash screen image created: {output_path}")
print(f"Image size: {width}x{height} pixels")
