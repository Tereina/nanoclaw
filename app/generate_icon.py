#!/usr/bin/env python3
"""Generate macOS app icon for MyAssistant Orchestrator."""

from PIL import Image, ImageDraw, ImageFilter
import math
import subprocess
import os

SIZE = 512
CORNER_RADIUS = 100

def rounded_rect_mask(size, radius):
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size[0]-1, size[1]-1], radius=radius, fill=255)
    return mask

def draw_icon():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Dark gradient background
    for y in range(SIZE):
        t = y / SIZE
        r = int(25 + t * 15)
        g = int(30 + t * 15)
        b = int(40 + t * 20)
        draw.line([(0, y), (SIZE, y)], fill=(r, g, b, 255))

    # Subtle radial highlight in center-top area
    glow_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    cx, cy = SIZE // 2, SIZE // 3
    for radius in range(180, 0, -1):
        alpha = int(15 * (1 - radius / 180))
        glow_draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                          fill=(0, 200, 255, alpha))
    img = Image.alpha_composite(img, glow_layer)

    # Draw the claw - 3 prongs gripping downward
    claw_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    claw_draw = ImageDraw.Draw(claw_layer)

    # Claw parameters
    base_y = 140
    tip_y = 390
    prong_width = 18

    # Color: cyan/electric blue
    claw_color = (0, 220, 255, 255)
    claw_color_dark = (0, 150, 220, 255)

    # Three prong paths: left, center, right
    prongs = [
        # Left prong - curves outward left then hooks inward
        {
            "start": (200, base_y),
            "control1": (130, 220),
            "control2": (140, 320),
            "tip": (185, tip_y),
            "hook": (210, tip_y + 15),
        },
        # Center prong - straight down with slight taper
        {
            "start": (256, base_y - 10),
            "control1": (256, 220),
            "control2": (256, 320),
            "tip": (256, tip_y + 20),
            "hook": (256, tip_y + 35),
        },
        # Right prong - mirror of left
        {
            "start": (312, base_y),
            "control1": (382, 220),
            "control2": (372, 320),
            "tip": (327, tip_y),
            "hook": (302, tip_y + 15),
        },
    ]

    def bezier(t, p0, p1, p2, p3):
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        return (x, y)

    # Draw glow behind claws
    glow2 = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    glow2_draw = ImageDraw.Draw(glow2)

    for prong in prongs:
        points = []
        for i in range(101):
            t = i / 100
            pt = bezier(t, prong["start"], prong["control1"], prong["control2"], prong["tip"])
            points.append(pt)
        # Extend to hook
        points.append(prong["hook"])

        # Draw thick glow line
        for i in range(len(points) - 1):
            glow2_draw.line([points[i], points[i+1]], fill=(0, 180, 255, 40), width=prong_width + 20)

    glow2 = glow2.filter(ImageFilter.GaussianBlur(radius=12))
    img = Image.alpha_composite(img, glow2)

    # Draw claw prongs
    claw_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    claw_draw = ImageDraw.Draw(claw_layer)

    for prong in prongs:
        points = []
        for i in range(101):
            t = i / 100
            pt = bezier(t, prong["start"], prong["control1"], prong["control2"], prong["tip"])
            points.append(pt)
        points.append(prong["hook"])

        # Draw main prong line with taper
        for i in range(len(points) - 1):
            t = i / len(points)
            w = int(prong_width * (1 - t * 0.5))  # taper toward tip
            # Gradient from bright to slightly darker
            r = int(0 + t * 0)
            g = int(220 - t * 60)
            b = int(255 - t * 30)
            claw_draw.line([points[i], points[i+1]], fill=(r, g, b, 255), width=max(w, 4))

        # Draw bright tip/hook highlight
        tip = prong["hook"]
        claw_draw.ellipse([tip[0]-6, tip[1]-6, tip[0]+6, tip[1]+6], fill=(150, 255, 255, 255))

    # Draw the connecting bar at top of claw (the "palm")
    palm_y = base_y - 5
    # Rounded bar connecting the three prong tops
    claw_draw.rounded_rectangle(
        [175, palm_y - 25, 337, palm_y + 15],
        radius=12,
        fill=(0, 180, 230, 255),
        outline=(0, 220, 255, 255),
        width=2
    )

    # Small "joint" circles at prong bases
    for prong in prongs:
        sx, sy = prong["start"]
        claw_draw.ellipse([sx-8, sy-8, sx+8, sy+8], fill=(0, 200, 245, 255))

    # Add circuit-like details on the palm bar
    for x_off in [-30, 0, 30]:
        cx = 256 + x_off
        cy = palm_y - 5
        claw_draw.ellipse([cx-3, cy-3, cx+3, cy+3], fill=(150, 255, 255, 255))

    # Top connector / "arm" stub
    claw_draw.rounded_rectangle(
        [236, palm_y - 55, 276, palm_y - 20],
        radius=8,
        fill=(0, 160, 210, 255),
        outline=(0, 220, 255, 200),
        width=2
    )
    # Small indicator light
    claw_draw.ellipse([251, palm_y - 50, 261, palm_y - 40], fill=(100, 255, 255, 255))

    img = Image.alpha_composite(img, claw_layer)

    # Inner glow on prongs
    inner_glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ig_draw = ImageDraw.Draw(inner_glow)
    for prong in prongs:
        points = []
        for i in range(101):
            t = i / 100
            pt = bezier(t, prong["start"], prong["control1"], prong["control2"], prong["tip"])
            points.append(pt)
        for i in range(len(points) - 1):
            ig_draw.line([points[i], points[i+1]], fill=(180, 255, 255, 30), width=6)
    inner_glow = inner_glow.filter(ImageFilter.GaussianBlur(radius=4))
    img = Image.alpha_composite(img, inner_glow)

    # Apply rounded corners mask
    mask = rounded_rect_mask((SIZE, SIZE), CORNER_RADIUS)
    result = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    result.paste(img, (0, 0), mask)

    return result


