#!/usr/bin/env python3
"""Extract SVG diagrams from workshop slides and convert to PNG with transparent background."""

import html
import re
import os
import cairosvg

WORKSHOP_DIR = os.path.dirname(os.path.abspath(__file__))
PNG_DIR = os.path.join(WORKSHOP_DIR, "png")
os.makedirs(PNG_DIR, exist_ok=True)

# Slide files and their descriptions
slides = [
    ("slide-01-titre.html", "01-titre-network"),
    ("slide-02-probleme.html", "02-probleme-comparison"),
    ("slide-03-protocole-a2a.html", "03-protocole-a2a-schema"),
    ("slide-04-architecture.html", "04-architecture-diagram"),
    ("slide-05-agents.html", "05-agents-grid"),
    ("slide-06-flux-technique.html", "06-flux-sequence-diagram"),
    ("slide-07-pixel-art-ui.html", "07-pixel-art-ui-mockup"),
    ("slide-08-deploiement.html", "08-deploiement-cloud"),
    ("slide-09-enseignements.html", "09-enseignements-matrix"),
]

# SVG wrapper with Inter font and transparent background
SVG_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" {attrs}>
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&amp;display=swap');
      text {{ font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif; }}
    </style>
  </defs>
  {content}
</svg>'''

SCALE = 3  # 3x resolution for crisp PNGs

for filename, output_name in slides:
    filepath = os.path.join(WORKSHOP_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # Find all SVG blocks
    svg_matches = list(re.finditer(r'<svg\b([^>]*)>(.*?)</svg>', html, re.DOTALL))

    if not svg_matches:
        print(f"  SKIP {filename}: no SVG found")
        continue

    for i, match in enumerate(svg_matches):
        attrs = match.group(1)
        content = match.group(2)

        # Extract width/height from attributes
        w_match = re.search(r'width="(\d+)"', attrs)
        h_match = re.search(r'height="(\d+)"', attrs)
        vb_match = re.search(r'viewBox="([^"]+)"', attrs)

        if not w_match or not h_match:
            if vb_match:
                vb_parts = vb_match.group(1).split()
                w, h = int(float(vb_parts[2])), int(float(vb_parts[3]))
            else:
                print(f"  SKIP {filename} SVG#{i}: no dimensions")
                continue
        else:
            w, h = int(w_match.group(1)), int(h_match.group(1))

        # Build clean SVG attrs
        svg_attrs = f'width="{w}" height="{h}"'
        if vb_match:
            svg_attrs += f' viewBox="{vb_match.group(1)}"'
        else:
            svg_attrs += f' viewBox="0 0 {w} {h}"'

        # Replace HTML entities with Unicode equivalents (XML only knows &amp; &lt; &gt; &quot; &apos;)
        html_entities = {
            '&mdash;': '\u2014', '&ndash;': '\u2013', '&bull;': '\u2022',
            '&larr;': '\u2190', '&rarr;': '\u2192', '&uarr;': '\u2191', '&darr;': '\u2193',
            '&laquo;': '\u00AB', '&raquo;': '\u00BB', '&nbsp;': '\u00A0',
            '&times;': '\u00D7', '&euro;': '\u20AC', '&copy;': '\u00A9',
            '&harr;': '\u2194', '&hArr;': '\u21D4',
        }
        for entity, char in html_entities.items():
            content = content.replace(entity, char)
        # Also decode any remaining numeric HTML entities (&#NNNN;)
        content = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), content)
        content = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), content)
        # Escape bare & that aren't already part of XML entities (&amp; &lt; &gt; &quot; &apos;)
        content = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;)', '&amp;', content)

        # Reconstruct full standalone SVG
        full_svg = SVG_TEMPLATE.format(attrs=svg_attrs, content=content)

        # Output filename
        suffix = f"-{i+1}" if len(svg_matches) > 1 else ""
        png_name = f"{output_name}{suffix}.png"
        png_path = os.path.join(PNG_DIR, png_name)

        try:
            cairosvg.svg2png(
                bytestring=full_svg.encode("utf-8"),
                write_to=png_path,
                output_width=w * SCALE,
                output_height=h * SCALE,
                background_color="transparent",
            )
            print(f"  OK  {png_name} ({w*SCALE}x{h*SCALE}px)")
        except Exception as e:
            print(f"  ERR {png_name}: {e}")

print(f"\nDone! PNGs saved to {PNG_DIR}/")
