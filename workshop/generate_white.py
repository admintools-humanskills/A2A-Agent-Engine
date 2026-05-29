#!/usr/bin/env python3
"""Generate white-background versions of workshop slides for screenshots."""

import os
import re

WORKSHOP_DIR = os.path.dirname(os.path.abspath(__file__))
WHITE_DIR = os.path.join(WORKSHOP_DIR, "white")
os.makedirs(WHITE_DIR, exist_ok=True)

# Color mappings: dark theme -> white theme
REPLACEMENTS = [
    # Body and slide backgrounds
    ('background: #0f0f1a', 'background: #ffffff'),
    ('background: #1a1a2e', 'background: #ffffff'),
    ('background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #1a1a2e 100%)', 'background: #ffffff'),

    # Primary text colors (light -> dark)
    ('color: #e0e0f0', 'color: #1a1a2e'),
    ('color: #b0b0d0', 'color: #444466'),
    ('color: #c0c0e0', 'color: #333355'),

    # Secondary/muted text
    ('color: #8888aa', 'color: #666688'),
    ('color: #8888bb', 'color: #666688'),
    ('color: #7777aa', 'color: #777799'),
    ('color: #6666aa', 'color: #555588'),
    ('color: #4a4a6a', 'color: #999999'),

    # Nav and slide counter
    ('color: #4a4a6a', 'color: #aaaaaa'),

    # Box shadow (softer on white)
    ('box-shadow: 0 20px 60px rgba(0,0,0,0.5)', 'box-shadow: 0 2px 20px rgba(0,0,0,0.08)'),

    # Borders
    ('border: 1px solid #2a2a4a', 'border: 1px solid #e0e0e8'),
    ('border-color: #7c3aed', 'border-color: #7c3aed'),
    ('stroke="#2a2a4a"', 'stroke="#e0e0e8"'),
    ('stroke="#3a3a5a"', 'stroke="#d0d0dd"'),

    # Slide card backgrounds (index page)
    ('background: #1a1a2e', 'background: #f8f8fc'),

    # Input/misc dark fills
    ('fill="#0a0a1a"', 'fill="#f0f0f5"'),
    ('fill="#0d0d1e"', 'fill="#f5f5fa"'),
    ('fill="#111122"', 'fill="#fafafe"'),
    ('fill="#1a1a2e"', 'fill="#f0f0f5"'),
    ('fill="#1a2a4a"', 'fill="#e8eef8"'),
    ('fill="#2a4a2a"', 'fill="#e8f0e8"'),
    ('fill="#1a3a1a"', 'fill="#d8e8d8"'),

    # SVG text colors (light on dark -> dark on light)
    ('fill="#e0e0f0"', 'fill="#1a1a2e"'),
    ('fill="#b0b0d0"', 'fill="#444466"'),
    ('fill="#c0c0e0"', 'fill="#333355"'),
    ('fill="#8888aa"', 'fill="#666688"'),
    ('fill="#7777aa"', 'fill="#777799"'),
    ('fill="#6666aa"', 'fill="#555588"'),
    ('fill="#4a4a6a"', 'fill="#999999"'),
    ('fill="#888"', 'fill="#888"'),

    # Building colors (keep but adjust slightly for white bg)
    ('fill="#7c6b5a"', 'fill="#8b7a6a"'),
    ('fill="#5a6a7a"', 'fill="#6a7a8a"'),
    ('fill="#8b7355"', 'fill="#a08868"'),
    ('fill="#a08060"', 'fill="#b89878"'),
    ('fill="#4a3a2a"', 'fill="#5a4a3a"'),

    # Separator lines
    ('stroke="#2a2a4a"', 'stroke="#e0e0e8"'),

    # Glow effects - hide on white background
    ('opacity: 0.15', 'opacity: 0'),
    ('filter: blur(120px)', 'filter: blur(120px); display: none'),

    # Dashed lines - darken slightly
    ('stroke="#3a3a5a"', 'stroke="#d0d0dd"'),

    # Title gradients: darken for white background readability
    ('background: linear-gradient(135deg, #c4b5fd, #93c5fd, #fdba74)', 'background: linear-gradient(135deg, #7c3aed, #2563eb, #ea580c)'),
    ('background: linear-gradient(135deg, #c4b5fd, #93c5fd)', 'background: linear-gradient(135deg, #7c3aed, #2563eb)'),
    ('-webkit-text-fill-color: transparent', '-webkit-text-fill-color: transparent'),

    # Badge/tag text colors - keep vibrant
    ('color: #a78bfa', 'color: #7c3aed'),
    ('color: #93c5fd', 'color: #2563eb'),
    ('color: #fdba74', 'color: #ea580c'),
    ('color: #6ee7b7', 'color: #059669'),
    ('color: #fca5a5', 'color: #dc2626'),
    ('color: #d8b4fe', 'color: #7c3aed'),
    ('color: #f9a8d4', 'color: #db2777'),
    ('color: #c4b5fd', 'color: #6d28d9'),

    # SVG text: vibrant colors for white bg
    ('fill="#c4b5fd"', 'fill="#6d28d9"'),
    ('fill="#a78bfa"', 'fill="#7c3aed"'),
    ('fill="#93c5fd"', 'fill="#2563eb"'),
    ('fill="#60a5fa"', 'fill="#2563eb"'),
    ('fill="#fdba74"', 'fill="#ea580c"'),
    ('fill="#fb923c"', 'fill="#ea580c"'),
    ('fill="#6ee7b7"', 'fill="#059669"'),
    ('fill="#34d399"', 'fill="#059669"'),
    ('fill="#fca5a5"', 'fill="#dc2626"'),
    ('fill="#d8b4fe"', 'fill="#7c3aed"'),
    ('fill="#f9a8d4"', 'fill="#db2777"'),
    ('fill="#ffffaa"', 'fill="#ffd700"'),
    ('fill="#ffcc88"', 'fill="#f59e0b"'),
    ('fill="#ff8888"', 'fill="#ef4444"'),
    ('fill="#ffd700"', 'fill="#d97706"'),

    # Slide border for definition on white
    ('border-radius: 16px;', 'border-radius: 16px; border: 1px solid #e5e7eb;'),
]

# SVG-specific opacity boosts for faint fills
SVG_OPACITY_BOOSTS = [
    # Boost faint background fills
    (r'fill="rgba\((\d+),\s*(\d+),\s*(\d+),\s*0\.0[3-8]\)"',
     lambda m: f'fill="rgba({m.group(1)},{m.group(2)},{m.group(3)},0.12)"'),
    (r'fill="rgba\((\d+),\s*(\d+),\s*(\d+),\s*0\.1[0-2]\)"',
     lambda m: f'fill="rgba({m.group(1)},{m.group(2)},{m.group(3)},0.15)"'),
]

files = [f for f in os.listdir(WORKSHOP_DIR) if f.endswith('.html')]

for filename in sorted(files):
    filepath = os.path.join(WORKSHOP_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply direct replacements
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)

    # Apply regex-based SVG opacity boosts
    for pattern, replacement in SVG_OPACITY_BOOSTS:
        content = re.sub(pattern, replacement, content)

    # Write to white directory
    outpath = os.path.join(WHITE_DIR, filename)
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  OK  {filename}")

print(f"\nDone! White versions saved to {WHITE_DIR}/")