def main():
    out_dir = "/Users/Tereina/NanoClaw/nanoclaw/menubar"
    icon = draw_icon()

    # Save 512x512 PNG
    png_path = os.path.join(out_dir, "icon.png")
    icon.save(png_path, "PNG")
    print(f"Saved {png_path}")

    # Create iconset for .icns
    iconset_dir = os.path.join(out_dir, "AppIcon.iconset")
    os.makedirs(iconset_dir, exist_ok=True)

    # Required sizes: 16, 32, 128, 256, 512 (and @2x variants)
    sizes = [
        ("icon_16x16.png", 16),
        ("icon_16x16@2x.png", 32),
        ("icon_32x32.png", 32),
        ("icon_32x32@2x.png", 64),
        ("icon_128x128.png", 128),
        ("icon_128x128@2x.png", 256),
        ("icon_256x256.png", 256),
        ("icon_256x256@2x.png", 512),
        ("icon_512x512.png", 512),
        ("icon_512x512@2x.png", 1024),
    ]

    # Generate 1024 version for @2x of 512
    icon_1024 = draw_icon()  # redraw is fine, or resize up
    # For 1024, just upscale the 512
    icon_1024 = icon.resize((1024, 1024), Image.LANCZOS)

    for name, size in sizes:
        if size <= 512:
            resized = icon.resize((size, size), Image.LANCZOS)
        else:
            resized = icon_1024.resize((size, size), Image.LANCZOS)
        resized.save(os.path.join(iconset_dir, name), "PNG")

    print(f"Created iconset at {iconset_dir}")

    # Convert to .icns
    icns_path = os.path.join(out_dir, "AppIcon.icns")
    subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", icns_path], check=True)
    print(f"Saved {icns_path}")

    # Clean up iconset
    import shutil
    shutil.rmtree(iconset_dir)
    print("Cleaned up iconset directory")


if __name__ == "__main__":
    main()
