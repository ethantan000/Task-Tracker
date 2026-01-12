#!/usr/bin/env python3
"""Generate application icon"""
from PIL import Image, ImageDraw

def create_icon():
    """Create a professional work monitor icon"""
    # Create images at multiple sizes for Windows
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    images = []

    for size in sizes:
        # Create image
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Calculate dimensions
        width, height = size
        center_x, center_y = width // 2, height // 2

        # Background circle (blue gradient effect)
        padding = int(width * 0.05)
        circle_bbox = [padding, padding, width - padding, height - padding]

        # Draw main circle background
        draw.ellipse(circle_bbox, fill='#3498db', outline='#2980b9', width=max(1, int(width * 0.03)))

        # Draw clock face
        clock_size = int(width * 0.6)
        clock_padding = (width - clock_size) // 2
        clock_bbox = [clock_padding, clock_padding,
                      clock_padding + clock_size, clock_padding + clock_size]
        draw.ellipse(clock_bbox, fill='white', outline='#2c3e50', width=max(1, int(width * 0.02)))

        # Draw clock hands
        hand_width = max(1, int(width * 0.015))

        # Hour hand (pointing to 10)
        hour_length = int(clock_size * 0.25)
        hour_end_x = center_x - int(hour_length * 0.5)
        hour_end_y = center_y - int(hour_length * 0.866)
        draw.line([center_x, center_y, hour_end_x, hour_end_y],
                  fill='#2c3e50', width=hand_width * 2)

        # Minute hand (pointing to 2)
        minute_length = int(clock_size * 0.35)
        minute_end_x = center_x + int(minute_length * 0.866)
        minute_end_y = center_y - int(minute_length * 0.5)
        draw.line([center_x, center_y, minute_end_x, minute_end_y],
                  fill='#2c3e50', width=hand_width * 2)

        # Center dot
        dot_size = max(2, int(width * 0.04))
        dot_bbox = [center_x - dot_size, center_y - dot_size,
                    center_x + dot_size, center_y + dot_size]
        draw.ellipse(dot_bbox, fill='#e74c3c')

        # Add checkmark overlay (small, in bottom right)
        check_size = int(width * 0.3)
        check_x = width - check_size - padding
        check_y = height - check_size - padding

        # Checkmark background circle
        check_bg_bbox = [check_x, check_y, check_x + check_size, check_y + check_size]
        draw.ellipse(check_bg_bbox, fill='#2ecc71', outline='#27ae60',
                    width=max(1, int(width * 0.02)))

        # Draw checkmark
        check_thickness = max(1, int(width * 0.025))
        check_center_x = check_x + check_size // 2
        check_center_y = check_y + check_size // 2

        # Checkmark lines
        check_offset = int(check_size * 0.15)
        check_point1 = (check_center_x - check_offset, check_center_y)
        check_point2 = (check_center_x - int(check_offset * 0.3), check_center_y + check_offset)
        check_point3 = (check_center_x + check_offset, check_center_y - check_offset)

        draw.line([check_point1, check_point2], fill='white', width=check_thickness)
        draw.line([check_point2, check_point3], fill='white', width=check_thickness)

        images.append(img)

    # Save as .ico file
    images[0].save('icon.ico', format='ICO', sizes=[(img.width, img.height) for img in images])
    print("Icon created successfully: icon.ico")

if __name__ == '__main__':
    create_icon()
